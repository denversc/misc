# Git Commit Message Specification

When creating git commit messages in this repository, the following format MUST be strictly adhered to:

1. **Title Line:** The first line of the commit message must begin with the name of the file that has changes, followed by a colon (`:`), followed by a single sentence that describes the changes. There is no line length restriction on this first line.
   * Example: `zshrc.zsh: implement dynamic resizing for the gradient status badge.`

2. **Detailed Description (Optional):** If there are more relevant details that cannot be captured in the single sentence title, add a blank line followed by a paragraph describing the changes.
3. **Wrapping:** The detailed description paragraph MUST wrap at exactly 100 characters.

## Example
```text
zshrc.zsh: implement responsive fallback logic for the gradient status badge to support narrow terminals.

The badge now calculates a maximum length to guarantee exactly 5 characters of padding on both the left and right sides. If the horizontal space is insufficient, the script will gracefully drop the date, then drop the time, then truncate the command string, and finally drop the command string entirely to ensure the line does not wrap unexpectedly.
```
