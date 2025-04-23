-- Load the local "pre" configuration file, if it exists
local local_pre_init_path = vim.fs.joinpath(vim.fn.stdpath("config"), "init.local.pre.lua")
if vim.fn.filereadable(local_pre_init_path) == 1 then
  dofile(local_pre_init_path)
end

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
vim.opt.softtabstop = 0
vim.opt.shiftwidth = 2
vim.opt.expandtab = true
vim.opt.smarttab = true

-- Highlight the entire line on which the cursor is located.
vim.opt.cursorline = true

-- Don't wrap long lines.
vim.opt.wrap = false

-- Show line numbers in the right column.
vim.opt.number = true

-- Set some GUI options for Neovide.
if vim.g.neovide then
  vim.opt.guifont = 'JetBrainsMonoNL Nerd Font:h16'

  if vim.fn.has('mac') == 1 then
    -- Allow clipboard copy paste in neovim
    -- https://github.com/neovide/neovide/issues/1263#issuecomment-1100895622
    vim.g.neovide_input_use_logo = 1
    vim.api.nvim_set_keymap('', '<D-v>', '+p<CR>', { noremap = true, silent = true})
    vim.api.nvim_set_keymap('!', '<D-v>', '<C-R>+', { noremap = true, silent = true})
    vim.api.nvim_set_keymap('t', '<D-v>', '<C-R>+', { noremap = true, silent = true})
    vim.api.nvim_set_keymap('v', '<D-v>', '<C-R>+', { noremap = true, silent = true})
  end

  -- Whether the mouse will be hidden upon starting to type.
  -- Moving the mouse makes it visible again.
  -- https://neovide.dev/configuration.html#hiding-the-mouse-when-typing
  vim.g.neovide_hide_mouse_when_typing = true

  -- Determines whether the window size from the previous session will be used on startup.
  -- https://neovide.dev/configuration.html#remember-previous-window-size
  vim.g.neovide_remember_window_size = true

  -- The time it takes for the cursor to complete it's animation, in seconds. Set to 0 to disable.
  -- https://neovide.dev/configuration.html#animation-length
  vim.g.neovide_cursor_animation_length = 0

  -- How long the scroll animation takes to complete, measured in seconds. Set to 0 to disable.
  -- https://neovide.dev/configuration.html#scroll-animation-length
  vim.g.neovide_scroll_animation_length = 0
end

require("config.lazy")

require('lualine').setup {
  theme = 'powerline',
}

local lspconfig = require('lspconfig')
lspconfig.clangd.setup {
  capabilities = require('cmp_nvim_lsp').default_capabilities(),
}

local cmp = require('cmp')
local luasnip = require('luasnip')

cmp.setup({
  snippet = {
    expand = function(args)
      luasnip.lsp_expand(args.body)
    end,
  },
  mapping = cmp.mapping.preset.insert({
    ['<C-b>'] = cmp.mapping.scroll_docs(-4),
    ['<C-f>'] = cmp.mapping.scroll_docs(4),
    ['<C-Space>'] = cmp.mapping.complete(),
    ['<C-e>'] = cmp.mapping.abort(),
    ['<CR>'] = cmp.mapping.confirm({ select = true }),
  }),
  sources = cmp.config.sources({
    { name = 'nvim_lsp' },
    { name = 'luasnip' },
    { name = 'buffer' },
    { name = 'path' },
  }),
})

luasnip.config.setup({})

-- Load the local "post" configuration file, if it exists
local local_post_init_path = vim.fs.joinpath(vim.fn.stdpath("config"), "init.local.post.lua")
if vim.fn.filereadable(local_post_init_path) == 1 then
  dofile(local_post_init_path)
end
