@echo off
setlocal
set "IDF_TOOLS_PATH=D:\esp-tool"
set "IDF_PYTHON_ENV_PATH=D:\esp-tool\python_env\idf6.0_py3.13_env"
set "PATH=%IDF_PYTHON_ENV_PATH%\Scripts;%PATH%"
call "D:\esp-idf\v6.0.2\esp-idf\export.bat"
if errorlevel 1 exit /b %errorlevel%
pushd "%~dp0"
python "%IDF_PATH%\tools\idf.py" %*
set "IDF_LOCAL_RESULT=%errorlevel%"
popd
exit /b %IDF_LOCAL_RESULT%
