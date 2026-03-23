# Elvish Shell Development Context

This file contains key learnings and guidelines for developing Elvish shell scripts in this workspace.

## Functions and Arguments

Elvish does not support defining optional positional arguments with default values directly in the function signature (e.g., `fn f {|a='default'| ...}` is not valid for positional arguments). 

### Optional Positional Arguments

To implement optional positional arguments, use a variadic argument (`@args`) and manually assign the default value if the list is empty:

```elvish
fn myfunc {|@args|
    var myarg = "default_value"
    if (> (count $args) 0) {
        set myarg = $args[0]
    }
    # ... use $myarg ...
}
```

### Argument Validation and Errors

To restrict the number of arguments and throw an error if too many are provided, check the count and use the `fail` command. You can include the unexpected argument in the error message:

```elvish
fn myfunc {|@args|
    if (> (count $args) 1) {
        fail "myfunc: too many arguments; unexpected argument: "$args[1]
    }
    # ...
}
```

## String Concatenation

When concatenating a variable with a literal string of alphanumeric characters, where the literal part could be misinterpreted as part of the variable name (e.g., `$varname` followed by `X`), you must quote the literal string and place the variable immediately adjacent to it outside the quotes.

**Correct:**
```elvish
var prefix = "tmp"
echo $prefix"XXXXXXXXXX" # Output: tmpXXXXXXXXXX
```

**Incorrect:**
```elvish
echo $prefixXXXXXXXXXX  # Looks for a variable named 'prefixXXXXXXXXXX'
echo $prefix^XXXXXXXXXX # The '^' operator does not work this way for this purpose
```
