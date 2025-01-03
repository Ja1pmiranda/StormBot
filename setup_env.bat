@echo off
echo Verificando a existência do ambiente virtual...
if not exist "%~dp0ambientevirtual\Scripts\activate.bat" (
    echo Ambiente virtual não encontrado. Criando um novo ambiente virtual...
    python -m venv "%~dp0ambientevirtual"
)

echo Ativando o ambiente virtual...
call "%~dp0ambientevirtual\Scripts\activate.bat"
if "%errorlevel%" neq "0" (
    echo Erro ao ativar o ambiente virtual.
    pause
    exit /b %errorlevel%
)

echo Verificando a existência do arquivo requirements.txt...
if not exist "%~dp0requirements.txt" (
    echo Arquivo requirements.txt não encontrado. Certifique-se de que está no diretório correto.
    pause
    exit /b 1
)

echo Instalando dependências...
pip install --upgrade pip
pip install -r "%~dp0requirements.txt"
if "%errorlevel%" neq "0" (
    echo Erro ao instalar as dependências.
    pause
    exit /b %errorlevel%
)

echo Dependências instaladas com sucesso.
echo Ambiente virtual configurado. Você pode agora fechar esta janela e executar o projeto clicando duas vezes em 'start_chatbot.bat'.
pause