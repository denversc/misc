-- Produced by Gemini when prompted with:
-- "how would i implement a keymap in nvim that is similar to the "less" command?"

local map = vim.api.nvim_set_keymap
local opt = { noremap = true, silent = true }

-- Mappings for normal mode
map('n', 'j', 'gj', opt)
map('n', 'k', 'gk', opt)
map('n', 'q', '<Cmd>q<CR>', opt)
map('n', '<Space>', '<C-f>', opt)
