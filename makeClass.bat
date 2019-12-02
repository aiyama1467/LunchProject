@echo off
if "%~1"=="" (
  echo ERROR: Too few arguments.
  echo USAGE: ./makeClass [package or application name]
  exit /b 1
)

mkdir docs
pyreverse -o png %1
move *.png docs
