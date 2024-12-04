-- To use nvim as an editor in git, add the following to ~/.gitconfig:
-- [core]
--   editor = /path/to/nvim -S /path/to/misc/nvim_git_editor.lua

vim.opt_local.confirm = false
vim.opt_local.wrap = false
vim.opt_local.cursorline = false
vim.opt_local.number = false

-- Extract the filenames from the default git commit template's message and
-- put them, one per line, at the top of the file. This makes it easy to include
-- filenames in the git commit message, which is often desirable.
do
  local pattern = "^#.-:%s*(.-)%s*$"
  local lines = vim.api.nvim_buf_get_lines(0, 0, -1, false)
  local filenames = {}

  for _, line in ipairs(lines) do
    local _, _, filename = string.find(line, pattern)
    if filename and #filename > 0 then
      table.insert(filenames, filename)
    end
  end

  if #filenames then
    vim.api.nvim_buf_set_lines(0, 0, 0, false, filenames)
    vim.api.nvim_win_set_cursor(0, {1, 0})
  end
end
