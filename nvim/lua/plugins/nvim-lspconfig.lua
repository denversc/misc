-- https://github.com/neovim/nvim-lspconfig

return {
  {
    'neovim/nvim-lspconfig',
    dependencies = {
      -- Mason automatically installs LSPs to stdpath for neovim
      'williamboman/mason.nvim',
      'williamboman/mason-lspconfig.nvim',
    },
    config = function()
      require('mason').setup()
      require('mason-lspconfig').setup({
        -- See full list at https://github.com/neovim/nvim-lspconfig/blob/master/doc/configs.md
        ensure_installed = {
          'bashls',
          'graphql',
          'kotlin_lsp',
          'pyright',
          'rust_analyzer',
          'ts_ls',
        },
      })
    end,
  },
}
