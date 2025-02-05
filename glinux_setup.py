import logging
import pathlib
import shutil
import subprocess
import tempfile
import urllib.request

def main() -> None:
    logging.info("Installing homebrew")
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = pathlib.Path(temp_dir_name)
        homebrew_install_script_url = "https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh"
        homebrew_install_script_path = temp_dir / "homebrew_install.sh"
        logging.info("Downloading %s to %s", homebrew_install_script_url, homebrew_install_script_path)
        with urllib.request.urlopen(homebrew_install_script_url) as request, homebrew_install_script_path.open("wb") as out_file:
            logging.info("Got HTTP response %s %s", request.status, request.reason)
            byte_download_count = 0
            while chunk := request.read(1024):
                byte_download_count += len(chunk)
                out_file.write(chunk)
            logging.info("Downloaded %s bytes", str.format("{:,}", byte_download_count))
        args = ["/bin/bash", str(homebrew_install_script_path)]
        logging.info("Running command: %s", subprocess.list2cmdline(args))
        #subprocess.check_call(args)

        add_zshrc_lines(
                "# Disable homebrew analytics, to make google happy",
                "# See https://docs.brew.sh/Analytics#opting-out",
                "export HOMEBREW_NO_ANALYTICS=1",
        )


def add_zshrc_lines(*lines) -> None:
    zshrc_file = pathlib.Path.home() / ".zshrc"
    logging.info("Adding %s lines to %s: %s",
        len(lines),
        zshrc_file,
        ", ".join(f"\"{line.strip()}\"" for line in lines),
    )

    with zshrc_file.open("w+", encoding="utf8", errors="strict", newline="\n") as f:
        f_text = f.read()
        if "\n".join(lines) in f_text:
            logging.info("Lines are already present; not re-adding them")
            return

        for line in lines:
            if line.strip() in f_text:
                raise GlinuxSetupError(f"Line already in file {zshrc_file}: {line.strip()}")

        for line in lines:
            f.write("\n")
            f.write(line)
        f.write("\n")
            

class GlinuxSetupError(Exception):
    pass

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        level=logging.INFO,
    )
    main()





"""
- Run these commands in your terminal to add Homebrew to your PATH:
    echo >> /usr/local/google/home/dconeybe/.zshrc
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /usr/local/google/home/dconeybe/.zshrc
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
- Install Homebrew's dependencies if you have sudo access:
    sudo apt-get install build-essential
  For more information, see:
    https://docs.brew.sh/Homebrew-on-Linux
- We recommend that you install GCC:
    brew install gcc
- Run brew help to get started
- Further documentation:
    https://docs.brew.sh
"""

