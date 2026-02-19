@echo off
title Bet Booster V2 - Sistema Avançado de Análise de Apostas
color 0A
echo.
echo  ┌─────────────────────────────────────────┐
echo  │        🎯 BET BOOSTER V2               │
echo  │   Sistema Avançado de Análise          │
echo  │        de Apostas Esportivas           │
echo  └─────────────────────────────────────────┘
echo.
echo ⚡ Iniciando BET BOOSTER V2...
echo.

cd /d "%~dp0"

if exist "bet_booster_v2.py" (
    echo ✅ Arquivo encontrado, executando...
    echo.
    python bet_booster_v2.py
    if errorlevel 1 (
        echo.
        echo ❌ Erro ao executar o programa!
        echo 💡 Soluções:
        echo    1. Certifique-se que o Python está instalado
        echo    2. Execute: pip install requests
        echo    3. Verifique se todos os arquivos estão presentes
        echo.
        pause
    )
) else (
    echo ❌ Erro: Arquivo bet_booster_v2.py não encontrado!
    echo.
    echo 📁 Verifique se o arquivo está na pasta correta
    echo 🔧 Execute novamente o instalador se necessário
    echo.
    pause
)
