"""
Módulo de Selenium Embarcado
Sistema híbrido para executar Selenium dentro da aplicação web
usando uma div escondida para máxima compatibilidade
"""

import os
import time
import threading
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class ChromeDriverError(Exception):
    """Exceção específica para problemas com ChromeDriver"""
    pass

class ChromeDriverError(Exception):
    """Exceção específica para problemas com ChromeDriver"""
    pass

class SeleniumEmbedded:
    """Classe para controlar Selenium de forma embarcada na aplicação web"""
    
    # Constantes para nomes de arquivos
    CHROMEDRIVER_EXE = "chromedriver.exe"
    CHROMEDRIVER = "chromedriver"
    
    def __init__(self, modo_escondido=False, callback_log=None):
        self.driver = None
        self.modo_escondido = modo_escondido
        self.callback_log = callback_log or print
        self.is_running = False
        self.screenshot_base64 = None
        
    def log(self, mensagem, categoria="INFO"):
        """Envia log para callback"""
        self.callback_log(f"[Selenium] {mensagem}", categoria)
    
    def _configurar_chrome_options(self, user_data_dir=None):
        """Configura as opções do Chrome"""
        chrome_options = Options()
        
        if self.modo_escondido:
            chrome_options.add_argument("--headless=new")
            self.log("👻 Modo headless ativado")
        else:
            chrome_options.add_argument("--start-maximized")
            self.log("🖥️ Modo visual ativado")
        
        # Configurações comuns para máxima compatibilidade
        args_comuns = [
            "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
            "--disable-extensions", "--disable-plugins", "--disable-images",
            "--disable-javascript-harmony-shipping", "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows",
            "--disable-ipc-flooding-protection", "--disable-features=TranslateUI",
            "--disable-features=VizDisplayCompositor", "--remote-debugging-port=0",
            "--disable-logging", "--disable-dev-tools-console", "--silent",
            "--log-level=3", "--disable-software-rasterizer",
            "--disable-background-networking", "--disable-sync", "--disable-translate",
            "--disable-features=AutofillServerCommunication", "--disable-features=Translate"
        ]
        
        for arg in args_comuns:
            chrome_options.add_argument(arg)
        
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        if user_data_dir:
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            self.log(f"📁 Usando diretório de dados: {user_data_dir}")
        
        # Prefs para otimização
        prefs = {
            "profile.default_content_setting_values": {
                "images": 2, "plugins": 2, "popups": 2,
                "geolocation": 2, "notifications": 2, "media_stream": 2,
            },
            "profile.managed_default_content_settings": {"images": 2}
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        return chrome_options
    
    def _tentar_chromedriver_manager(self, chrome_options):
        """Tenta usar ChromeDriverManager com timeout"""
        try:
            self.log("🔄 Tentativa 1: ChromeDriverManager com timeout...")
            
            import socket
            socket.setdefaulttimeout(30)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.log("✅ Driver instalado automaticamente via ChromeDriverManager")
            return True
            
        except Exception as e:
            self.log(f"⚠️ Falha no ChromeDriverManager: {e}")
            return False
    
    def _tentar_chrome_padrao(self, chrome_options):
        """Tenta usar Chrome padrão do sistema"""
        try:
            self.log("🔄 Tentativa 2: Chrome padrão do sistema...")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.log("✅ Usando Chrome padrão do sistema")
            return True
            
        except Exception as e:
            self.log(f"⚠️ Falha no Chrome padrão: {e}")
            return False
    
    def _obter_caminhos_chromedriver(self):
        """Retorna lista de caminhos comuns para chromedriver"""
        return [
            self.CHROMEDRIVER_EXE,
            self.CHROMEDRIVER,
            r"C:\Program Files\Google\Chrome\Application\chromedriver.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe",
            r"C:\Windows\System32\chromedriver.exe",
            "/usr/local/bin/chromedriver",
            "/usr/bin/chromedriver",
            os.path.join(os.path.expanduser("~"), "chromedriver"),
            os.path.join(os.path.dirname(__file__), self.CHROMEDRIVER_EXE),
            os.path.join(os.path.dirname(__file__), self.CHROMEDRIVER)
        ]
    
    def _tentar_caminhos_comuns(self, chrome_options):
        """Busca chromedriver em caminhos comuns"""
        try:
            self.log("🔄 Tentativa 3: Buscando chromedriver em caminhos padrão...")
            
            caminhos_comuns = self._obter_caminhos_chromedriver()
            
            for caminho in caminhos_comuns:
                try:
                    if os.path.exists(caminho) or caminho in [self.CHROMEDRIVER_EXE, self.CHROMEDRIVER]:
                        service = Service(caminho)
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        self.log(f"✅ ChromeDriver encontrado em: {caminho}")
                        return True
                except OSError:
                    continue
                    
            self.log("⚠️ ChromeDriver não encontrado em caminhos padrão")
            return False
            
        except Exception as e:
            self.log(f"⚠️ Erro na busca de chromedriver: {e}")
            return False
    
    def _tentar_download_manual(self, chrome_options):
        """Tenta download manual com versões específicas"""
        try:
            self.log("🔄 Tentativa 4: Download manual do ChromeDriver...")
            
            versoes_teste = ["114.0.5735.90", "113.0.5672.63", "112.0.5615.49"]
            
            for versao in versoes_teste:
                try:
                    self.log(f"   Tentando versão {versao}...")
                    driver_path = ChromeDriverManager(version=versao).install()
                    service = Service(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.log(f"✅ ChromeDriver versão {versao} funcionou!")
                    return True
                except OSError:
                    continue
                    
            return False
            
        except Exception as e:
            self.log(f"⚠️ Falha no download manual: {e}")
            return False
    
    def _tentar_modo_compatibilidade(self):
        """Modo compatibilidade máxima com configurações mínimas"""
        try:
            self.log("🔄 Tentativa 5: Modo compatibilidade máxima...")
            
            chrome_options_simples = Options()
            if self.modo_escondido:
                chrome_options_simples.add_argument("--headless")
            chrome_options_simples.add_argument("--no-sandbox")
            chrome_options_simples.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options_simples)
            self.log("✅ Modo compatibilidade máxima funcionou!")
            return True
            
        except Exception as e:
            self.log(f"⚠️ Falha no modo compatibilidade: {e}")
            return False
    
    def _verificar_chrome_instalado(self):
        """Verifica se o Chrome está instalado"""
        import subprocess
        
        comandos_teste = [
            (['google-chrome', '--version'], "Chrome Linux"),
            (['chrome', '--version'], "Chrome"),
        ]
        
        for comando, nome in comandos_teste:
            try:
                result = subprocess.run(comando, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return f"✅ {nome}: {result.stdout.strip()}"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        # Verifica Chrome no Windows
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                return f"✅ Chrome Windows: {path}"
        
        return "❌ Google Chrome não encontrado"
    
    def _verificar_conectividade(self):
        """Verifica conectividade com repositório ChromeDriver"""
        try:
            import requests
            response = requests.get('https://chromedriver.chromium.org/', timeout=10)
            if response.status_code == 200:
                return "✅ Conectividade com repositório ChromeDriver: OK"
            return f"⚠️ Conectividade com repositório ChromeDriver: HTTP {response.status_code}"
        except Exception as e:
            return f"❌ Sem conectividade com repositório ChromeDriver: {e}"
    
    def _verificar_permissoes(self):
        """Verifica permissões de escrita"""
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tmp.write(b"teste")
            return "✅ Permissões de escrita: OK"
        except Exception as e:
            return f"❌ Problemas de permissão de escrita: {e}"
    
    def _verificar_drivers_existentes(self):
        """Verifica se há drivers existentes"""
        caminhos = self._obter_caminhos_chromedriver()
        drivers_encontrados = [c for c in caminhos if os.path.exists(c)]
        
        if drivers_encontrados:
            return f"✅ ChromeDrivers encontrados: {', '.join(drivers_encontrados)}"
        return "⚠️ Nenhum ChromeDriver encontrado em caminhos padrão"
    
    def _verificar_variaveis_ambiente(self):
        """Verifica variáveis de ambiente relacionadas"""
        resultados = []
        env_vars = ['PATH', 'CHROME_EXECUTABLE_PATH', 'CHROMEDRIVER_PATH']
        
        for var in env_vars:
            valor = os.environ.get(var)
            if valor:
                valor_display = f"{valor[:100]}..." if len(valor) > 100 else valor
                resultados.append(f"ℹ️ {var}: {valor_display}")
        
        return resultados
    
    def diagnosticar_ambiente(self):
        """Diagnostica o ambiente para troubleshooting de problemas com ChromeDriver"""
        diagnostico = []
        
        try:
            # Verificações individuais
            diagnostico.append(self._verificar_chrome_instalado())
            diagnostico.append(self._verificar_conectividade())
            diagnostico.append(self._verificar_permissoes())
            diagnostico.append(self._verificar_drivers_existentes())
            diagnostico.extend(self._verificar_variaveis_ambiente())
            
        except Exception as e:
            diagnostico.append(f"❌ Erro durante diagnóstico: {e}")
        
        return diagnostico
    
    def _categorizar_diagnostico(self, diag):
        """Categoriza mensagem de diagnóstico"""
        if "❌" in diag:
            return "ERROR"
        elif "⚠️" in diag:
            return "WARNING"
        else:
            return "INFO"
    
    def exibir_diagnostico(self):
        """Exibe diagnóstico completo do ambiente"""
        self.log("🔍 INICIANDO DIAGNÓSTICO DO AMBIENTE...")
        diagnosticos = self.diagnosticar_ambiente()
        
        for diag in diagnosticos:
            categoria = self._categorizar_diagnostico(diag)
            self.log(diag, categoria)
        
        self.log("🔍 DIAGNÓSTICO CONCLUÍDO")
        return diagnosticos
    
    def inicializar_driver(self, user_data_dir=None):
        """Inicializa o driver Chrome com as configurações apropriadas"""
        try:
            self.log("🔧 Inicializando driver Chrome...")
            
            chrome_options = self._configurar_chrome_options(user_data_dir)
            
            # Tenta diferentes estratégias até uma funcionar
            estrategias = [
                lambda: self._tentar_chromedriver_manager(chrome_options),
                lambda: self._tentar_chrome_padrao(chrome_options),
                lambda: self._tentar_caminhos_comuns(chrome_options),
                lambda: self._tentar_download_manual(chrome_options),
                lambda: self._tentar_modo_compatibilidade(),
            ]
            
            for i, estrategia in enumerate(estrategias, 1):
                if estrategia():
                    break
            else:
                # Se todas as estratégias falharam, executa diagnóstico
                self.log("❌ FALHA CRÍTICA: Todas as estratégias falharam!", "ERROR")
                self.log("🔍 Executando diagnóstico automático...", "INFO")
                self.exibir_diagnostico()
                
                raise ChromeDriverError(
                    "Não foi possível inicializar o ChromeDriver com nenhuma das estratégias disponíveis. "
                    "Verifique se o Google Chrome está instalado e se não há bloqueios de antivírus/firewall. "
                    "Consulte o diagnóstico acima para mais detalhes."
                )
            
            # Configurações finais do driver
            if self.driver:
                self.driver.implicitly_wait(10)
                self.driver.set_page_load_timeout(60)
                self.driver.set_window_size(1920, 1080)
                self.is_running = True
                self.log("🎯 Driver Chrome inicializado com sucesso!")
                return True
            
            return False
            
        except Exception as e:
            self.log(f"❌ Erro ao inicializar driver: {e}", "ERROR")
            return False
    
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
            
        except Exception:
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
