@echo off
echo Verificando a existência do ambiente virtual...
if not exist "%~dp0ambientevirtual\Scripts\activate.bat" (
    echo Ambiente virtual não encontrado. Certifique-se de que está criado no diretório correto.
    pause
    exit /b 1
)

echo Ativando o ambiente virtual...
call "%~dp0ambientevirtual\Scripts\activate.bat"

if "%errorlevel%" neq "0" (
    echo Erro ao ativar o ambiente virtual.
    pause
    exit /b %errorlevel%
)

echo Iniciando o StormBot...
python "%~dp0src\main.py"

if "%errorlevel%" neq "0" (
    echo Erro ao iniciar o StormBot.
    pause
    exit /b %errorlevel%
)

echo O StormBot está rodando. Você pode ja pode rodar os comandos no discord.
pause