#!/usr/bin/env python3
"""
Script para executar a versão web do MonitorRabbitMQ
100% compatível com qualquer sistema operacional
Versão Web Completa - Substitui completamente o tkinter
"""

import os
import sys

# Adiciona o diretório atual ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from web_app import MonitorRabbitMQWebApp
    from version import VERSION
    
    if __name__ == "__main__":
        print(f"🌐 Iniciando MonitorRabbitMQ Web {VERSION}...")
        print("🚀 Sistema 100% web - Sem tkinter")
        print("📱 Interface moderna e responsiva")
        
        app = MonitorRabbitMQWebApp()
        app.executar(debug=False, porta=8083)
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("📦 Instale as dependências:")
    print("   pip install flask flask-socketio eventlet")
    print("   pip install selenium webdriver-manager")
    input("Pressione Enter para sair...")
except Exception as e:
    print(f"❌ Erro: {e}")
    input("Pressione Enter para sair...")
