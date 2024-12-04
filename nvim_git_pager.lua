-- To use nvim as a pager in git, add the following to ~/.gitconfig:
-- [color]
--   pager = no
-- [core]
--   pager = /path/to/nvim -R -S /path/to/misc/nvim_git_pager.lua

vim.opt_local.wrap = false
vim.opt_local.cursorline = false
vim.opt_local.number = false
vim.opt_local.buftype = 'nofile'

-- Map some keys to behave like "less", such as "space" is "page down"
-- and "q" simply quits.
do
  local buf_id = vim.api.nvim_get_current_buf()
  local map = vim.api.nvim_buf_set_keymap
  local map_options = { noremap = true, silent = true }

  -- Mappings for normal mode
  map(buf_id, 'n', 'q', '<Cmd>q!<CR>', map_options)
  map(buf_id, 'n', '<Space>', '<C-f>', map_options)
end
