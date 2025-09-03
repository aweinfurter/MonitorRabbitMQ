"""
Gerenciador de Configurações Seguras
Mantém dados sensíveis internos e permite configuração via interface web
"""

import json
import os
import base64
import sys

# Constantes para os arquivos de configuração
CONFIG_FILE = "config.txt"

# Define o diretório base para os arquivos de configuração
def _get_config_directory():
    """Obtém o diretório onde ficam os arquivos de configuração"""
    if getattr(sys, 'frozen', False):
        # Se executando como executável (PyInstaller, cx_Freeze, etc.)
        return os.path.dirname(sys.executable)
    else:
        # Se executando em modo de desenvolvimento
        # Os arquivos de config ficam na pasta src
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(current_dir)  # Volta de modules para src

SSO_CONFIG_FILE = os.path.join(_get_config_directory(), "sso_config.json")
CONFIG_FILE_PATH = os.path.join(_get_config_directory(), CONFIG_FILE)

def codificar_senha(senha):
    """Codifica a senha usando base64"""
    if not senha:
        return ""
    return base64.b64encode(senha.encode('utf-8')).decode('utf-8')

def decodificar_senha(senha_codificada):
    """Decodifica a senha usando base64"""
    if not senha_codificada:
        return ""
    try:
        return base64.b64decode(senha_codificada.encode('utf-8')).decode('utf-8')
    except Exception:
        return senha_codificada  # Se falhar, retorna original (compatibilidade)

class ConfigManager:
    def __init__(self):
        # Configurações internas (sensíveis) - ficam ocultas no executável
        self.config_interno = {
            "sso_username": "",
            "sso_password": "",
            "sso_mfa_token": ""
        }
        
        # Configurações padrão (não-sensíveis) - podem ser exportadas
        self.config_padrao = {
            "filas": [
                "wms-selecao-estoque-errors.wms-selecao-estoque-errors",
                "wms-separacao-errors.wms-separacao-errors",
                "wms-picking-errors.wms-picking-errors",
                "wms-query-errors.wms-query-errors",
                "wms-estoque-errors.wms-estoque-errors",
                "wms-expedicao-errors.wms-expedicao-errors",
                "wms-conferencia-expedicao-errors.wms-conferencia-expedicao-errors",
                "wms-recebimento-errors.wms-recebimento-errors",
                "wms-atividade-extra-errors.wms-atividade-extra-errors",
                "wes-core-errors.wes-core-errors",
                "wes-query-errors.wes-query-errors",
                "wms-conferencia-recebimento-errors.wms-conferencia-recebimento-errors",
                "wms-endereco-errors.wms-endereco-errors",
                "wms-estoque-fiscal-errors.wms-estoque-fiscal-errors",
                "wms-manufatura-errors.wms-manufatura-errors",
                "inventario-errors.inventario-errors",
                "wms-inventario-errors.wms-inventario-errors",
                "documento-errors.documento-errors",
                "documento-query-errors.errors",
                "etiqueta-query-errors.etiqueta-query-errors",
                "wms-integracao-errors.wms-integracao-errors",
                "wms-setup-errors.wms-setup-errors"
            ],
            "filas_monitoradas": [
                "wms-selecao-estoque-errors.wms-selecao-estoque-errors",
                "wms-separacao-errors.wms-separacao-errors",
                "wms-picking-errors.wms-picking-errors",
                "wms-query-errors.wms-query-errors",
                "wms-estoque-errors.wms-estoque-errors",
                "wms-expedicao-errors.wms-expedicao-errors",
                "wms-conferencia-expedicao-errors.wms-conferencia-expedicao-errors",
                "wms-recebimento-errors.wms-recebimento-errors",
                "wms-atividade-extra-errors.wms-atividade-extra-errors",
                "wes-core-errors.wes-core-errors",
                "wes-query-errors.wes-query-errors",
                "wms-conferencia-recebimento-errors.wms-conferencia-recebimento-errors",
                "wms-endereco-errors.wms-endereco-errors",
                "wms-estoque-fiscal-errors.wms-estoque-fiscal-errors",
                "wms-manufatura-errors.wms-manufatura-errors",
                "inventario-errors.inventario-errors",
                "wms-inventario-errors.wms-inventario-errors",
                "documento-errors.documento-errors",
                "documento-query-errors.errors",
                "etiqueta-query-errors.etiqueta-query-errors",
                "wms-integracao-errors.wms-integracao-errors",
                "wms-setup-errors.wms-setup-errors"
            ],
            "serviços": {
                "Staging": {
                    "url": "https://message-broker.staging.totvs.app/#/",
                    "password": ""
                },
                "Produção": {
                    "url": "https://message-broker.totvs.app/#/",
                    "password": ""
                }
            },
            "serviço_selecionado": "Produção",
            "username": "supply-logistica-devops",
            "rabbitmq_password": "lvf4G285N9!RbxZM@ysUDCPUtoebjW",
            "intervalo_minutos": 10,
            "regex_filtro": "wms.+-errors|documento.+-errors|etiqueta.+-errors|wes.+-errors"
        }
        
        # Carrega configurações do arquivo se existir
        self.carregar_configuracao_arquivo()
        # Carrega credenciais SSO do arquivo se existir
        self.carregar_sso_arquivo()
    
    def carregar_sso_arquivo(self):
        """Carrega credenciais SSO do arquivo sso_config.json se existir"""
        try:
            if os.path.exists(SSO_CONFIG_FILE):
                with open(SSO_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    sso_dados = json.load(f)
                
                # Atualiza campos válidos de SSO e decodifica a senha
                for chave in self.config_interno:
                    # Nunca carrega o token MFA a partir do arquivo: deve permanecer apenas em memória
                    if chave == 'sso_mfa_token':
                        continue

                    if chave in sso_dados:
                        if chave == "sso_password":
                            # Decodifica a senha
                            self.config_interno[chave] = decodificar_senha(sso_dados[chave])
                        else:
                            self.config_interno[chave] = sso_dados[chave]
                
                print(f"🔐 Credenciais SSO carregadas do arquivo {SSO_CONFIG_FILE}")
            else:
                print(f"🔐 Arquivo {SSO_CONFIG_FILE} não encontrado, SSO precisará ser configurado")
        except Exception as e:
            print(f"⚠️ Erro ao carregar {SSO_CONFIG_FILE}: {e}, SSO precisará ser configurado")
    
    def salvar_sso_arquivo(self):
        """Salva as credenciais SSO no arquivo sso_config.json"""
        try:
            # Cria uma cópia dos dados para codificar a senha
            dados_para_salvar = self.config_interno.copy()

            # Não persistir o token MFA em disco - mantê-lo somente em memória
            if 'sso_mfa_token' in dados_para_salvar:
                dados_para_salvar.pop('sso_mfa_token', None)

            if "sso_password" in dados_para_salvar:
                dados_para_salvar["sso_password"] = codificar_senha(dados_para_salvar["sso_password"])
            
            with open(SSO_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(dados_para_salvar, f, indent=2, ensure_ascii=False)
            print(f"🔐 Credenciais SSO salvas no arquivo {SSO_CONFIG_FILE}")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar credenciais SSO: {e}")
            return False
    
    def carregar_configuracao_arquivo(self):
        """Carrega configurações do arquivo config.txt se existir"""
        try:
            if os.path.exists(CONFIG_FILE_PATH):
                with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                    config_arquivo = json.load(f)
                
                # Atualiza apenas campos válidos
                def _normalize_services(raw_services, fallback_pwd=''):
                    """Converte formato antigo de services para o novo formato {name: {url,password}}"""
                    if not isinstance(raw_services, dict):
                        return raw_services
                    normalized = {}
                    for name, value in raw_services.items():
                        if isinstance(value, str):
                            normalized[name] = {'url': value, 'password': fallback_pwd}
                        elif isinstance(value, dict):
                            normalized[name] = value
                    return normalized

                for chave in self.config_padrao:
                    if chave in config_arquivo:
                        if chave == 'serviços':
                            raw = config_arquivo[chave]
                            self.config_padrao[chave] = _normalize_services(raw, config_arquivo.get('rabbitmq_password', ''))
                        else:
                            self.config_padrao[chave] = config_arquivo[chave]
                
                print(f"📄 Configurações carregadas do arquivo {CONFIG_FILE_PATH}")
            else:
                print(f"📄 Arquivo {CONFIG_FILE_PATH} não encontrado, usando configurações padrão")
        except Exception as e:
            print(f"⚠️ Erro ao carregar {CONFIG_FILE_PATH}: {e}, usando configurações padrão")
    
    def obter_configuracao_completa(self):
        """Retorna configuração completa (interno + padrão)"""
        config_completa = self.config_padrao.copy()
        config_completa.update(self.config_interno)
        return config_completa
    
    def atualizar_config_interno(self, novos_dados):
        """Atualiza apenas dados sensíveis internos"""
        for chave in self.config_interno:
            if chave in novos_dados:
                # Atualiza em memória - salvamento em disco ocorrerá em salvar_sso_arquivo(),
                # que já ignora o campo 'sso_mfa_token'.
                self.config_interno[chave] = novos_dados[chave]

        # Persiste as credenciais SSO (salvar_sso_arquivo ignora sso_mfa_token)
        self.salvar_sso_arquivo()
    
    def atualizar_config_nao_sensivel(self, novos_dados):
        """Atualiza apenas dados não-sensíveis"""
        for chave in self.config_padrao:
            if chave in novos_dados:
                self.config_padrao[chave] = novos_dados[chave]
    
    def salvar_configuracao_arquivo(self):
        """Salva as configurações não-sensíveis no arquivo config.txt"""
        try:
            with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config_padrao, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar configurações no arquivo: {e}")
            return False

# Instância global do gerenciador
config_manager = ConfigManager()
