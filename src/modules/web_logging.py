"""
Sistema de Logs para Interface Web
Monitor automatizado de filas RabbitMQ

Desenvolvido por: André Weinfurter - TOTVS
Email: andre.weinfurter@totvs.com.br
Versão: v3.0.0 - Setembro 2025
"""

import logging
import warnings
from datetime import datetime

# Suprime logs do Selenium e Chrome
logging.getLogger('selenium').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.CRITICAL)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

# Suprime avisos do sistema
warnings.filterwarnings("ignore")

class WebLoggingSystem:
    """Sistema de logs integrado com interface web"""
    
    def __init__(self, socketio=None, app_instance=None):
        """Inicializa o sistema de logging para a UI.

        Mantém um buffer em memória com lock e um ID incremental para suportar polling
        HTTP quando SocketIO estiver desabilitado.
        """
        self.socketio = socketio
        self.app_instance = app_instance  # Referência para controle de debug

        # Buffer em memória para últimos logs (usado quando SocketIO está desabilitado)
        from collections import deque
        import threading
        self._logs_buffer = deque(maxlen=1000)
        self._logs_lock = threading.Lock()

        # ID incremental para cada log (ajuda polling continuar de onde parou)
        self._next_log_id = 1
        
        # Cache para evitar duplicações
        self._last_logs_cache = deque(maxlen=50)
        
        # Referência para print original (evita recursão)
        self.original_print = print
        
    def enviar_log_web(self, mensagem, categoria="INFO"):
        """Envia log diretamente para a interface web via WebSocket"""
        try:
            # Detecta categoria automaticamente se não especificada
            if categoria == "INFO":
                categoria_detectada = self.detectar_categoria_log(mensagem)
                if categoria_detectada:
                    categoria = categoria_detectada
                else:
                    # Se não detectar categoria, não envia para web
                    return
            
            # AJUSTE: Permite resumos serem exibidos novamente após 30 segundos
            # Para categorias de RESUMO, usa cache com tempo limitado
            if categoria == "RESUMO":
                import time
                current_time = time.time()
                log_key = f"{categoria}:{mensagem}"
                
                # Verifica se já existe no cache com timestamp
                for cached_item in list(self._last_logs_cache):
                    if isinstance(cached_item, tuple) and cached_item[0] == log_key:
                        # Se passou mais de 30 segundos, remove do cache
                        if current_time - cached_item[1] > 30:
                            self._last_logs_cache.remove(cached_item)
                        else:
                            return  # Ainda dentro do tempo de cache
                
                # Adiciona com timestamp para RESUMO
                self._last_logs_cache.append((log_key, current_time))
            else:
                # Para outras categorias, mantém o comportamento original
                log_key = f"{categoria}:{mensagem}"
                if log_key in self._last_logs_cache:
                    return  # Ignora duplicação
                
                # Adiciona ao cache de duplicação
                self._last_logs_cache.append(log_key)

            # Armazena no buffer local para polling HTTP
            try:
                with self._logs_lock:
                    self._logs_buffer.append({
                        'id': self._next_log_id,
                        'categoria': categoria,
                        'mensagem': mensagem,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    self._next_log_id += 1
            except Exception:
                # Não falha o sistema de logs por erro de buffer
                pass
            
            # Se SocketIO estiver disponível, emite para clientes conectados
            if self.socketio:
                self.emitir_socketio('novo_log', {
                    'categoria': categoria,
                    'mensagem': mensagem,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
                
        except Exception as e:
            # Usa print original para evitar recursão
            self.original_print(f"Erro ao enviar log para web: {e}")
    
    def emitir_socketio(self, evento, dados):
        """Função auxiliar para emitir via SocketIO apenas se estiver disponível"""
        try:
            if self.socketio and hasattr(self.socketio, 'emit'):
                self.socketio.emit(evento, dados)
            else:
                print(f"[SocketIO Desabilitado] {evento}: {dados}")
        except Exception as e:
            print(f"Erro ao emitir SocketIO: {e}")

    def obter_logs_recentes(self, from_index=None, max_items=200):
        """Retorna os logs do buffer.

        - Se from_index for None: retorna os últimos `max_items` logs e `next_index` = próximo id a ser consumido.
        - Se from_index for um número inteiro N: retorna logs com id >= N (até max_items) e next_index = last_returned_id + 1.
        Retorna um dicionário: {'logs': [...], 'next_index': int}
        """
        with self._logs_lock:
            logs = list(self._logs_buffer)

        # nenhum log armazenado
        if not logs:
            return {'logs': [], 'next_index': self._next_log_id}

        try:
            if from_index is None:
                # retorna os últimos max_items
                slice_logs = logs[-max_items:]
                # next_index é o id que ainda não foi gerado
                next_index = self._next_log_id
                return {'logs': slice_logs, 'next_index': next_index}
            else:
                idx = int(from_index)
                # filtra logs com id >= idx
                filtered = [l for l in logs if l.get('id', 0) >= idx]
                slice_logs = filtered[:max_items]
                if slice_logs:
                    last_id = slice_logs[-1].get('id', idx)
                    next_index = last_id + 1
                else:
                    next_index = self._next_log_id
                return {'logs': slice_logs, 'next_index': next_index}
        except Exception:
            # fallback: retorna últimos itens
            return {'logs': logs[-max_items:], 'next_index': self._next_log_id}
    
    def capturar_prints_modulos(self):
        """Intercepta prints dos módulos e envia para web"""
        original_print = print
        logging_system = self  # Referência para usar no closure
        
        def print_interceptado(*args, **kwargs):
            # CONTROLE DE DEBUG: Só mostra no terminal se estiver em modo debug
            modo_debug = False
            if logging_system.app_instance:
                modo_debug = getattr(logging_system.app_instance, 'modo_debug', False)
            
            # Se estiver em modo debug, mantém o print original no terminal
            if modo_debug:
                original_print(*args, **kwargs)
            
            # Processa o texto para a web (sempre envia para interface web)
            if args:
                texto = ' '.join(str(arg) for arg in args)
                
                # Evita recursão infinita ignorando logs que já têm prefixo de categoria
                if not texto.startswith('[') or '] ' not in texto[:20]:
                    categoria = logging_system.detectar_categoria_log(texto)
                    if categoria:
                        logging_system.enviar_log_web(texto, categoria)
        
        return original_print, print_interceptado
    
    def detectar_categoria_log(self, texto):
        """Detecta a categoria do log baseado no conteúdo"""
        texto_lower = texto.lower()
        
        # Filtra logs muito longos (lista de filas completas)
        if len(texto) > 200 and "filas monitoradas:" in texto_lower:
            return None  # Não exibe logs muito longos
        
        # Primeiro: detecta logs com formato [CATEGORIA] explícito
        if texto.startswith('[') and ']' in texto:
            categoria_match = texto.split(']')[0].replace('[', '').strip().upper()
            if categoria_match in ['SELENIUM', 'LOGIN', 'RABBITMQ', 'SUCCESS', 'OK', 'PROBLEMA', 
                                   'MISSING', 'RESUMO', 'TIMESTAMP', 'AGUARDANDO', 'EXCECOES', 
                                   'INFO', 'ERRO', 'SISTEMA', 'CONFIG', 'VERIFICACAO', 'COLETA',
                                   'FILTRO', 'TABELA', 'CICLO', 'MONITOR', 'DRIVER', 'CONEXAO']:
                return categoria_match
        
        # Segundo: padrões específicos dos logs dos módulos (emoji-based)
        if "[selenium]" in texto_lower:
            return "SELENIUM"
        elif "🔧" in texto and ("selenium" in texto_lower or "driver" in texto_lower or "inicializando" in texto_lower):
            return "SELENIUM"
        elif "🚀" in texto and ("sistema" in texto_lower or "monitor" in texto_lower):
            return "SISTEMA"
        elif "⚙️" in texto and "config" in texto_lower:
            return "CONFIG" 
        elif "🌐" in texto and "driver" in texto_lower:
            return "DRIVER"
        elif "🔗" in texto and ("navegando" in texto_lower or "conexão" in texto_lower):
            return "CONEXAO"
        elif "🔐" in texto and ("login" in texto_lower or "sso" in texto_lower or "rabbit" in texto_lower):
            return "LOGIN"
        elif "👻" in texto and "stealth" in texto_lower:
            return "STEALTH"
        elif "🎯" in texto and "monitor" in texto_lower:
            return "MONITOR"
        
        # Padrões de COLETA e ETAPAS
        elif "🔍" in texto and ("etapa" in texto_lower and "coletando" in texto_lower):
            return "COLETA"
        elif "🔍" in texto and ("verificação" in texto_lower or "ciclo" in texto_lower):
            return "VERIFICACAO"
        elif "🔍" in texto and ("coleta" in texto_lower or "verificação real" in texto_lower):
            return "COLETA"
        elif "🔍" in texto and ("filtro já está aplicado" in texto_lower or "o filtro" in texto_lower):
            return "FILTRO"
        elif "🔍" in texto and ("encontradas" in texto_lower and "linhas" in texto_lower):
            return "TABELA"
        elif "🔍" in texto and ("aplicando filtro" in texto_lower):
            return "FILTRO"
        elif "🔍" in texto and ("filtro" in texto_lower):
            return "FILTRO"
        elif "🔍" in texto and ("tabela" in texto_lower or "linhas" in texto_lower):
            return "TABELA"
        
        # Padrões de OK e PROBLEMAS
        elif "✅" in texto and ("ok" in texto_lower or "fila vazia" in texto_lower):
            return "OK"
        elif texto_lower.startswith("[ok]") or "fila vazia:" in texto_lower:
            return "OK"
        elif "✅" in texto and ("filtro aplicado" in texto_lower or "checkbox" in texto_lower):
            return "FILTRO"
        elif "✅" in texto and ("todas as filas" in texto_lower and "vazias" in texto_lower):
            return "RESUMO"
        
        # Padrões de RESUMO
        elif "📊" in texto and "resumo" in texto_lower:
            return "RESUMO"
        elif texto.startswith("📊 RESUMO"):
            return "RESUMO"
        elif "filas encontradas:" in texto_lower or "filas com problemas:" in texto_lower:
            return "RESUMO"
        elif "filas não encontradas:" in texto_lower:
            return "RESUMO"
        
        # Outros padrões
        elif "⚠️" in texto and ("problema" in texto_lower or "tem" in texto_lower and "mensagens" in texto_lower):
            return "PROBLEMA"
        elif "❌" in texto and ("missing" in texto_lower or "não encontrada" in texto_lower):
            return "MISSING"
        elif "⏰" in texto and ("timestamp" in texto_lower or "última verificação" in texto_lower):
            return "TIMESTAMP"
        elif "⏰" in texto and ("aguardando" in texto_lower or "próxima verificação" in texto_lower):
            return "AGUARDANDO"
        elif "🔍" in texto and ("exceções" in texto_lower or "extraindo" in texto_lower):
            return "EXCECOES"
        elif "💡" in texto and "info" in texto_lower:
            return "INFO"
        elif "❌" in texto and "erro" in texto_lower:
            return "ERRO"
        elif "🛑" in texto and ("parando" in texto_lower or "sistema" in texto_lower):
            return "SISTEMA"
        else:
            return None  # Não envia para web se não identificar categoria

    def configurar_socketio(self, app, socketio):
        """Configura eventos do SocketIO para logs em tempo real"""
        
        @socketio.on('connect')
        def handle_connect():
            self.emitir_socketio('status_update', {
                'message': 'Cliente conectado ao sistema de logs'
            })
        
        @socketio.on('disconnect')
        def handle_disconnect():
            pass
