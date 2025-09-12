import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import json
import os
from .config_manager import decodificar_senha

def _obter_config_email():
    """Obtém configurações de email do sso_config.json e config.txt"""
    try:
        # Pega username e senha do sso_config.json
        sso_config_path = os.path.join(os.path.dirname(__file__), '..', 'sso_config.json')
        with open(sso_config_path, 'r', encoding='utf-8') as f:
            sso_config = json.load(f)

        print(sso_config)
        username = sso_config.get("sso_username", "")
        senha_codificada = sso_config.get("email_password", "")
        senha = decodificar_senha(senha_codificada)  # Decodifica a senha
        
        # Pega destinatários do config principal
        from .config_manager import ConfigManager
        config_mgr = ConfigManager()
        config = config_mgr.obter_configuracao_completa()
        destinatarios = config.get("email_recipients", [])
        
        # Se não tem destinatários configurados, usa o próprio username
        if not destinatarios:
            destinatarios = [username]
        
        return username, senha, destinatarios
        
    except Exception as e:
        print(f"❌ Erro ao obter config de email: {e}")
        return None, None, None

def _enviar_email_sync(username, senha, destinatarios,assunto, msg):
    """Envia email sincronamente"""

    try:
        # Adiciona o username à lista de destinatários (evita duplicata)
        todos_destinatarios = list(destinatarios)
        if username not in todos_destinatarios:
            todos_destinatarios.append(username)
        
        # Monta a mensagem
        mensagem = MIMEMultipart()
        mensagem["From"] = username
        mensagem["To"] = ", ".join(todos_destinatarios)
        mensagem["Subject"] = assunto
        mensagem.attach(MIMEText(msg, "plain"))
        
        # Envia
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(username, senha)
            server.sendmail(username, todos_destinatarios, mensagem.as_string())
            print(f"✅ E-mail enviado com sucesso para: {', '.join(todos_destinatarios)}")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao enviar email: {e}")
        return False

def enviar_email(assunto, msg):
    """Envia email em thread separada (não bloqueia)"""
    username, senha, destinatarios = _obter_config_email()

    if not username or not senha or not destinatarios:
        print("Sem configuração de email.")
        return False
    
    print(f"Username: {'✓' if username else '✗'}")
    print(f"Senha: {'✓' if senha else '✗'}")
    print(f"Destinatários: {'✓' if destinatarios else '✗'}")

    def _thread_email(username, senha, destinatarios):
        _enviar_email_sync(username, senha, destinatarios, assunto, msg)
    
    try:
        thread = threading.Thread(target=_thread_email, args=(username, senha, destinatarios), daemon=True)
        thread.start()
        print("📧 Envio de email disparado em background")
        return True
    except Exception as e:
        print(f"❌ Erro ao disparar thread de email: {e}")
        return False