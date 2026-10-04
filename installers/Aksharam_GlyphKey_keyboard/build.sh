#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
./generate_keyboard.py
mkdir -p build tests
rm -f build/aksharam_glyphkey.kmx build/aksharam_glyphkey.kmp
kmc build aksharam_glyphkey.kmn -o build/aksharam_glyphkey.kmx | tee tests/kmc_keyboard.log
kmc build aksharam_glyphkey.kps -o build/aksharam_glyphkey.kmp | tee tests/kmc_package.log
python3 tests/run_tests.py
printf 'Built: build/aksharam_glyphkey.kmp\n'
