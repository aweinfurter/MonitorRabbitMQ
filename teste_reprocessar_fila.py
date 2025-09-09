from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("🔄 Abrindo a URL...")
    driver.get("https://totvstfs.visualstudio.com/TOTVSApps/_build?definitionId=5358")

    print("✉️ Aguardando input de e-mail...")
    email_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "i0116"))
    )
    email_input.send_keys("SEU_EMAIL_AQUI")
    email_input.send_keys(Keys.ENTER)
    print("✅ E-mail digitado")

    print("🔑 Aguardando input de senha...")
    senha_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "i0118"))
    )
    senha_input.send_keys("SUA_SENHA_AQUI")
    senha_input.send_keys(Keys.ENTER)
    print("✅ Senha digitada")

    print("📲 Aguardando botão Authenticator...")
    auth_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[data-value='PhoneAppNotification']"))
    )
    auth_button.click()
    print("✅ Botão 'Aprovar no aplicativo' clicado")

    print("⌛ Aguardando token aparecer...")
    token_div = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "idRichContext_DisplaySign"))
    )
    token_value = token_div.text.strip()
    print(f"🔑 Token capturado: {token_value}")

    # Mostra no navegador
    driver.execute_script(f"alert('Token de verificação: {token_value}')")

    print("✅ Alerta exibido no navegador. Feche para continuar...")

    WebDriverWait(driver, 60).until(EC.alert_is_present())
    driver.switch_to.alert.accept()

    print("☑️ Selecionando checkbox...")
    kmsi_checkbox = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "KmsiCheckboxField"))
    )
    kmsi_checkbox.click()

    print("➡️ Clicando no botão 'Sim'...")
    submit_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.ID, "idSIButton9"))
    )
    submit_button.click()

    print("🎉 Login finalizado com sucesso!")

except Exception as e:
    print(f"❌ Erro: {e}")

finally:
    print("🔚 Encerrando navegador...")
    driver.quit()
