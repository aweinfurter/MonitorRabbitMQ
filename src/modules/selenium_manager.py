"""
Gerenciador do Sistema Selenium Embarcado
Monitor automatizado de filas RabbitMQ

Desenvolvido por: André Weinfurter - TOTVS
Email: andre.weinfurter@totvs.com.br
Versão: v3.0.0 - Setembro 2025
"""

import sys
import os

# Importa o sistema Selenium embarcado original
try:
    from src.modules.selenium_embed import SeleniumEmbedded
    from src.modules.sso_auth import fazer_login_sso_automatico, aguardar_sso_e_fazer_login_completo
    SELENIUM_DISPONIVEL = True
except ImportError:
    try:
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from selenium_embed import SeleniumEmbedded
        from sso_auth import fazer_login_sso_automatico, aguardar_sso_e_fazer_login_completo
        SELENIUM_DISPONIVEL = True
    except ImportError:
        print("⚠️ Aviso: Sistema Selenium embarcado não disponível")
        SELENIUM_DISPONIVEL = False
        SeleniumEmbedded = None

class SeleniumManager:
    """Gerenciador do sistema Selenium embarcado"""
    
    def __init__(self, config, logging_system):
        self.config = config
        self.logging_system = logging_system
        self.selenium_driver = None
        self.selenium_ativo = False
        self.modo_headless = True
        
    def inicializar_selenium_embarcado(self):
        """Inicializa o sistema Selenium embarcado original"""
        try:
            if not SELENIUM_DISPONIVEL:
                self.logging_system.enviar_log_web("⚠️ Sistema Selenium embarcado não disponível", "WARNING")
                return False
            
            self.logging_system.enviar_log_web("🤖 Inicializando Selenium embarcado...", "INFO")
            
            # Cria instância do Selenium embarcado original
            self.selenium_driver = SeleniumEmbedded(
                modo_escondido=self.modo_headless,
                callback_log=self.logging_system.enviar_log_web
            )
            
            # Obtém configurações
            from modules.config import obter_url_rabbitmq
            url_rabbitmq = obter_url_rabbitmq()
            self.logging_system.enviar_log_web(f"🌐 URL obtida do config: {url_rabbitmq}", "INFO")
            
            if not url_rabbitmq:
                self.logging_system.enviar_log_web("❌ URL do RabbitMQ não configurada", "ERROR")
                return False
            
            # Inicializa o driver
            if not self.selenium_driver.inicializar_driver():
                self.logging_system.enviar_log_web("❌ Falha ao inicializar driver", "ERROR")
                return False
            
            # Navega para a URL
            if not self.selenium_driver.navegar_para_url(url_rabbitmq):
                self.logging_system.enviar_log_web("❌ Falha ao navegar para URL", "ERROR")
                return False
            
            self.selenium_ativo = True
            self.logging_system.enviar_log_web("✅ Selenium embarcado inicializado com sucesso!", "SUCCESS")
            
            # Notifica interface web
            self.logging_system.emitir_socketio('selenium_atualizado', {
                'ativo': True,
                'modo': 'escondido',
                'url': url_rabbitmq
            })
            
            # Inicia processo de login automático
            self.logging_system.enviar_log_web("🔐 Iniciando processo de login via Selenium embarcado...", "INFO")
            
            # Faz login SSO automático
            sso_username = self.config.get('sso_username', '')
            sso_password = self.config.get('sso_password', '')
            sso_mfa_token = self.config.get('sso_mfa_token', '')
            
            if fazer_login_sso_automatico(self.selenium_driver.driver, sso_username, sso_password, sso_mfa_token):
                self.logging_system.enviar_log_web("✅ Login SSO realizado com sucesso!", "SUCCESS")
                
                # Aguarda e faz login no RabbitMQ
                username = self.config.get('username', '')
                password = self.config.get('rabbitmq_password', '')
                
                if aguardar_sso_e_fazer_login_completo(self.selenium_driver.driver, username, password):
                    self.logging_system.enviar_log_web("✅ Login completo realizado com sucesso!", "SUCCESS")
                    
                    # Navega para aba de filas após login bem-sucedido
                    try:
                        from modules.rabbitmq import navegar_para_queues, definir_autorefresh
                        if definir_autorefresh(self.selenium_driver.driver):
                            self.logging_system.enviar_log_web("✅ Auto-refresh definido para 30 segundos", "SUCCESS")
                        else:
                            self.logging_system.enviar_log_web("⚠️ Falha ao definir auto-refresh", "WARNING")
                        self.logging_system.enviar_log_web("🔍 Navegando para aba de filas...", "INFO")
                        if navegar_para_queues(self.selenium_driver.driver):
                            self.logging_system.enviar_log_web("✅ Navegação para filas concluída!", "SUCCESS")
                        else:
                            self.logging_system.enviar_log_web("⚠️ Falha na navegação - continue manualmente", "WARNING")
                    except Exception as e:
                        self.logging_system.enviar_log_web(f"❌ Erro na navegação para filas: {e}", "ERROR")
                    
                    return True
                else:
                    self.logging_system.enviar_log_web("⚠️ Aguardando login RabbitMQ ou timeout", "WARNING")
                    return True  # Considera sucesso mesmo que não detecte RabbitMQ imediatamente
            else:
                self.logging_system.enviar_log_web("⚠️ Login SSO não realizado automaticamente", "WARNING")
                return True  # Considera sucesso para permitir login manual
                
        except Exception as e:
            self.logging_system.enviar_log_web(f"❌ Erro ao inicializar Selenium embarcado: {e}", "ERROR")
            return False

    def obter_estado_navegador(self):
        """Obtém estado atual do navegador"""
        try:
            if not self.selenium_ativo or not self.selenium_driver:
                return {
                    'url': 'N/A',
                    'titulo': 'N/A',
                    'screenshot': None
                }
            
            # Implementa lógica para obter estado do navegador
            url_atual = self.selenium_driver.driver.current_url if self.selenium_driver.driver else 'N/A'
            titulo_atual = self.selenium_driver.driver.title if self.selenium_driver.driver else 'N/A'
            
            # Captura screenshot se disponível
            screenshot = None
            try:
                if self.selenium_driver.driver:
                    screenshot_data = self.selenium_driver.driver.get_screenshot_as_base64()
                    screenshot = f"data:image/png;base64,{screenshot_data}"
            except:
                pass
            
            return {
                'url': url_atual,
                'titulo': titulo_atual,
                'screenshot': screenshot
            }
            
        except Exception as e:
            self.logging_system.enviar_log_web(f"❌ Erro ao obter estado do navegador: {e}", "ERROR")
            return {
                'url': 'Erro',
                'titulo': 'Erro',
                'screenshot': None
            }

    def alternar_modo_visual(self):
        """Alterna entre modo visual e escondido"""
        try:
            if not self.selenium_ativo or not self.selenium_driver:
                return False
            
            # Implementa lógica para alternar modo
            # Esta funcionalidade depende da implementação do SeleniumEmbedded
            self.modo_headless = not self.modo_headless
            
            self.logging_system.enviar_log_web(
                f"🔄 Modo alternado para: {'Headless' if self.modo_headless else 'Visual'}", 
                "INFO"
            )
            
            return True
            
        except Exception as e:
            self.logging_system.enviar_log_web(f"❌ Erro ao alternar modo: {e}", "ERROR")
            return False

    def obter_modo_atual(self):
        """Retorna o modo atual do Selenium"""
        return 'escondido' if self.modo_headless else 'visual'

    def obter_driver(self):
        """Retorna o driver do Selenium se disponível"""
        if self.selenium_ativo and self.selenium_driver:
            return self.selenium_driver.driver
        return None

    def finalizar_selenium_embarcado(self):
        """Finaliza o sistema Selenium embarcado"""
        try:
            if self.selenium_driver:
                if hasattr(self.selenium_driver, 'finalizar'):
                    self.selenium_driver.finalizar()
                elif hasattr(self.selenium_driver, 'driver') and self.selenium_driver.driver:
                    self.selenium_driver.driver.quit()
                
                self.selenium_driver = None
                self.selenium_ativo = False
                
                # Notifica interface web
                self.logging_system.emitir_socketio('selenium_atualizado', {
                    'ativo': False,
                    'modo': 'inativo',
                    'url': 'N/A',
                    'screenshot': None
                })
                
                self.logging_system.enviar_log_web("🛑 Selenium embarcado finalizado", "INFO")
                
        except Exception as e:
            self.logging_system.enviar_log_web(f"⚠️ Erro ao finalizar Selenium: {e}", "WARNING")

    def verificar_login_ativo(self):
        """Verifica se o login ainda está ativo"""
        try:
            if not self.selenium_ativo or not self.selenium_driver:
                return False
            
            estado = self.obter_estado_navegador()
            url_atual = estado.get('url', '')
            
            # Verifica se ainda está na página do RabbitMQ
            if ('rabbitmq' in url_atual.lower() or 
                'message-broker' in url_atual.lower() or
                'totvs.app' in url_atual.lower()):
                return True
            
            return False
            
        except Exception as e:
            self.logging_system.enviar_log_web(f"⚠️ Erro ao verificar login: {e}", "WARNING")
            return False
