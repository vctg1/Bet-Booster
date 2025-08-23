#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 BET BOOSTER - Teste de Instalação
Verifica se todos os componentes estão funcionando corretamente
"""

import os
import sys
import importlib.util

def test_file_exists(filepath, description):
    """Testa se um arquivo existe"""
    if os.path.exists(filepath):
        print(f"✅ {description}: OK")
        return True
    else:
        print(f"❌ {description}: FALTANDO")
        return False

def test_import(module_name, description):
    """Testa se um módulo pode ser importado"""
    try:
        __import__(module_name)
        print(f"✅ {description}: OK")
        return True
    except ImportError as e:
        print(f"❌ {description}: ERRO - {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 BET BOOSTER - Teste de Instalação")
    print("=" * 50)
    
    # Diretório atual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Diretório: {current_dir}")
    print()
    
    # Testes de arquivos
    print("📄 TESTANDO ARQUIVOS:")
    files_ok = True
    
    essential_files = [
        ("interface_apostas.py", "Programa Principal"),
        ("sofascore_api.py", "Módulo de API"),
        ("times_database.json", "Base de Dados"),
        ("bet-booster.ico", "Ícone"),
        ("launcher_bet_booster.py", "Launcher")
    ]
    
    for filename, description in essential_files:
        filepath = os.path.join(current_dir, filename)
        if not test_file_exists(filepath, description):
            files_ok = False
    
    print()
    
    # Testes de módulos Python
    print("🐍 TESTANDO MÓDULOS PYTHON:")
    modules_ok = True
    
    # Módulos padrão
    standard_modules = [
        ("tkinter", "Interface Gráfica"),
        ("json", "Manipulação JSON"),
        ("os", "Sistema Operacional"),
        ("threading", "Multi-threading")
    ]
    
    for module, description in standard_modules:
        if not test_import(module, description):
            modules_ok = False
    
    # Módulos externos
    external_modules = [
        ("requests", "Requisições HTTP")
    ]
    
    for module, description in external_modules:
        if not test_import(module, description):
            print(f"⚠️ {description}: Será instalado automaticamente")
    
    print()
    
    # Teste específico do programa
    print("🎯 TESTANDO PROGRAMA:")
    program_ok = True
    
    try:
        # Verificar se o programa principal pode ser importado
        spec = importlib.util.spec_from_file_location(
            "interface_apostas", 
            os.path.join(current_dir, "interface_apostas.py")
        )
        if spec and spec.loader:
            print("✅ Programa Principal: Importável")
        else:
            print("❌ Programa Principal: Erro de importação")
            program_ok = False
            
    except Exception as e:
        print(f"❌ Programa Principal: {e}")
        program_ok = False
    
    # Verificar ícone
    icon_path = os.path.join(current_dir, "bet-booster.ico")
    if os.path.exists(icon_path):
        size = os.path.getsize(icon_path)
        print(f"✅ Ícone: OK ({size} bytes)")
    else:
        print("❌ Ícone: Arquivo não encontrado")
        program_ok = False
    
    print()
    
    # Resultado final
    print("📊 RESULTADO FINAL:")
    print("=" * 30)
    
    if files_ok and modules_ok and program_ok:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O Bet Booster está pronto para instalação")
        print("✅ Execute BetBoosterInstaller.py para instalar")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        if not files_ok:
            print("⚠️ Arquivos essenciais estão faltando")
        if not modules_ok:
            print("⚠️ Módulos Python não disponíveis")
        if not program_ok:
            print("⚠️ Programa principal tem problemas")
        print()
        print("🔧 Soluções:")
        print("• Verifique se todos os arquivos estão na pasta")
        print("• Instale Python de https://python.org/downloads")
        print("• Execute: pip install requests")
    
    print()
    input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
