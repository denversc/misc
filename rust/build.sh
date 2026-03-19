#!/bin/bash

set -v

exec cargo build --release --bins
