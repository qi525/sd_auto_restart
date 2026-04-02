@echo off

set PYTHON=C:\Users\SNOW\AppData\Local\Programs\Python\Python312\python.exe
set GIT=C:\Program Files\Git\bin\git.exe
set VENV_DIR=C:\stable-diffusion-webui-reForge\venv
set COMMANDLINE_ARGS=--use-ipex --theme dark --port 7861 --opt-sdp-attention --api --autolaunch --listen --skip-python-version-check

@REM Uncomment following code to reference an existing A1111 checkout.
@REM set A1111_HOME=Your A1111 checkout dir
@REM
@REM set VENV_DIR=%A1111_HOME%\\venv
@REM set COMMANDLINE_ARGS=%COMMANDLINE_ARGS% ^
@REM  --ckpt-dir %A1111_HOME%\\models\\Stable-diffusion ^
@REM  --hypernetwork-dir %A1111_HOME%\\models\\hypernetworks ^
@REM  --embeddings-dir %A1111_HOME%\\embeddings ^
@REM  --lora-dir %A1111_HOME%\\models\\Lora

call webui.bat
