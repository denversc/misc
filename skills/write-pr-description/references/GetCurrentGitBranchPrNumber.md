# Get the PR number of the current Git branch.

Here are instructions for two ways to get the GitHub Pull Request ("PR") number of the current Git branch.

## GitHub MCP Server (preferred)

### Step 1: Determine remote branch

To determine the remote branch to which the current branch will be pushed, run this command:

git rev-parse --abbrev-ref --symbolic-full-name '@{u}'

The output will look something like this:

```
origin/foo/bar/baz
```

In this example the remote branch name is "foo/bar/baz".

### Step 2: Determine PR number from remote branch

Use the GitHub MCP server to determine the PR number for the remote branch determined in the previous step.

## GitHub CLI (`gh` command)

To get the GitHub Pull Request ("PR") number of the current Git branch, run this command:

gh pr view --json number

This command will output a simple JSON structure like this:

```
{
  "number": 12345
}
```

In this example the PR number of the current Git branch is "12345".

If the command completes with a non-zero exit code
or with a message like "no pull requests found"
then this is an error and you MUST report
the error that you were unable to determine the PR number.
