---
name: dconeybe-write-pr-description
description: Writes a description for a GitHub PR and sets it.
---

# Write a PR description

## When to use this skill

Use this skill when asked to write and set the description for a GitHub pull request ("PR").

## Prerequisites

*   The GitHub CLI (`gh`) must be installed and authenticated.

## Instructions

1. Learn about the PR for which you will write a description.
    * Use `gh pr diff <PR_NUMBER>` to understand the code changes.
    * Consider any other relevant aspects of the PR for writing the description, such as its title and commit messages.
    * If the PR already has a description then ignore it, as it may be incorrect or outdated.
2. Write a description for the PR, using the template and examples below, to a temporary file (e.g., `PrDescription.md`).
3. Set the description for the PR.
    * Use Github's "gh" command: `gh pr edit <PR Number> --body-file <PR description file>`
4. Delete the temporary file containing the PR description.

## Error Handling

If any command fails or you are unable to write to the temporary file then abort and report the error to the user.

## PR Description Structure

PR descriptions are written using Github-flavored markdown. The content for each section should be derived from the PR's title, commit messages, and diff.

### Summary

The PR description must begin with a 1-2 sentence summary of the change. Synthesize the PR title and the overarching theme of the commit messages to create this summary.

### Highlights

After the summary, add a "Highlights" section with a bulleted list. Each bullet point should summarize a notable change. Identify the most significant changes from the diff, such as new features, major refactors, or user-facing fixes. Group related changes into a single bullet point.

### Changelog

Finally, add a "Changelog" section that lists the individual files affected by the PR.
This section must be enclosed in a `<details>` block.
For each file in the diff, create a bullet point summarizing what was added, changed, or removed.
**DO NOT USE THE FULL PATH OF THE FILE** in the bullet point because it is noisy and more difficult for humans to absorb.
Instead, just use the **FILE NAME** without the path.
The only exception would be if two files in the "Changelog" section have the same name, then use the shortest path possible to disambiguate.

## Example PR descriptions

Use the following examples of good PR descriptions as a reference for style and structure. The content of the description you write must be derived entirely from the pull request you are working on.
* [PR7714.md](assets/PR7714.md)
* [PR7720.md](assets/PR7720.md)
* [PR7759.md](assets/PR7759.md)

The examples come from PRs 7714, 7720, and 7759 in https://github.com/firebase/firebase-android-sdk, respectively.
