"""
Módulo de configuração do MonitorRabbitMQ
Responsável por carregar e gerenciar as configurações do sistema
Agora utiliza configurações internas seguras
"""

import json
import os
import sys
from .config_manager import config_manager

# Informações da versão
try:
    from src.version import VERSION as VERSAO
except ImportError:
    try:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from version import VERSION as VERSAO
    except ImportError:
        VERSAO = "v3.0.0"
DATA = "Agosto 2025"

def atualizar_urls_servico(config):
    """Atualiza as URLs baseado no serviço selecionado"""
    servico_selecionado = config.get("serviço_selecionado", "Produção")
    # Suporta ambas chaves 'serviços' e 'servicos' e formatos string ou dict
    servicos = config.get('servicos', config.get('serviços', {}))
    svc = servicos.get(servico_selecionado)
    if svc:
        if isinstance(svc, dict):
            url = svc.get('url')
        else:
            url = str(svc)
        print(f"🌐 URL atualizada para {servico_selecionado}: {url}")
    else:
        print(f"⚠️ Serviço '{servico_selecionado}' não encontrado, usando Produção como padrão")

def carregar_configuracoes():
    """Carrega configurações do gerenciador interno"""
    try:
        print("📄 Carregando configurações internas seguras...")
        config = config_manager.obter_configuracao_completa()
        atualizar_urls_servico(config)
        print("✅ Configurações carregadas com sucesso!")
        print(f"📊 {len(config.get('filas_monitoradas', []))} filas serão monitoradas")
        return config
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")
        return config_manager.obter_configuracao_completa()

def obter_url_rabbitmq():
    """Obtém a URL atual do RabbitMQ baseado na configuração"""
    config = carregar_configuracoes()
    servico_selecionado = config.get("serviço_selecionado", "Produção")
    # Suporta ambas chaves e formatos (string ou dict)
    servicos = config.get('servicos', config.get('serviços', {}))
    default_url = 'https://message-broker.totvs.app/#/'

    svc = servicos.get(servico_selecionado)
    if svc:
        if isinstance(svc, dict):
            url = svc.get('url') or default_url
        else:
            url = str(svc)
        print(f"🌐 Usando URL do {servico_selecionado}: {url}")
        return url

    # fallback para chave Produção
    prod = servicos.get('Produção') or servicos.get('Producao')
    if prod:
        url = prod.get('url') if isinstance(prod, dict) else str(prod)
        print(f"⚠️ Serviço '{servico_selecionado}' não encontrado, usando Produção: {url}")
        return url

    print(f"⚠️ Serviço '{servico_selecionado}' não encontrado e nenhuma URL padrão configurada, usando fallback: {default_url}")
    return default_url

def obter_url_queues_rabbitmq():
    """Obtém a URL das filas do RabbitMQ baseado na configuração"""
    return obter_url_rabbitmq() + "queues"

def salvar_config_interno(config_dados):
    """Salva apenas dados sensíveis internos"""
    config_manager.atualizar_config_interno(config_dados)
    # Persistência já é feita dentro de atualizar_config_interno

def salvar_config_nao_sensivel(config_dados):
    """Salva apenas dados não-sensíveis"""
    config_manager.atualizar_config_nao_sensivel(config_dados)
    # Persiste as configurações no arquivo
    config_manager.salvar_configuracao_arquivo()

def obter_configuracoes():
    """Obtém as configurações carregadas"""
    return carregar_configuracoes()

def salvar_config_interno(config_dados):
    """Salva apenas dados sensíveis internos"""
    config_manager.atualizar_config_interno(config_dados)
    # Persistência já é feita dentro de atualizar_config_interno

def salvar_config_nao_sensivel(config_dados):
    """Salva apenas dados não-sensíveis"""
    config_manager.atualizar_config_nao_sensivel(config_dados)
    # Persiste as configurações no arquivo
    config_manager.salvar_configuracao_arquivo()
