"""
Módulo de autenticação SSO
Responsável por realizar login automático no SSO e RabbitMQ
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def fazer_login_sso_automatico(driver, sso_username, sso_password, mfa_token=None, timeout=60):
    """Faz login automático no SSO se as credenciais estiverem configuradas"""
    try:
        if not sso_username or not sso_password:
            print("⚠️ Credenciais do SSO não configuradas no config.txt")
            print("👤 Faça o login do SSO manualmente na janela do navegador")
            return False
        
        print("🤖 Tentando login automático do SSO...")
        print(f"👤 Usuário SSO: {sso_username}")
        
        wait = WebDriverWait(driver, timeout)
        
        # Aguarda aparecer os campos de login do SSO
        # Procura por campos com id/name "username" e "password" que NÃO sejam do RabbitMQ
        sso_detected = wait.until(
            lambda driver: (
                len(driver.find_elements(By.CSS_SELECTOR, "input[name='username'], input[id='username']")) > 0 and
                len(driver.find_elements(By.CSS_SELECTOR, "input[name='password'], input[id='password']")) > 0 and
                # Verifica se NÃO é a tela do RabbitMQ
                "RabbitMQ" not in driver.page_source and
                "message-broker.totvs.app" not in driver.current_url
            )
        )
        
        print("✅ Tela de login do SSO detectada!")
        
        # Busca os campos de username e password (tenta diferentes seletores)
        username_field = None
        password_field = None
        
        # Tenta encontrar por name primeiro
        username_candidates = driver.find_elements(By.NAME, "username")
        password_candidates = driver.find_elements(By.NAME, "password")
        
        # Se não encontrar por name, tenta por id
        if not username_candidates:
            username_candidates = driver.find_elements(By.ID, "username")
        if not password_candidates:
            password_candidates = driver.find_elements(By.ID, "password")
        
        # Se ainda não encontrar, tenta por type
        if not username_candidates:
            username_candidates = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
        if not password_candidates:
            password_candidates = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        
        if username_candidates:
            username_field = username_candidates[0]
        if password_candidates:
            password_field = password_candidates[0]
        
        if not username_field or not password_field:
            print("❌ Não foi possível encontrar os campos de login do SSO")
            return False
        
        # Preenche as credenciais do SSO
        print("🔒 Preenchendo credenciais do SSO...")
        username_field.clear()
        username_field.send_keys(sso_username)
        
        password_field.clear()
        password_field.send_keys(sso_password)
        
        # Procura botão de login/submit
        login_buttons = []
        
        # Tenta diferentes seletores para o botão de login
        button_selectors = [
            "input[type='submit']",
            "button[type='submit']", 
            "button:contains('Login')",
            "button:contains('Entrar')",
            "button:contains('Sign in')",
            "*[role='button']:contains('Login')",
            "*[role='button']:contains('Entrar')"
        ]
        

        try:
            buttons = driver.find_elements(By.ID, "login-button")
            login_buttons.extend(buttons)
        except:
            password_field.send_keys(Keys.RETURN)
 
        if login_buttons:
            print("🖱️ Clicando no botão de login do SSO...")
            login_buttons[0].click()
            print("✅ Login do SSO realizado automaticamente!")

             # Aguarda um pouco para o redirecionamento e então verifica MFA
            time.sleep(1)

            empresa_xpath = "//*[ (self::div[@class='item-name'] or self::span[@class='tooltip-text']) and normalize-space(text())='TOTVS S/A']"
            if driver.find_elements(By.XPATH, empresa_xpath):
                print("🏢 Tela de seleção de empresa detectada...")
                selecionar_empresa_e_logar(driver, "TOTVS S/A")
                print("✅ Empresa selecionada e login finalizado!")
            else:
                print("ℹ️ Nenhuma seleção de empresa necessária")
            
            # Verifica se apareceu campo de MFA e preenche automaticamente
            if mfa_token:
                if detectar_e_preencher_mfa(driver, mfa_token):
                    print("✅ Token MFA preenchido automaticamente!")
                else:
                    print("ℹ️ Campo MFA não detectado ou já processado")
            else:
                print("⚠️ Token MFA não configurado - se aparecer tela de MFA, preencha manualmente")

            return True
        else:
            print("⚠️ Botão de login não encontrado, pressione Enter manualmente")
            # Tenta pressionar Enter no campo de senha como fallback
            password_field.send_keys(Keys.RETURN)
            print("✅ Enter enviado no campo de senha")

            # Aguarda um pouco e verifica MFA mesmo sem botão
            time.sleep(2)
            if mfa_token:
                if detectar_e_preencher_mfa(driver, mfa_token):
                    print("✅ Token MFA preenchido automaticamente!")

            return True
            
    except Exception as e:
        print(f"❌ Erro no login automático do SSO: {e}")
        print("👤 Faça o login do SSO manualmente se necessário")
        return False

def aguardar_sso_e_fazer_login_completo(driver, username, password, timeout=120):
    """Aguarda SSO e faz login completo automaticamente no RabbitMQ"""
    try:
        print("⏳ Aguardando login do SSO completar...")
        print("🔍 Detectando automaticamente quando aparecer o login do RabbitMQ...")
        
        wait = WebDriverWait(driver, timeout)
        
        # Aguarda até aparecer elementos específicos do RabbitMQ (não do SSO)
        rabbit_login_detected = wait.until(
            lambda driver: (
                # Verifica se existe campo username E campo password juntos
                len(driver.find_elements(By.NAME, "username")) > 0 and
                len(driver.find_elements(By.NAME, "password")) > 0 and
                # E verifica se há algum texto indicativo do RabbitMQ na página OU URL específica
                ("RabbitMQ" in driver.page_source or 
                 "Management" in driver.page_source or
                 "message-broker.totvs.app" in driver.current_url)
            )
        )
        
        print("✅ Tela de login do RabbitMQ detectada!")
        
        # Pega os campos de login
        input_username = driver.find_element(By.NAME, "username")
        input_password = driver.find_element(By.NAME, "password")
        
        # Preenche username
        print(f"🤖 Preenchendo username: {username}")
        input_username.clear()
        input_username.send_keys(username)
        
        # Preenche senha automaticamente se fornecida
        if password:
            print("🔒 Preenchendo senha automaticamente...")
            input_password.clear()
            input_password.send_keys(password)
            
            # Procura e clica no botão de login
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
                print("🖱️ Clicando no botão de login...")
                login_button.click()
                print("✅ Login automático realizado!")
                return True
            except Exception as e:
                print(f"⚠️ Não foi possível clicar automaticamente no botão de login: {e}")
                print("👤 Clique manualmente no botão 'Login' no navegador")
                return True
        else:
            print("⚠️ Senha não configurada no config.txt")
            print("👤 Digite sua SENHA manualmente no navegador e clique em Login")
            return True
        
    except Exception as e:
        print(f"❌ Erro ao detectar tela de login do RabbitMQ: {e}")
        print("Faça o login manualmente se necessário.")
        return False

def aguardar_login_completar(driver, timeout=60):
    """Aguarda até o login estar completo (detecta a presença do menu)"""
    try:
        print("⏳ Aguardando login completar...")
        
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((By.ID, "menu")))
        
        print("✅ Login realizado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Timeout aguardando login: {e}")
        return False

def detectar_e_preencher_mfa(driver, mfa_token, timeout=10):
    """Detecta campo de MFA e preenche automaticamente com o token fornecido"""
    try:
        print("🔍 Verificando se apareceu campo de MFA...")
        
        wait = WebDriverWait(driver, timeout)
        
        # Lista de possíveis seletores para campos de MFA
        mfa_selectors = [
            "#mfa-token",           # ID específico mencionado pelo usuário
            "input[id*='mfa']",     # Input com 'mfa' no id
            "input[name*='mfa']",   # Input com 'mfa' no name
            "input[id*='token']",   # Input com 'token' no id
            "input[name*='token']", # Input com 'token' no name
            "input[id*='code']",    # Input com 'code' no id
            "input[name*='code']",  # Input com 'code' no name
            "input[id*='2fa']",     # Input com '2fa' no id
            "input[name*='2fa']",   # Input com '2fa' no name
            "input[placeholder*='token']",    # Input com 'token' no placeholder
            "input[placeholder*='código']",   # Input com 'código' no placeholder
            "input[placeholder*='code']",     # Input com 'code' no placeholder
        ]
        
        mfa_field = None
        
        # Tenta encontrar o campo MFA com diferentes seletores
        for selector in mfa_selectors:
            try:
                mfa_fields = driver.find_elements(By.CSS_SELECTOR, selector)
                if mfa_fields:
                    # Pega o primeiro campo visível
                    for field in mfa_fields:
                        if field.is_displayed() and field.is_enabled():
                            mfa_field = field
                            print(f"✅ Campo MFA encontrado com seletor: {selector}")
                            break
                    if mfa_field:
                        break
            except:
                continue
        
        if not mfa_field:
            print("ℹ️ Campo de MFA não encontrado nesta tela")
            return False
        
        # Preenche o token MFA
        print(f"🔐 Preenchendo token MFA: {mfa_token[:2]}***{mfa_token[-2:] if len(mfa_token) > 4 else '***'}")
        mfa_field.clear()
        mfa_field.send_keys(mfa_token)
        
        # Simula pressionar Enter
        print("⌨️ Enviando Enter no campo MFA...")
        mfa_field.send_keys(Keys.RETURN)
        
        print("✅ Token MFA enviado com sucesso!")
        return True
        
    except Exception as e:
        print(f"⚠️ Erro ao processar MFA: {e}")
        return False
    
def selecionar_empresa_e_logar(driver, empresa="TOTVS S/A"):
    wait = WebDriverWait(driver, 10)

    xpath_empresa = f"//*[ (self::div[@class='item-name'] or self::span[@class='tooltip-text']) and normalize-space(text())='{empresa}']"
    elemento = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_empresa)))
    elemento.click()

    botao_entrar = wait.until(EC.element_to_be_clickable((By.ID, "login-select")))
    botao_entrar.click()