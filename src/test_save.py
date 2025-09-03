import json, os, sys
sys.path.insert(0, os.path.abspath('.'))
from modules.config_manager import config_manager, CONFIG_FILE_PATH, SSO_CONFIG_FILE
# Ajusta alguns valores de teste
config_manager.config_interno['sso_username'] = 'usuario_test'
config_manager.config_interno['sso_password'] = 'senha_test'
config_manager.config_interno['sso_mfa_token'] = 'mfa12345'
config_manager.config_padrao['username'] = 'usu_publico'
config_manager.config_padrao['rabbitmq_password'] = 'rabbit_pwd'
# Salva SSO e config
ok1 = config_manager.salvar_sso_arquivo()
ok2 = config_manager.salvar_configuracao_arquivo()
print('SSO saved:', ok1, 'Config saved:', ok2)
# Imprime conteúdos dos arquivos gravados (resumido)
if os.path.exists(SSO_CONFIG_FILE):
    with open(SSO_CONFIG_FILE,'r',encoding='utf-8') as f:
        s = json.load(f)
    print('SSO file keys:', list(s.keys()))
if os.path.exists(CONFIG_FILE_PATH):
    with open(CONFIG_FILE_PATH,'r',encoding='utf-8') as f:
        c = json.load(f)
    print('Config file keys:', list(c.keys()))
