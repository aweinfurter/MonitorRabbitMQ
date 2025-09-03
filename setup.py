#!/usr/bin/env python3
"""
Setup script para MonitorRabbitMQ
Configura ambiente e dependências automaticamente
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Executa um comando e exibe o progresso"""
    print(f"🔄 {description}...")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=True, capture_output=True, text=True)
        print(f"✅ {description} - Concluído!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False

def check_python_version():
    """Verifica se a versão do Python é adequada"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão atual: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK!")
    return True

def main():
    """Setup principal"""
    print("🚀 MonitorRabbitMQ - Setup Automático")
    print("=" * 50)
    
    # Verifica versão do Python
    if not check_python_version():
        input("Pressione Enter para sair...")
        return
    
    # Verifica se está no diretório correto
    if not os.path.exists("src/run_web.py"):
        print("❌ Execute este script na pasta raiz do projeto!")
        input("Pressione Enter para sair...")
        return
    
    # Cria ambiente virtual se não existir
    if not os.path.exists("venv"):
        print("📦 Criando ambiente virtual...")
        if not run_command(f"{sys.executable} -m venv venv", "Criação do ambiente virtual"):
            input("Pressione Enter para sair...")
            return
    else:
        print("✅ Ambiente virtual já existe!")
    
    # Determina comando pip/python baseado no SO
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip.exe"
        python_cmd = "venv\\Scripts\\python.exe"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Atualiza pip (corrigido: usar python -m pip)
    run_command(f"{python_cmd} -m pip install --upgrade pip", "Atualização do pip")
    
    # Instala dependências
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Instalação das dependências"):
        print("⚠️ Tentando instalação manual das dependências principais...")
        deps = [
            "Flask>=2.0.0",
            "selenium>=4.0.0", 
            "webdriver-manager>=3.8.0",
            "Pillow>=9.0.0",
            "requests>=2.25.0"
        ]
        for dep in deps:
            run_command(f"{pip_cmd} install {dep}", f"Instalação de {dep}")
    
    print("\n" + "=" * 50)
    print("🎉 Setup concluído!")
    print("\n📋 Próximos passos:")
    print("1. Execute o sistema:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\python.exe src\\run_web.py")
    else:
        print("   venv/bin/python src/run_web.py")
    print("\n2. Configure o sistema:")
    print("   - Acesse http://localhost:8083")
    print("   - Configure suas credenciais SSO")
    print("   - Selecione as filas para monitorar")
    print("\n3. Inicie o monitoramento!")
    print("\n🔗 Para mais informações, consulte o README.md")
    print("=" * 50)
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
