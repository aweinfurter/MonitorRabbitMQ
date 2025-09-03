#!/usr/bin/env python3
"""
Script de Teste - Detecção Automática de Navegador
Testa se o sistema detecta corretamente o navegador baseado no SO
"""

import sys
import os

# Adiciona o diretório src ao path para importações
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Função principal de teste"""
    print("🧪 Teste de Detecção Automática de Navegador")
    print("=" * 50)
    
    try:
        from modules.selenium_embed import SeleniumEmbedded
        
        # Criar instância para testar detecção
        print("📱 Criando instância do Selenium...")
        selenium = SeleniumEmbedded()
        
        # Obter informações do navegador
        info = selenium.obter_info_navegador()
        
        print(f"\n🔍 Informações Detectadas:")
        print(f"   Sistema Operacional: {info['sistema']}")
        print(f"   Navegador Selecionado: {info['navegador']}")
        print(f"   Suporte Headless: {'Sim' if info['suporte_headless'] else 'Não'}")
        print(f"   Requer Configuração: {'Sim' if info['requer_configuracao'] else 'Não'}")
        
        if info['instrucoes']:
            print(f"\n⚙️ Instruções de Configuração:")
            for i, instrucao in enumerate(info['instrucoes'], 1):
                print(f"   {i}. {instrucao}")
        
        # Perguntar se quer testar o navegador
        resposta = input(f"\n🚀 Deseja testar o {info['navegador']}? (s/n): ").lower().strip()
        
        if resposta in ['s', 'sim', 'y', 'yes']:
            print(f"\n🔧 Iniciando teste do {info['navegador']}...")
            
            if selenium.testar_navegador():
                print("\n✅ Teste concluído com sucesso!")
                print("   O navegador está funcionando corretamente.")
            else:
                print("\n❌ Teste falhou!")
                print("   Verifique as configurações do navegador.")
        else:
            print("\n⏭️ Teste pulado pelo usuário.")
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("💡 Certifique-se de que as dependências estão instaladas:")
        print("   pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        
    print(f"\n📋 Teste concluído!")

if __name__ == "__main__":
    main()
