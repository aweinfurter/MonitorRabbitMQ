"""
MonitorRabbitMQ - Sistema Web Integrado (Versão Modular)
Monitor automatizado de filas RabbitMQ com interface web completa

Desenvolvido por: André Weinfurter - TOTVS
Email: andre.weinfurter@totvs.com.br
Versão: v3.0.0 - Setembro 2025

Arquitetura Modular:
- web_app.py: Classe principal e orquestração
- web_routes.py: Todas as rotas Flask
- web_logging.py: Sistema de logs e WebSocket
- selenium_manager.py: Gestão do Selenium embarcado
- monitoring_engine.py: Motor de monitoramento
- config_manager.py: Gestão de configurações (já existente)
"""

import os
import sys
import json
import threading
import time
import webbrowser
from flask import Flask
from datetime import datetime

# Importa versão
try:
    from src.version import VERSION
except ImportError:
    try:
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from version import VERSION
    except ImportError:
        VERSION = "v3.0.0"

# Importa módulos segregados
try:
    from src.modules.web_logging import WebLoggingSystem
    from src.modules.web_routes import WebRoutes
    from src.modules.selenium_manager import SeleniumManager, SELENIUM_DISPONIVEL
    from src.modules.monitoring_engine import MonitoringEngine
except ImportError:
    try:
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from modules.web_logging import WebLoggingSystem
        from modules.web_routes import WebRoutes
        from modules.selenium_manager import SeleniumManager, SELENIUM_DISPONIVEL
        from modules.monitoring_engine import MonitoringEngine
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        sys.exit(1)

class MonitorRabbitMQWebApp:
    """Aplicação web principal do MonitorRabbitMQ - Versão Modular"""
    
    def __init__(self):
        # Configuração básica do Flask
        self.app = Flask(__name__, 
                         template_folder='templates',
                         static_folder='templates/static')
        self.app.secret_key = 'monitorrabbit_secret_2025'
        
        # SocketIO desabilitado temporariamente
        self.socketio = None
        
        # Estado da aplicação
        self.config = None
        self.is_monitoring = False
        self.status = "🟡 Pronto para iniciar"
        self.modo_debug = False
        self.modo_headless = True
        self.usar_selenium_embarcado = SELENIUM_DISPONIVEL
        
        # Inicializa módulos segregados
        self._inicializar_modulos()
        
        # Configurar rotas e carregar configuração inicial
        self._configurar_aplicacao()
    
    def _inicializar_modulos(self):
        """Inicializa todos os módulos segregados"""
        # Sistema de logs (passa referência do app_instance para controle de debug)
        self.logging_system = WebLoggingSystem(self.socketio, self)
        
        # Ativa interceptação de prints para capturar logs dos módulos
        self.original_print, print_interceptado = self.logging_system.capturar_prints_modulos()
        
        # Substitui print global temporariamente
        import builtins
        builtins.print = print_interceptado
        
        # Gerenciador do Selenium
        self.selenium_manager = SeleniumManager(self.config, self.logging_system)
        
        # Motor de monitoramento
        self.monitoring_engine = MonitoringEngine(self)
        
        # Gerenciador de rotas
        self.web_routes = WebRoutes(self)
    
    def _configurar_aplicacao(self):
        """Configura a aplicação"""
        # Configura rotas
        self.web_routes.configurar_rotas(self.app)
        
        # Carrega configuração inicial
        self.carregar_configuracao()
        
        # Atualiza referências de config nos módulos
        self.selenium_manager.config = self.config
        self.monitoring_engine.config = self.config
    
    def carregar_configuracao(self):
        """Carrega configuração usando o módulo original"""
        try:
            from modules.config import carregar_configuracoes
            self.config = carregar_configuracoes()
            
            # Atualiza modo headless se configurado
            if 'modo_headless' in self.config:
                self.modo_headless = self.config['modo_headless']
                self.selenium_manager.modo_headless = self.modo_headless
                
            return self.config
        except Exception as e:
            print(f"Erro ao carregar config: {e}")
            # Fallback para carregar do arquivo direto
            self.config = self._carregar_config_fallback()
            return self.config
    
    def _carregar_config_fallback(self):
        """Carrega configuração com fallback"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'config.txt')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._configuracao_padrao()
        except:
            return self._configuracao_padrao()
    
    def _configuracao_padrao(self):
        """Configuração padrão se não conseguir carregar"""
        return {
            "sso_username": "",
            "sso_password": "",
            "sso_mfa_token": "",
            "rabbitmq_password": "",
            "regex_filtro": "wms.+-errors|documento.+-errors|etiqueta.+-errors|wes.+-errors",
            "intervalo_minutos": 10,
            "filas_monitoradas": [
                "wms-selecao-estoque-errors.wms-selecao-estoque-errors",
                "wms-separacao-errors.wms-separacao-errors",
                "wms-picking-errors.wms-picking-errors",
                "wms-query-errors.wms-query-errors",
                "wms-estoque-errors.wms-estoque-errors",
                "wms-expedicao-errors.wms-expedicao-errors"
            ],
            "serviço_selecionado": "Staging",
            "username": "supply-logistica-devops",
            "modo_headless": True
        }
    
    def salvar_configuracao_arquivo(self):
        """Salva configuração no arquivo"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'config.txt')
            # Filtra campos sensíveis (SSO) para que fiquem apenas em sso_config.json
            data_to_persist = {k: v for k, v in self.config.items() if not k.startswith('sso_')}
            data_to_persist.pop('sso_mfa_token', None)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data_to_persist, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuração salva em {config_file}")
        except Exception as e:
            print(f"❌ Erro ao salvar configuração: {e}")
    
    def atualizar_status(self, novo_status):
        """Atualiza status e notifica clientes"""
        self.status = novo_status
        self.logging_system.emitir_socketio('status_update', {
            'is_monitoring': self.is_monitoring,
            'status': self.status,
            'modo_debug': self.modo_debug
        })
    
    def atualizar_status_web(self, dados):
        """Atualiza status na interface web"""
        self.logging_system.emitir_socketio('status_update', dados)
    
    def executar(self, debug=False, porta=5000):
        """Executa a aplicação web"""
        try:
            self._exibir_informacoes_inicializacao(porta)
            
            # Abre automaticamente o navegador
            self._abrir_navegador_automatico(porta)
            
            # Inicia servidor Flask
            self.app.run(host='127.0.0.1', port=porta, debug=debug)
            
        except KeyboardInterrupt:
            print("\n🛑 Servidor encerrado pelo usuário")
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor: {e}")
    
    def _exibir_informacoes_inicializacao(self, porta):
        """Exibe informações de inicialização"""
        print(f"🚀 MonitorRabbitMQ {VERSION} - Sistema Web Modular")
        print("👨‍💻 Desenvolvido por André Weinfurter - TOTVS")
        print("🌐 Iniciando servidor web...")
        print("=" * 60)
        print("📁 Arquitetura Modular:")
        print("  ├── web_app.py: Orquestração principal")
        print("  ├── web_routes.py: Rotas Flask")
        print("  ├── web_logging.py: Sistema de logs")
        print("  ├── selenium_manager.py: Gestão Selenium")
        print("  └── monitoring_engine.py: Motor de monitoramento")
        print("=" * 60)
        print(f"🔗 Servidor disponível em: http://localhost:{porta}")
        print("📱 Interface web carregando...")
        print("🔄 Para parar: Ctrl+C")
        print("=" * 60)
    
    def _abrir_navegador_automatico(self, porta):
        """Abre o navegador automaticamente"""
        def abrir_navegador():
            time.sleep(1.5)  # Aguarda servidor iniciar
            url = f"http://localhost:{porta}"
            print(f"🌐 Abrindo navegador: {url}")
            webbrowser.open(url)
        
        # Thread para abrir navegador
        threading.Thread(target=abrir_navegador, daemon=True).start()

def main():
    """Função principal para execução standalone"""
    try:
        print("🔄 Inicializando MonitorRabbitMQ Web (Versão Modular)...")
        app = MonitorRabbitMQWebApp()
        app.executar(debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Aplicação encerrada pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()
