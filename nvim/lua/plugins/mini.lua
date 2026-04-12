-- https://github.com/nvim-mini/mini.nvim

return {
  'nvim-mini/mini.nvim',
  version = '*',
  config = function()
    require('mini.surround').setup() -- https://github.com/nvim-mini/mini.nvim/blob/main/doc/mini-surround.txt
    require('mini.statusline').setup()
    require('mini.tabline').setup()
    vim.opt.showtabline = 1 -- Only show if there are at least two tabs
  end
}
