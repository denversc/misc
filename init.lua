-- Configuration file for Neovim: https://neovim.io
-- On Linux/macOS, you can copy it to ~/.config/nvim/init.lua

-- Disable cursor keys, forcing usage of the more ergonomic h, j, k, and l keys.
vim.keymap.set('n', '<up>', '<nop>', {noremap=true, desc='Use k instead of the up button'})
vim.keymap.set('n', '<down>', '<nop>', {noremap=true, desc='Use j instead of the down button'})
vim.keymap.set('n', '<left>', '<nop>', {noremap=true, desc='Use l instead of the left button'})
vim.keymap.set('n', '<right>', '<nop>', {noremap=true, desc='Use h instead of the right button'})

-- Enable typing "jk" to exit insert mode.
vim.keymap.set('i', 'jk', '<esc>', {noremap=true})

-- Enable typing "jk" to exit "typing" mode in the terminal started via :terminal.
vim.keymap.set('t', 'jk', '<C-\\><C-n>', {noremap=true})

-- Set tab to 2 spaces.
vim.opt.tabstop = 2
vim.opt.softtabstop = 2
vim.opt.shiftwidth = 2
vim.opt.expandtab = true

-- Highlight the entire line on which the cursor is located.
vim.opt.cursorline = true

-- Don't wrap long lines.
vim.opt.wrap = false

-- Show line numbers in the right column.
vim.opt.number = true
