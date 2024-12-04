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
function insert_filenames_from_git_comment_comments()
  local saved_cursor = vim.api.nvim_win_get_cursor(0)
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
    local insert_line = saved_cursor[1] - 1
    vim.api.nvim_buf_set_lines(0, insert_line, insert_line, false, filenames)
    vim.api.nvim_win_set_cursor(0, saved_cursor)
  end
end

-- When called, runs "git diff --cached" and appends the output to
-- the current buffer.
function git_diff_cached_append()
  local handle = io.popen("git diff --cached")
  while true do
    local line = handle:read("*l")
    if not line then
      break
    end
    vim.api.nvim_buf_set_lines(0, -1, -1, false, {line})
  end
  handle:close()
end

-- Set up custom key mappings that are convenient when editing git commit messages.
do
  local buf_id = vim.api.nvim_get_current_buf()
  local map = vim.api.nvim_buf_set_keymap
  local map_options = { noremap = true, silent = true }
  map(buf_id, 'n', '<Leader>d', '<Cmd>lua git_diff_cached_append()<CR>', map_options)
  map(buf_id, 'n', '<Leader>f', '<Cmd>lua insert_filenames_from_git_comment_comments()<CR>', map_options)
end
