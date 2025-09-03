"""
Módulo de Selenium Embarcado
Sistema híbrido para executar Selenium dentro da aplicação web
usando uma div escondida para máxima compatibilidade
"""

import os
import time
import threading
import base64
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class SeleniumEmbedded:
    """Classe para controlar Selenium de forma embarcada na aplicação web"""
    
    def __init__(self, modo_escondido=False, callback_log=None):
        self.driver = None
        self.modo_escondido = modo_escondido
        self.callback_log = callback_log or print
        self.is_running = False
        self.screenshot_base64 = None
    
    def _detectar_sistema_operacional(self):
        """Detecta o sistema operacional atual"""
        sistema = platform.system().lower()
        return sistema
    
    def _eh_macos(self):
        """Verifica se está rodando no macOS"""
        return self._detectar_sistema_operacional() == 'darwin'
        
    def log(self, mensagem, categoria="INFO"):
        """Envia log para callback"""
        self.callback_log(f"[Selenium] {mensagem}", categoria)

    def inicializar_driver(self, user_data_dir=None):
        """Inicializa o driver baseado no sistema operacional"""
        if self._eh_macos():
            print("😎😎😎😎:ramon-feliz:😎😎😎😎")
            return self._inicializar_chromium_macos()
        else:
            return self._inicializar_chromium(user_data_dir)
    
    def _configurar_opcoes_chrome(self, user_data_dir=None):
            chrome_options = Options()
            
            if self.modo_escondido:
                # Modo headless para execução escondida
                chrome_options.add_argument("--headless=new")
                self.log("👻 Modo headless ativado")
            else:
                # Modo visual para debugging
                chrome_options.add_argument("--start-maximized")
                self.log("🖥️ Modo visual ativado")
            
            # Configurações comuns para máxima compatibilidade
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Acelera carregamento
            chrome_options.add_argument("--disable-javascript-harmony-shipping")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--remote-debugging-port=0")  # Porta dinâmica
            
            # Suprime avisos desnecessários do Chrome
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-dev-tools-console")
            chrome_options.add_argument("--silent")
            chrome_options.add_argument("--log-level=3")  # FATAL apenas
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-background-networking")
            chrome_options.add_argument("--disable-sync")
            chrome_options.add_argument("--disable-translate")
            chrome_options.add_argument("--disable-features=AutofillServerCommunication")
            chrome_options.add_argument("--disable-features=Translate")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # User data directory personalizado se fornecido
            if user_data_dir:
                chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
                self.log(f"📁 Usando diretório de dados: {user_data_dir}")
            
            # Prefs para otimização
            prefs = {
                "profile.default_content_setting_values": {
                    "images": 2,  # Bloquear imagens
                    "plugins": 2,  # Bloquear plugins
                    "popups": 2,  # Bloquear popups
                    "geolocation": 2,  # Bloquear localização
                    "notifications": 2,  # Bloquear notificações
                    "media_stream": 2,  # Bloquear câmera/microfone
                },
                "profile.managed_default_content_settings": {
                    "images": 2
                }
            }
            chrome_options.add_experimental_option("prefs", prefs)

            return chrome_options

    def _inicializar_chromium(self, user_data_dir=None):
        """Inicializa o driver Chrome com as configurações apropriadas"""
        try:
            self.log("🔧 Inicializando driver Chromium...")
            chrome_options = self._configurar_opcoes_chrome(user_data_dir=user_data_dir)
            
            # Instala e configura o ChromeDriver automaticamente
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                self.log("✅ Driver instalado automaticamente via ChromeDriverManager")
            except Exception as e:
                self.log(f"⚠️ Falha no ChromeDriverManager: {e}")
                # Fallback para Chrome padrão do sistema
                self.driver = webdriver.Chrome(options=chrome_options)
                self.log("✅ Usando Chrome padrão do sistema")
            
            # Configurações do driver
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(60)
            
            # Definir tamanho da janela mesmo em headless para screenshots
            self.driver.set_window_size(1920, 1080)
            
            self.is_running = True
            self.log("🎯 Driver Chrome inicializado com sucesso!")
            return True
            
        except Exception as e:
            self.log(f"❌ Erro ao inicializar driver: {e}", "ERROR")
            return False
    
    def _inicializar_chromium_macos(self, user_data_dir=None, modo_stealth=False):

        """
        Cria e configura o driver do Chrome com modo selecionável
        modo_stealth: False = visível para login, True = sempre invisível
        """
        # Suprime logs do ChromeDriver também
        os.environ['WDM_LOG_LEVEL'] = '0'
    
        if modo_stealth:
            print("👻 Chrome será executado em modo STEALTH (100% invisível)")
        else:
            print("🔍 Chrome será executado em modo DEBUG (visível para login)")
    
        # Configura o serviço do Chrome com gerenciamento automático do driver
        service = Service(ChromeDriverManager().install())
        options = self._configurar_opcoes_chrome(modo_stealth)

         # 🔒 FORÇA o caminho do Chrome no macOS
        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
        self.driver = webdriver.Chrome(service=service, options=options)
    
        if modo_stealth:
            print("✅ Chrome iniciado em modo STEALTH - 100% invisível!")
        else:
            print("✅ Chrome iniciado em modo DEBUG - visível para autenticação!")
        
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(60)
        self.driver.set_window_size(1920, 1080)
        self.is_running = True

        return True

    def navegar_para_url(self, url):
        """Navega para uma URL específica"""
        try:
            if not self.driver:
                self.log("❌ Driver não inicializado", "ERROR")
                return False
            # Validação: garantir que url seja string e não vazia
            if isinstance(url, dict):
                # Tenta extrair campo 'url' se for um dict
                url = url.get('url') if 'url' in url else None

            if url is None:
                self.log("❌ URL inválida (None) recebida para navegação", "ERROR")
                return False

            url = str(url)
            if not url.strip():
                self.log(f"❌ URL vazia recebida para navegação: '{url}'", "ERROR")
                return False

            self.log(f"🌐 Navegando para (tipo={type(url).__name__}): {url[:120]}")
            self.driver.get(url)
            self.atualizar_estado()
            self.log(f"✅ Página carregada: {self.current_url}")
            return True
            
        except Exception:
            self.log("❌ Erro ao navegar: exceção não esperada", "ERROR")
            return False
    
    def capturar_screenshot(self):
        """Captura screenshot da página atual e retorna em base64"""
        try:
            if not self.driver:
                return None
            
            # Captura screenshot como PNG
            screenshot_png = self.driver.get_screenshot_as_png()
            
            # Converte para base64
            screenshot_b64 = base64.b64encode(screenshot_png).decode('utf-8')
            self.screenshot_base64 = f"data:image/png;base64,{screenshot_b64}"
            
            return self.screenshot_base64
            
        except Exception as e:
            self.log(f"⚠️ Erro ao capturar screenshot: {e}", "WARNING")
            return None
    
    def atualizar_estado(self):
        """Atualiza o estado interno com informações da página"""
        try:
            if not self.driver:
                return
            
            # As propriedades page_source e current_url são atualizadas automaticamente
            # Captura screenshot se estiver em modo escondido
            if self.modo_escondido:
                self.capturar_screenshot()
                
        except Exception as e:
            self.log(f"⚠️ Erro ao atualizar estado: {e}", "WARNING")
    
    def executar_javascript(self, script):
        """Executa JavaScript na página"""
        try:
            if not self.driver:
                return None
            
            resultado = self.driver.execute_script(script)
            self.log(f"📜 JavaScript executado: {script[:50]}...")
            return resultado
            
        except Exception as e:
            self.log(f"❌ Erro ao executar JavaScript: {e}", "ERROR")
            return None
    
    def encontrar_elemento(self, by, value, timeout=10):
        """Encontra elemento na página com timeout"""
        try:
            if not self.driver:
                return None
            
            # Verifica se a sessão ainda é válida
            if not self.verificar_sessao_valida():
                self.log("⚠️ Sessão inválida detectada, tentando recuperar...", "WARNING")
                return None
            
            wait = WebDriverWait(self.driver, timeout)
            elemento = wait.until(EC.presence_of_element_located((by, value)))
            self.log(f"✅ Elemento encontrado: {by}={value}")
            return elemento
            
        except Exception as e:
            # Verifica se é erro de sessão inválida
            if "invalid session id" in str(e).lower():
                self.log("❌ Sessão inválida detectada, finalizando driver", "ERROR")
                self.finalizar()
                return None
            
            self.log(f"⚠️ Elemento não encontrado: {by}={value} - {e}", "WARNING")
            return None
    
    def verificar_sessao_valida(self):
        """Verifica se a sessão do Selenium ainda é válida"""
        try:
            if not self.driver:
                return False
            # Tenta uma operação simples para verificar se a sessão está ativa
            _ = self.driver.current_url
            return True
        except Exception as e:
            if "invalid session id" in str(e).lower():
                self.log("❌ Sessão detectada como inválida", "ERROR")
                return False
            return True
    
    @property
    def page_source(self):
        """Obtém o código fonte da página de forma segura"""
        try:
            if not self.driver or not self.verificar_sessao_valida():
                return ""
            return self.driver.page_source
        except Exception:
            return ""
    
    @property 
    def current_url(self):
        """Obtém a URL atual de forma segura"""
        try:
            if not self.driver or not self.verificar_sessao_valida():
                return ""
            return self.driver.current_url
        except Exception:
            return ""
    
    def preencher_campo(self, by, value, texto, limpar=True):
        """Preenche um campo de input"""
        try:
            elemento = self.encontrar_elemento(by, value)
            if elemento:
                if limpar:
                    elemento.clear()
                elemento.send_keys(texto)
                self.log(f"✅ Campo preenchido: {value}")
                return True
            return False
            
        except Exception as e:
            self.log(f"❌ Erro ao preencher campo: {e}", "ERROR")
            return False
    
    def clicar_elemento(self, by, value):
        """Clica em um elemento"""
        try:
            elemento = self.encontrar_elemento(by, value)
            if elemento:
                elemento.click()
                self.log(f"✅ Clique realizado: {value}")
                time.sleep(1)  # Pequena pausa após clique
                self.atualizar_estado()
                return True
            return False
            
        except Exception as e:
            self.log(f"❌ Erro ao clicar: {e}", "ERROR")
            return False
    
    def aguardar_elemento_aparecer(self, by, value, timeout=30):
        """Aguarda um elemento aparecer na página"""
        try:
            if not self.driver:
                return False
            
            self.log(f"⏳ Aguardando elemento: {value}")
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((by, value)))
            self.log(f"✅ Elemento apareceu: {value}")
            self.atualizar_estado()
            return True
            
        except Exception as e:
            self.log(f"⏰ Timeout aguardando elemento: {value}", "WARNING")
            return False
    
    def obter_informacoes_pagina(self):
        """Retorna informações completas da página atual"""
        info = {
            'url': self.current_url,
            'titulo': '',
            'screenshot': self.screenshot_base64,
            'elementos_visiveis': [],
            'status': 'ativo' if self.is_running else 'inativo'
        }
        
        try:
            if self.driver:
                info['titulo'] = self.driver.title
                
                # Lista alguns elementos importantes visíveis
                elementos = self.driver.find_elements(By.CSS_SELECTOR, "input, button, a, form")
                info['elementos_visiveis'] = [
                    {
                        'tag': elem.tag_name,
                        'tipo': elem.get_attribute('type'),
                        'id': elem.get_attribute('id'),
                        'classe': elem.get_attribute('class'),
                        'texto': elem.text[:50] if elem.text else ''
                    }
                    for elem in elementos[:10]  # Limita a 10 elementos
                ]
                
        except Exception as e:
            self.log(f"⚠️ Erro ao obter informações: {e}", "WARNING")
        
        return info
    
    def alternar_modo_visibilidade(self):
        """Alterna entre modo headless e visual"""
        try:
            if self.driver:
                self.finalizar()
            
            self.modo_escondido = not self.modo_escondido
            modo_texto = "escondido" if self.modo_escondido else "visual"
            self.log(f"🔄 Alternando para modo {modo_texto}")
            
            return self.inicializar_driver()
            
        except Exception as e:
            self.log(f"❌ Erro ao alternar modo: {e}", "ERROR")
            return False
    
    def finalizar(self):
        """Finaliza o driver e limpa recursos"""
        try:
            if self.driver:
                self.log("🛑 Finalizando driver...")
                self.driver.quit()
                self.driver = None
                self.is_running = False
                self.log("✅ Driver finalizado com sucesso")
                
        except Exception as e:
            self.log(f"⚠️ Erro ao finalizar driver: {e}", "WARNING")

# Classe singleton para uso global
_selenium_instance = None

def obter_selenium_instance(modo_escondido=True, callback_log=None):
    """Obtém a instância singleton do Selenium"""
    global _selenium_instance
    
    if _selenium_instance is None:
        _selenium_instance = SeleniumEmbedded(modo_escondido, callback_log)
    
    return _selenium_instance

def finalizar_selenium_global():
    """Finaliza a instância global do Selenium"""
    global _selenium_instance
    
    if _selenium_instance:
        _selenium_instance.finalizar()
        _selenium_instance = None