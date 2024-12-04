-- To use nvim as a pager in git, add the following to ~/.gitconfig:
-- [color]
--   pager = no
-- [core]
--   pager = /path/to/nvim -l /path/to/misc/nvim_git_pager.lua -R

vim.opt.confirm = false
vim.opt.wrap = false
vim.opt.cursorline = false
vim.opt.number = false

local map = vim.api.nvim_set_keymap
local opt = { noremap = true, silent = true }

-- Mappings for normal mode
map('n', 'j', 'gj', opt)
map('n', 'k', 'gk', opt)
map('n', 'q', '<Cmd>q<CR>', opt)
map('n', '<Space>', '<C-f>', opt)
