@echo off

REM ================================================================================================
REM ==
REM == rdbg.bat
REM == By: Denver Coneybeare
REM == August 23, 2007
REM ==
REM == This simple BAT file asynchronously deletes a directory and all of its subdirectories and
REM == their files recursively.  It is merely a convenience script so that a directory can be
REM == quickly deleted in the background while the user continues on with their task.  While the
REM == delete is in progress a command window will appear in the taskbar and will disappear once the
REM == operation has completed.
REM ==
REM == To maximize the usefulness of this script, add the directory that contains it to the PATH
REM == environment variable so that at a command prompt you can simply type "rdbg <directory>".
REM ==
REM ================================================================================================

if "%1" == "dowork" goto dowork

start "Deleting %1" /min /low cmd /c %0 dowork %1
goto done




:dowork

echo The current directory is:
cd

echo.
echo Deleting %2
echo.

rd /s /q "%2"
if %ERRORLEVEL% == 0 goto done
pause

:done
