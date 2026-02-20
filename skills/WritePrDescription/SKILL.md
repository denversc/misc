---
name: dconeybe-write-pr-description
description: Writes a description for a GitHub PR and sets it.
---

# Write a PR description

## When to use this skill

Use this skill when asked to write and set the description for a GitHub pull request ("PR").

## How to set the description for a PR

Use GitHub's "gh" command to set the PR description.
To avoid problems with special characters, write the PR description to a temporary file,
then specify that file to the "gh" command.

For example, to set the description for PR 1234 using the test from file description.md, run this command:

```
gh pr edit 1234 --body-file description.md
```

## Example templates for PR descriptions

Use the following examples of good PR descriptions to write the PR description:
* assets/PR7714.json
* assets/PR7716.json
* assets/PR7720.json
* assets/PR7759.json

The examples come from PRs 7714, 7716, 7720, and 7759 in https://github.com/firebase/firebase-android-sdk, respectively.
The contents of PRNNNN.json was retrieved by running this command:

```
gh pr --repo firebase/firebase-android-sdk view NNNN --json title,body
```
