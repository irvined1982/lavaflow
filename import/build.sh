#!/bin/bash

CWD=$(pwd)

mkdir -p build

cd build

echo "[Build Log] BEGIN" > build.log

cmake $CWD 2>&1 | tee -a build.log

make       2>&1 | tee -a build.log
