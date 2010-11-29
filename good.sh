#!/bin/bash

GOOD_MESSAGE=""
if [ $# -gt 0 ] ; then
    GOOD_MESSAGE="($@)"
fi

echo 'SUCCESS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!' "$GOOD_MESSAGE"
