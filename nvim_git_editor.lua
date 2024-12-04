-- To use nvim as an editor in git, add the following to ~/.gitconfig:
-- [core]
--   editor = /path/to/nvim -l /path/to/misc/nvim_git_editor.lua -R

vim.opt.confirm = false
vim.opt.wrap = false
vim.opt.cursorline = false
vim.opt.number = false

local function git_commit_message_init()
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

git_commit_message_init()
