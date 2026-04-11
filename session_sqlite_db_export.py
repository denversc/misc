import sqlite3
import os
import datetime
import re
import argparse
import json
import shutil
import ctypes
import html

try:
    from fpdf import FPDF
    from PIL import Image
    HAS_PDF_LIBS = True
except ImportError:
    HAS_PDF_LIBS = False

class SessionDecryptor:
    def __init__(self, key_hex):
        self.key = bytes.fromhex(key_hex)
        self.sodium = None
        for path in ['/opt/homebrew/lib/libsodium.dylib', 'libsodium.dylib', '/usr/local/lib/libsodium.dylib']:
            try:
                self.sodium = ctypes.cdll.LoadLibrary(path)
                break
            except Exception:
                continue
                
        if self.sodium:
            self.HEADERBYTES = self.sodium.crypto_secretstream_xchacha20poly1305_headerbytes()
            self.STATEBYTES = self.sodium.crypto_secretstream_xchacha20poly1305_statebytes()
            self.ABYTES = self.sodium.crypto_secretstream_xchacha20poly1305_abytes()

    def decrypt(self, input_path, output_path):
        if not self.sodium:
            return False

        try:
            with open(input_path, 'rb') as f:
                header = f.read(self.HEADERBYTES)
                if len(header) < self.HEADERBYTES:
                    return False
                ciphertext = f.read()

            state = ctypes.create_string_buffer(self.STATEBYTES)
            res = self.sodium.crypto_secretstream_xchacha20poly1305_init_pull(state, header, self.key)
            if res != 0:
                return False

            clen = len(ciphertext)
            mlen = clen - self.ABYTES
            if mlen < 0: return False
            
            message = ctypes.create_string_buffer(mlen)
            mlen_p = ctypes.c_ulonglong()
            tag_p = ctypes.c_ubyte()
            
            res = self.sodium.crypto_secretstream_xchacha20poly1305_pull(
                state, message, ctypes.byref(mlen_p), ctypes.byref(tag_p),
                ciphertext, ctypes.c_ulonglong(clen), None, ctypes.c_ulonglong(0)
            )
            
            if res != 0:
                return False
                
            with open(output_path, 'wb') as f:
                f.write(message.raw[:mlen_p.value])
                
            return True
        except Exception as e:
            print(f"Error decrypting {input_path}: {e}")
            return False

class ChatPDF(FPDF if HAS_PDF_LIBS else object):
    def header(self):
        if hasattr(self, 'conv_name'):
            from fpdf.enums import XPos, YPos
            self.set_font('helvetica', 'B', 12)
            # cell() supports new_x/new_y
            self.cell(0, 10, f'Conversation: {self.conv_name}', 
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def export_session_db(db_path, export_dir, attachments_root=None):
    os.makedirs(export_dir, exist_ok=True)
    attachments_export_dir = os.path.join(export_dir, "attachments")
    os.makedirs(attachments_export_dir, exist_ok=True)

    if not HAS_PDF_LIBS:
        print("Warning: fpdf2 or Pillow not found. PDF files will not be generated.")
        print("To enable PDF export, run: pip install fpdf2 Pillow")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get the attachment decryption key
    cursor.execute("SELECT json FROM items WHERE id = 'local_attachment_encrypted_key'")
    row = cursor.fetchone()
    decryptor = None
    if row:
        try:
            key_data = json.loads(row['json'])
            key_hex = key_data.get('value')
            if key_hex:
                decryptor = SessionDecryptor(key_hex)
                if decryptor.sodium:
                    print(f"Decryption key found. Attachments will be decrypted.")
                else:
                    print("Warning: libsodium not found. Attachments will be exported but remain encrypted.")
        except Exception as e:
            print(f"Error loading decryption key: {e}")

    # Try to find attachments directory
    if not attachments_root:
        db_dir = os.path.dirname(os.path.abspath(db_path))
        potential_paths = [
            os.path.join(db_dir, "attachments.noindex"),
            os.path.expanduser("~/Library/Application Support/Session/attachments.noindex")
        ]
        for p in potential_paths:
            if os.path.exists(p):
                attachments_root = p
                break

    if attachments_root:
        print(f"Using attachments source: {attachments_root}")
    else:
        print("Warning: Attachments directory not found.")

    try:
        cursor.execute("SELECT id, nickname, displayNameInProfile FROM conversations")
        contacts = {row['id']: (row['displayNameInProfile'] or row['nickname'] or row['id']) for row in cursor.fetchall()}

        cursor.execute("SELECT id, type, nickname, displayNameInProfile FROM conversations")
        conversations = cursor.fetchall()

        exported_count = 0
        for conv in conversations:
            conv_id = conv['id']
            conv_name = conv['displayNameInProfile'] or conv['nickname'] or conv_id
            safe_name = re.sub(r'[/\\?%*:|"<>]', '_', conv_name)
            
            cursor.execute('''
                SELECT sent, source, body, sort_timestamp_full, type, json, hasAttachments
                FROM messages 
                WHERE conversationId = ?
                ORDER BY sort_timestamp_full ASC
            ''', (conv_id,))
            messages = cursor.fetchall()
            if not messages: continue
                
            exported_count += 1
            print(f"Exporting: {conv_name} ({len(messages)} messages)...")
            
            # Text Export
            txt_file_path = os.path.join(export_dir, f"{safe_name}_{conv_id[:8]}.txt")
            with open(txt_file_path, 'w', encoding='utf-8') as f:
                f.write(f"Conversation: {conv_name}\nID: {conv_id}\nType: {conv['type']}\n")
                f.write("="*40 + "\n\n")

            # HTML Export
            html_file_path = os.path.join(export_dir, f"{safe_name}_{conv_id[:8]}.html")
            with open(html_file_path, 'w', encoding='utf-8') as f_html:
                f_html.write(f'<!DOCTYPE html>\n<html>\n<head>\n<meta charset="utf-8">\n<title>Conversation: {html.escape(conv_name)}</title>\n')
                f_html.write("<style>\nbody { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f0f2f5; }\n")
                f_html.write(".message { margin-bottom: 12px; padding: 10px; border-radius: 8px; background-color: #ffffff; border: 1px solid #ddd; }\n")
                f_html.write(".sender { font-weight: bold; color: #1c1e21; }\n")
                f_html.write(".timestamp { color: #65676b; font-size: 0.85em; margin-left: 10px; }\n")
                f_html.write(".body { margin-top: 6px; white-space: pre-wrap; color: #050505; }\n")
                f_html.write(".attachment { margin-top: 10px; }\n")
                f_html.write(".attachment img { max-width: 100%; height: auto; max-height: 400px; border-radius: 4px; display: block; }\n")
                f_html.write(".attachment a { display: inline-block; padding: 6px 12px; background-color: #007bff; color: white; text-decoration: none; border-radius: 4px; font-size: 0.9em; }\n")
                f_html.write("</style>\n</head>\n<body>\n")
                f_html.write(f'<h1>Conversation: {html.escape(conv_name)}</h1>\n')
                f_html.write(f"<p><strong>ID:</strong> {html.escape(conv_id)}<br><strong>Type:</strong> {html.escape(conv['type'])}</p>\n<hr>\n")

            # PDF Export
            pdf = None
            if HAS_PDF_LIBS:
                pdf = ChatPDF()
                pdf.conv_name = conv_name
                pdf.add_page()
                pdf.set_font("helvetica", size=10)

            for msg in messages:
                body = msg['body'] or ""
                ts = msg['sort_timestamp_full']
                if ts:
                    try:
                        dt_obj = datetime.datetime.fromtimestamp(ts / 1000.0)
                        dt = dt_obj.strftime('%Y-%m-%d %H:%M:%S')
                        file_ts = dt_obj.strftime('%Y%m%d_%H%M%S')
                    except Exception:
                        dt = str(ts); file_ts = str(ts)
                else:
                    dt = "Unknown Time"; file_ts = "unknown"
                    
                sender = "Me" if msg['sent'] else contacts.get(msg['source'], msg['source'])

                attachment_refs = []
                local_attachment_paths = []
                html_attachments = []
                if msg['hasAttachments'] and msg['json']:
                    try:
                        attachments = json.loads(msg['json']).get('attachments', [])
                        for idx, att in enumerate(attachments):
                            att_path = att.get('path')
                            att_name = att.get('fileName') or ""
                            content_type = att.get('contentType')
                            if attachments_root and att_path:
                                source_file = os.path.join(attachments_root, att_path)
                                if os.path.exists(source_file):
                                    ext = os.path.splitext(att_name)[1].lower()
                                    if not ext and content_type:
                                        mime_map = {
                                            'image/jpeg': '.jpg', 'image/jpg': '.jpg',
                                            'image/png': '.png', 'image/gif': '.gif',
                                            'image/webp': '.webp', 'video/mp4': '.mp4',
                                            'audio/ogg': '.ogg', 'audio/mpeg': '.mp3',
                                            'application/pdf': '.pdf'
                                        }
                                        ext = mime_map.get(content_type, '')
                                    
                                    export_filename = f"{file_ts}_{conv_id[:4]}_{idx}{ext}"
                                    dest_file = os.path.join(attachments_export_dir, export_filename)
                                    
                                    success = False
                                    if decryptor:
                                        success = decryptor.decrypt(source_file, dest_file)
                                    
                                    if not success:
                                        shutil.copy2(source_file, dest_file)
                                        attachment_refs.append(f"[Attachment (Encrypted): attachments/{export_filename}]")
                                        html_attachments.append(f'<div class="attachment"><em>Encrypted Attachment: <a href="attachments/{html.escape(export_filename)}">{html.escape(att_name or export_filename)}</a></em></div>')
                                    else:
                                        attachment_refs.append(f"[Attachment: attachments/{export_filename}]")
                                        # Track for HTML/PDF
                                        rel_path = f"attachments/{export_filename}"
                                        if content_type and content_type.startswith('image/'):
                                            local_attachment_paths.append(dest_file)
                                            html_attachments.append(f'<div class="attachment"><img src="{html.escape(rel_path)}" alt="{html.escape(att_name)}"></div>')
                                        else:
                                            html_attachments.append(f'<div class="attachment"><a href="{html.escape(rel_path)}">Download: {html.escape(att_name or export_filename)}</a></div>')
                                else:
                                    attachment_refs.append(f"[Attachment Missing: {att_name or 'unnamed'}]")
                                    html_attachments.append(f'<div class="attachment"><em>[Attachment Missing: {html.escape(att_name or "unnamed")}]</em></div>')
                    except Exception: pass

                if not body and not attachment_refs:
                    body = f"[{msg['type']}]" if msg['type'] and msg['type'] != 'message' else "[No Content]"
                
                # Write to text file
                with open(txt_file_path, 'a', encoding='utf-8') as f:
                    f.write(f"[{dt}] {sender}: {body}")
                    if attachment_refs:
                        if body: f.write(" ")
                        f.write(" ".join(attachment_refs))
                    f.write("\n")

                # Write to HTML file
                with open(html_file_path, 'a', encoding='utf-8') as f_html:
                    f_html.write('<div class="message">\n')
                    f_html.write(f'  <div><span class="sender">{html.escape(sender)}</span><span class="timestamp">[{dt}]</span></div>\n')
                    if body:
                        f_html.write(f'  <div class="body">{html.escape(body)}</div>\n')
                    for html_att in html_attachments:
                        f_html.write(f'  {html_att}\n')
                    f_html.write('</div>\n')

                # Write to PDF
                if pdf:
                    # Core fonts only support latin-1. Sanitize text for PDF.
                    pdf_text = f"[{dt}] {sender}: {body}"
                    pdf_text = pdf_text.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 5, pdf_text)
                    pdf.ln(2) # Move to next line after text
                    for img_path in local_attachment_paths:
                        # Check if image is valid and get dimensions
                        with Image.open(img_path) as img:
                            width, height = img.size
                            aspect = height / width
                            
                            # Scale to at most 1/3 of printable page width or height, whichever is smaller
                            max_dim = min(pdf.epw / 3, pdf.eph / 3)
                            
                            if width > height:
                                display_width = max_dim
                                display_height = display_width * aspect
                            else:
                                display_height = max_dim
                                display_width = display_height / aspect
                            
                            # Check if we need a new page for the image
                            if pdf.get_y() + display_height > (pdf.h - 20):
                                pdf.add_page()
                            
                            # image() does NOT support new_x/new_y. 
                            # It automatically moves Y to the bottom of the image if y is not provided.
                            # We just need to ensure X is reset to margin for the next line.
                            pdf.image(img_path, w=display_width, h=display_height)
                            pdf.set_x(pdf.l_margin)
                            pdf.ln(2) # Small spacer after image
                    pdf.ln(2)

            if pdf:
                pdf_file_path = os.path.join(export_dir, f"{safe_name}_{conv_id[:8]}.pdf")
                pdf.output(pdf_file_path)

            # Close HTML
            with open(html_file_path, 'a', encoding='utf-8') as f_html:
                f_html.write("</body>\n</html>\n")

        print(f"Successfully exported {exported_count} conversations to {export_dir}")
    finally:
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Export Session Messenger SQLite database to text/pdf files.")
    parser.add_argument("db_path", help="Path to the Session SQLite database file")
    parser.add_argument("-o", "--output", default="session_exports", help="Output directory")
    parser.add_argument("-a", "--attachments", help="Path to attachments directory")
    args = parser.parse_args()
    export_session_db(args.db_path, args.output, args.attachments)
