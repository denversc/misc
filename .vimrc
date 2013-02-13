set nocompatible
syntax on

set tabstop=4
set softtabstop=4
set shiftwidth=4
set expandtab
set smarttab
set autoindent
set nobackup

set hlsearch
set incsearch
set magic
set showmatch

set ruler
set autowrite
set undolevels=1000
set history=100
set cpoptions=aABceFs

set icon
set backspace=indent,eol,start
set indentexpr=
set nowrap

set mousefocus
set mousehide

" Disable cursor keys, to force usage of hjkl
noremap <up> <nop>
noremap <down> <nop>
noremap <left> <nop>
noremap <right> <nop>

" Make pressing "j" followed by "k" in rapid succession in insert mode
" equivalent to escape; saves reaching all the way up to the real escape
inoremap jk <ESC>

au BufNewFile,BufRead *.avs set syntax=avs

" Source: http://vim.wikia.com/wiki/Pretty-formatting_XML
function! DoPrettyXML()
  " save the filetype so we can restore it later
  let l:origft = &ft
  set ft=
  " delete the xml header if it exists. This will
  " permit us to surround the document with fake tags
  " without creating invalid xml.
  1s/<?xml .*?>//e
  " insert fake tags around the entire document.
  " This will permit us to pretty-format excerpts of
  " XML that may contain multiple top-level elements.
  0put ='<PrettyXML>'
  $put ='</PrettyXML>'
  silent %!xmllint --format -
  " xmllint will insert an <?xml?> header. it's easy enough to delete
  " if you don't want it.
  " delete the fake tags
  2d
  $d
  " restore the 'normal' indentation, which is one extra level
  " too deep due to the extra tags we wrapped around the document.
  silent %<
  " back to home
  1
  " restore the filetype
  exe "set ft=" . l:origft
endfunction
command! XmlPretty call DoPrettyXML()
