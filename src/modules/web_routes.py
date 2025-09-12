"""
Rotas da Aplicação Web
Monitor automatizado de filas RabbitMQ

Desenvolvido por: André Weinfurter - TOTVS
Email: andre.weinfurter@totvs.com.br
Versão: v3.0.0 - Setembro 2025
"""

from flask import render_template, request, jsonify, redirect, url_for
from datetime import datetime
import base64
import io

try:
    from src.version import VERSION
except ImportError:
    try:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
        from version import VERSION
    except ImportError:
        VERSION = "v3.0.0"

class WebRoutes:
    """Gerenciador de rotas da aplicação web"""
    
    def __init__(self, app_instance):
        self.app_instance = app_instance
        
    def configurar_rotas(self, app):
        """Configura todas as rotas da aplicação web"""
        
        @app.route('/')
        def index():
            """Página inicial - sempre vai para configuração primeiro"""
            return redirect(url_for('configuracao'))
        
        @app.route('/configuracao')
        def configuracao():
            """Página de configuração"""
            if not self.app_instance.config:
                self.app_instance.carregar_configuracao()
            # Passa também a estrutura de serviços como JSON embutido para o JS
            return render_template('configuracao.html', 
                                 config=self.app_instance.config, 
                                 versao=VERSION,
                                 services_json=self.app_instance.config.get('servicos', self.app_instance.config.get('serviços', {})))
        
        @app.route('/salvar_configuracao', methods=['POST'])
        def salvar_configuracao():
            """Salva configuração e redireciona para monitoramento"""
            try:
                data = request.get_json()
                
                # Separa dados sensíveis (SSO) dos não-sensíveis
                try:
                    from src.modules import config as modules_config
                except Exception:
                    # fallback se import relativo
                    from modules import config as modules_config

                sso_data = {
                    'sso_username': data.get('sso_username', ''),
                    'sso_password': data.get('sso_password', ''),
                    'sso_mfa_token': data.get('sso_mfa_token', ''),
                    'email_password': data.get('senha_email', '')  # Campo para senha do email
                }

                # Atualiza a config em memória para uso imediato (mantém SSO em memória)
                # e persiste os dados sensíveis via módulo de config (codificação fica a cargo do manager)
                self.app_instance.config.update(sso_data)
                try:
                    modules_config.salvar_config_interno({
                        'sso_username': sso_data.get('sso_username', ''),
                        'sso_password': sso_data.get('sso_password', ''),
                        'email_password': sso_data.get('email_password', '')  # Salva senha do email no SSO
                    })
                except Exception as e:
                    # Se falhar, apenas logamos; não escrevemos SSO em config.txt
                    print(f"⚠️ Falha ao salvar SSO via modules.config: {e}")
                
                # Atualiza configuração geral
                selected_service = data.get('servico_selecionado', 'Staging')
                self.app_instance.config.update({
                    'username': data.get('username', 'supply-logistica-devops'),
                    'serviço_selecionado': selected_service,
                    'intervalo_minutos': int(data.get('intervalo_minutos', 10)),
                    'regex_filtro': data.get('regex_filtro', 'wms.+-errors|documento.+-errors'),
                    'filas_monitoradas': data.get('filas_monitoradas', []),
                    'email_recipients': data.get('email_recipients', [])  # Adiciona destinatários de email
                })

                # Se a estrutura de serviços for a nova (dict com url/password), atualiza a senha no serviço selecionado
                servicos = self.app_instance.config.get('servicos', self.app_instance.config.get('serviços', {})) or {}
                if isinstance(servicos, dict) and selected_service in servicos:
                    svc = servicos[selected_service]
                    # atualiza password do serviço com o valor vindo do formulário
                    svc_password = data.get('rabbitmq_password', '')
                    if isinstance(svc, dict):
                        svc['password'] = svc_password
                    else:
                        # fallback: sobrescreve entry simples
                            servicos[selected_service] = {'url': str(svc), 'password': svc_password}
                    self.app_instance.config['servicos'] = servicos

                # Mantém compatibilidade e atualiza o campo rabbitmq_password para casos legados
                self.app_instance.config['rabbitmq_password'] = data.get('rabbitmq_password', '')
                
                # Persiste apenas as configurações não-sensíveis via módulo de config
                try:
                    nao_sensiveis = {
                        'username': self.app_instance.config.get('username', 'supply-logistica-devops'),
                        'serviço_selecionado': selected_service,
                        'intervalo_minutos': int(self.app_instance.config.get('intervalo_minutos', 10)),
                        'regex_filtro': self.app_instance.config.get('regex_filtro', ''),
                        'filas_monitoradas': self.app_instance.config.get('filas_monitoradas', []),
                        'rabbitmq_password': self.app_instance.config.get('rabbitmq_password', ''),
                        'email_recipients': self.app_instance.config.get('email_recipients', [])  # Persiste destinatários
                    }
                    modules_config.salvar_config_nao_sensivel(nao_sensiveis)
                except Exception as e:
                    # Fallback: grava filtrando diretamente (garante compatibilidade)
                    print(f"⚠️ Falha ao salvar config via modules.config: {e} - usando fallback")
                    self.app_instance.salvar_configuracao_arquivo()
                
                return jsonify({'success': True, 'message': 'Configuração salva com sucesso!'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro ao salvar: {str(e)}'})
        
        @app.route('/monitoramento')
        def monitoramento():
            """Página de monitoramento"""
            if not self.app_instance.config or not self.app_instance.config.get('sso_username'):
                return redirect(url_for('configuracao'))
            return render_template('monitoramento.html', 
                                 config=self.app_instance.config, 
                                 status=self.app_instance.status, 
                                 versao=VERSION)
        
        # APIs de Status e Controle
        @app.route('/api/status')
        def api_status():
            """API para obter status atual"""
            return jsonify({
                'is_monitoring': self.app_instance.is_monitoring,
                'status': self.app_instance.status,
                'modo_debug': self.app_instance.modo_debug,
                'modo_headless': self.app_instance.modo_headless,
                'config': {
                    'usuario': self.app_instance.config.get('sso_username', 'N/A'),
                    'intervalo': self.app_instance.config.get('intervalo_minutos', 10),
                    'filas_count': len(self.app_instance.config.get('filas_monitoradas', [])),
                    'servico': self.app_instance.config.get('serviço_selecionado', 'N/A')
                }
            })
        
        @app.route('/api/iniciar_monitoramento', methods=['POST'])
        def api_iniciar_monitoramento():
            """API para iniciar monitoramento real"""
            try:
                if self.app_instance.is_monitoring:
                    return jsonify({'success': False, 'message': 'Monitoramento já está ativo'})
                
                self.app_instance.monitoring_engine.iniciar_monitoramento_real()
                return jsonify({'success': True, 'message': 'Monitoramento iniciado'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
        
        @app.route('/api/iniciar_simulacao', methods=['POST'])
        def api_iniciar_simulacao():
            """API para iniciar simulação"""
            try:
                if self.app_instance.is_monitoring:
                    return jsonify({'success': False, 'message': 'Monitoramento já está ativo'})
                
                self.app_instance.monitoring_engine.iniciar_simulacao()
                return jsonify({'success': True, 'message': 'Simulação iniciada'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
        
        @app.route('/api/parar_monitoramento', methods=['POST'])
        def api_parar_monitoramento():
            """API para parar monitoramento"""
            try:
                self.app_instance.monitoring_engine.parar_monitoramento()
                return jsonify({'success': True, 'message': 'Monitoramento parado'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
        
        @app.route('/parar', methods=['POST'])
        def parar():
            """API para encerrar completamente o monitoramento"""
            try:
                self.app_instance.monitoring_engine.encerrar_monitoramento()
                return jsonify({'status': 'success', 'message': 'Monitoramento encerrado completamente'})
                
            except Exception as e:
                return jsonify({'status': 'error', 'message': f'Erro: {str(e)}'})
        
        @app.route('/api/encerrar_sistema', methods=['POST'])
        def api_encerrar_sistema():
            """API para encerrar completamente o sistema"""
            try:
                # Para todos os processos de monitoramento
                self.app_instance.monitoring_engine.encerrar_monitoramento()
                
                # Finaliza Selenium se estiver ativo
                if hasattr(self.app_instance.selenium_manager, 'finalizar_selenium_embarcado'):
                    self.app_instance.selenium_manager.finalizar_selenium_embarcado()
                
                # Atualiza status
                self.app_instance.is_monitoring = False
                self.app_instance.atualizar_status("🛑 Sistema encerrado")
                
                # Agenda o encerramento do Flask em segundo plano
                import threading
                import time
                def encerrar_flask():
                    time.sleep(2)  # Aguarda retorno da requisição
                    import os
                    os._exit(0)  # Força encerramento completo
                
                threading.Thread(target=encerrar_flask, daemon=True).start()
                
                return jsonify({'success': True, 'message': 'Sistema será encerrado em 2 segundos...'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
        @app.route('/api/debug', methods=['POST'])
        def api_debug():
            """API para alternar modo debug (visual/headless)"""
            try:
                if self.app_instance.is_monitoring:
                    return jsonify({'success': False, 'message': 'Pare o monitoramento antes de alterar o modo'})
                
                # Alterna modo headless
                self.app_instance.modo_headless = not self.app_instance.modo_headless
                
                self.app_instance.config['modo_headless'] = self.app_instance.modo_headless
                self.app_instance.salvar_configuracao_arquivo()
                
                modo_texto = "Headless (invisível)" if self.app_instance.modo_headless else "Visual (visível)"
                return jsonify({
                    'success': True, 
                    'modo_headless': self.app_instance.modo_headless,
                    'message': f'Modo alterado para: {modo_texto}'
                })
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
        
        @app.route('/api/alternar_debug_terminal', methods=['POST'])
        def api_alternar_debug_terminal():
            """API para alternar modo debug de logs no terminal"""
            try:
                # Alterna modo debug
                self.app_instance.modo_debug = not self.app_instance.modo_debug
                
                # Teste imediato para verificar se funciona
                print(f"🔧 TESTE DEBUG: Modo debug alterado para {self.app_instance.modo_debug}")
                
                modo_texto = "Ativado (logs aparecem no terminal)" if self.app_instance.modo_debug else "Desativado (logs só na web)"
                return jsonify({
                    'success': True, 
                    'modo_debug': self.app_instance.modo_debug,
                    'message': f'🖥️ Modo debug terminal: {modo_texto}'
                })
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
        # APIs do Selenium Embarcado
        @app.route('/api/selenium/screenshot', methods=['POST'])
        def api_selenium_screenshot():
            """API para capturar screenshot do Selenium"""
            try:
                if not self.app_instance.selenium_manager.selenium_ativo:
                    return jsonify({'success': False, 'message': 'Selenium não está ativo'})
                
                estado = self.app_instance.selenium_manager.obter_estado_navegador()
                screenshot = estado.get('screenshot')
                
                if screenshot:
                    # Atualiza interface via WebSocket
                    self.app_instance.logging_system.emitir_socketio('selenium_atualizado', {
                        'ativo': True,
                        'screenshot': screenshot,
                        'url': estado.get('url', 'N/A')
                    })
                    
                    return jsonify({
                        'success': True, 
                        'screenshot': screenshot,
                        'message': 'Screenshot capturado'
                    })
                else:
                    return jsonify({'success': False, 'message': 'Erro ao capturar screenshot'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
        
        @app.route('/api/selenium/alternar_modo', methods=['POST'])
        def api_selenium_alternar_modo():
            """API para alternar modo visual/escondido do Selenium"""
            try:
                if not self.app_instance.selenium_manager.selenium_ativo:
                    return jsonify({'success': False, 'message': 'Selenium não está ativo'})
                
                if self.app_instance.selenium_manager.alternar_modo_visual():
                    modo_atual = self.app_instance.selenium_manager.obter_modo_atual()
                    
                    # Atualiza interface via WebSocket
                    self.app_instance.logging_system.emitir_socketio('selenium_atualizado', {
                        'ativo': True,
                        'modo': modo_atual
                    })
                    
                    return jsonify({
                        'success': True, 
                        'modo': modo_atual,
                        'message': f'Modo alternado para {modo_atual}'
                    })
                else:
                    return jsonify({'success': False, 'message': 'Erro ao alternar modo'})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
        
        @app.route('/api/selenium/status', methods=['GET'])
        def api_selenium_status():
            """API para obter status do Selenium"""
            try:
                if not self.app_instance.selenium_manager.selenium_ativo:
                    return jsonify({
                        'ativo': False,
                        'modo': 'inativo',
                        'url': 'N/A',
                        'screenshot': None
                    })
                
                estado = self.app_instance.selenium_manager.obter_estado_navegador()
                return jsonify({
                    'ativo': True,
                    'modo': self.app_instance.selenium_manager.obter_modo_atual(),
                    'url': estado.get('url', 'N/A'),
                    'screenshot': estado.get('screenshot'),
                    'titulo': estado.get('titulo', 'N/A')
                })
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})

        # API de Logs para polling HTTP
        @app.route('/api/logs', methods=['GET'])
        def api_logs():
            """Retorna logs recentes para polling HTTP quando SocketIO estiver desabilitado."""
            try:
                # opcional: cliente pode enviar ?from_index=NUMBER para obter apenas novos logs
                from_index = request.args.get('from_index')
                max_items = int(request.args.get('max', 200))

                if hasattr(self.app_instance, 'logging_system') and hasattr(self.app_instance.logging_system, 'obter_logs_recentes'):
                    result = self.app_instance.logging_system.obter_logs_recentes(from_index, max_items)
                    # result deve conter {'logs': [...], 'next_index': N}
                    return jsonify({'success': True, 'logs': result.get('logs', []), 'next_index': result.get('next_index', None)})
                else:
                    return jsonify({'success': True, 'logs': [], 'next_index': None})
            except Exception as e:
                return jsonify({'success': False, 'message': f'Erro: {str(e)}'})
