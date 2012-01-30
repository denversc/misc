#!/bin/bash

eval `dircolors -b`
alias ls='ls --color=auto'

export INTPURC="$HOME/.inputrc"

export CFLAGS="-O3 -march=native"
export CXXFLAGS="-O3 -march=native"
