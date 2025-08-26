@echo off
echo.
echo ===================================================
echo          BET BOOSTER V2 - INICIALIZANDO
echo ===================================================
echo.

REM Verificar se estamos no diretório correto
if not exist "src\bet_booster_v2.py" (
    echo ERRO: Execute este arquivo do diretorio raiz do projeto
    echo Diretorio atual: %CD%
    pause
    exit /b 1
)

echo [1/4] Verificando ambiente Python...
if not exist ".venv\Scripts\python.exe" (
    echo ERRO: Ambiente virtual nao encontrado
    echo Execute o instalador primeiro: instalador_bet_booster.py
    pause
    exit /b 1
)

echo [2/4] Verificando dependencias...
.venv\Scripts\python.exe -c "import tkinter, requests, json" >nul 2>&1
if errorlevel 1 (
    echo ERRO: Dependencias nao encontradas
    echo Instalando dependencias necessarias...
    .venv\Scripts\pip.exe install requests
)

echo [3/4] Verificando integridade do sistema...
if exist "src\teste_completo_v2.py" (
    echo Executando testes rapidos...
    .venv\Scripts\python.exe src\teste_completo_v2.py --quick >nul 2>&1
)

echo [4/4] Iniciando BET BOOSTER V2...
echo.
echo ===================================================
echo          SISTEMA CARREGADO COM SUCESSO!
echo ===================================================
echo.
echo NOVAS FUNCIONALIDADES V2:
echo - Apostas Hot: Recomendacoes automaticas
echo - Jogos do Dia: Integracao completa
echo - Multiplas: Gestao avancada
echo - Status Ao Vivo: Controle em tempo real
echo - Value Betting: Identificacao automatica
echo.
echo Pressione qualquer tecla para continuar...
pause >nul

REM Executar o sistema
.venv\Scripts\python.exe src\bet_booster_v2.py

REM Se chegou aqui, o programa foi fechado
echo.
echo Sistema encerrado. Pressione qualquer tecla para sair...
pause >nul
