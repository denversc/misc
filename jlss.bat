@echo off

REM This script invokes javaloader screenshot and then converts the
REM screenshot to a PNG image with the given name, or screenshot.png if
REM no name is given

set SCREENSHOT_FILENAME=%1
shift
if (%SCREENSHOT_FILENAME)==() goto screenshot_filename_ok
set SCREENSHOT_FILENAME=screenshot.png
:screenshot_filename_ok

@echo on
javaloader screenshot out.bmp
@if errorlevel 1 goto fail
cygconvert out.bmp "%SCREENSHOT_FILENAME%"
@if errorlevel 1 goto fail
del out.bmp
@goto done

:fail
del out.bmp
exit /b 1

:done
