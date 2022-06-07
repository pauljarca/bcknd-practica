@echo off

IF NOT EXIST venv (
    echo python system interpreter:
    where python
    python --version || goto :error
    echo creating new virtualenv...
    python -m venv venv || goto :error
)

echo activating venv
call deactivate >NUL 2>NUL
call .\venv\Scripts\activate
echo python version:
python -VV
echo pip version:
pip --version

if "%1" == "--no-pip" goto :nopip
echo installing requirements...
python -m pip install -U pip || goto :error
pip install -U --find-links=wheels -r requirements.txt || goto :error

:error
echo Failed with error #%errorlevel%.
exit /b %errorlevel%

