#!/usr/bin/env python3
"""
Teste do Sistema de Alertas - MonitorRabbitMQ
Verifica se os popups estão funcionando corretamente
"""

import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    try:
        from modules.ui import popup, confirmar_modo_invisivel
        
        print("🧪 Teste do Sistema de Alertas - MonitorRabbitMQ")
        print("=" * 60)
        
        print("📋 Testando função confirmar_modo_invisivel()...")
        resultado = confirmar_modo_invisivel()
        print(f"✅ Resultado: {resultado}")
        
        print("\n🚨 Testando popup de alerta crítico...")
        print("👀 Um popup deve aparecer na sua tela agora!")
        
        mensagem_teste = """TESTE DE ALERTA: 2 fila(s) com mensagens!

===================================

🔴 wms-teste-errors: 5 mensagens
🔴 wms-exemplo-errors: 3 mensagens

⏰ Verificação realizada em: 03/09/2025 às 15:45:30

🧪 Este é um TESTE do sistema de alertas.
Se você está vendo este popup, os alertas estão funcionando perfeitamente!"""
        
        popup(mensagem_teste, "🧪 TESTE - Alerta RabbitMQ")
        
        print("✅ Teste concluído!")
        print("📋 Se o popup apareceu, o sistema de alertas está funcionando!")
        print("❌ Se não apareceu, verifique:")
        print("   - Windows: pip install pywin32")
        print("   - Linux: sudo apt-get install zenity")
        print("   - macOS: Permissões do AppleScript")
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("📦 Execute a partir da pasta raiz do projeto")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
