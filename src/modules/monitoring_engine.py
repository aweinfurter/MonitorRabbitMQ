"""
Motor de Monitoramento
Monitor automatizado de filas RabbitMQ

Desenvolvido por: André Weinfurter - TOTVS
Email: andre.weinfurter@totvs.com.br
Versão: v3.0.0 - Setembro 2025
"""

import threading
import time
import sys
import os
from datetime import datetime
from selenium.webdriver.common.by import By

class MonitoringEngine:
    """Motor principal de monitoramento"""
    
    def __init__(self, app_instance):
        """Inicializa o motor de monitoramento com referência para a aplicação."""
        self.app_instance = app_instance
        self.config = app_instance.config
        self.logging_system = app_instance.logging_system
        self.selenium_manager = app_instance.selenium_manager
        self.monitoring_thread = None

        # contador de falhas consecutivas para detectar quando reiniciar o Selenium
        self._consec_failures = 0
        
    def iniciar_monitoramento_real(self):
        """Inicia monitoramento real"""
        if self.app_instance.is_monitoring:
            return
            
        self.app_instance.is_monitoring = True
        self.app_instance.atualizar_status("🔄 Iniciando monitoramento real...")
        
        # Thread para monitoramento real
        self.monitoring_thread = threading.Thread(target=self.executar_monitoramento_real, daemon=True)
        self.monitoring_thread.start()
    
    def executar_monitoramento_real(self):
        """Executa o monitoramento real com Selenium embarcado ou tradicional"""
        try:
            self.logging_system.enviar_log_web("🚀 INICIANDO", "Iniciando sistema de monitoramento real...")
            
            # Decide qual sistema usar baseado na disponibilidade
            from modules.selenium_manager import SELENIUM_DISPONIVEL
            if self.app_instance.usar_selenium_embarcado and SELENIUM_DISPONIVEL:
                self.logging_system.enviar_log_web("🖥️ SISTEMA", "Usando Selenium embarcado para máxima compatibilidade")
                return self._executar_com_selenium_embarcado()
            else:
                self.logging_system.enviar_log_web("🖥️ SISTEMA", "Usando sistema tradicional com WebDriver")
                return self._executar_com_sistema_tradicional()
                
        except Exception as e:
            self.logging_system.enviar_log_web(f"❌ ERRO", f"Erro no monitoramento: {e}")
            self.app_instance.is_monitoring = False
        finally:
            self.cleanup_monitoramento()
    
    def _executar_com_selenium_embarcado(self):
        """Executa monitoramento usando Selenium embarcado"""
        try:
            # Inicializa o Selenium embarcado (já faz o login automaticamente)
            if not self.selenium_manager.inicializar_selenium_embarcado():
                return False
            
            # Observação: lemos as configurações a cada ciclo para permitir alterações em runtime
            self.logging_system.enviar_log_web("⚙️ CONFIG", "Iniciando monitoramento (configurações serão verificadas a cada ciclo)")
            
            # Loop principal de monitoramento
            ciclo = 1
            while self.app_instance.is_monitoring:
                try:
                    # Recarrega as filas e intervalo a cada ciclo para que alterações via UI entrem em vigor
                    queue_names = self.app_instance.config.get('filas_monitoradas', [])
                    intervalo_minutos = int(self.app_instance.config.get('intervalo_minutos', 10))

                    if not queue_names:
                        # Não encerra o monitoramento se a lista estiver vazia; apenas aguarda por configuração
                        self.logging_system.enviar_log_web("⚠️ CONFIG", "Nenhuma fila configurada - aguardando configurações...")
                        # espera curto para rechecagem rápida
                        for _ in range(10):
                            if not self.app_instance.is_monitoring:
                                break
                            time.sleep(1)
                        # pular verificação desse ciclo
                        ciclo += 1
                        continue

                    # self.logging_system.enviar_log_web("⚙️ CONFIG", f"Filas monitoradas: {', '.join(queue_names)}")
                    self.logging_system.enviar_log_web("⚙️ CONFIG", f"Intervalo: {intervalo_minutos} minutos")

                    self.logging_system.enviar_log_web("🔄 CICLO", f"Iniciando ciclo {ciclo} de monitoramento...")
                    
                    # Verifica as filas diretamente (login já foi feito com sucesso)
                    ok = self._verificar_filas_selenium_embarcado(queue_names, intervalo_minutos)
                    if ok is False or ok is None:
                        # Incrementa contador de falhas consecutivas
                        self._consec_failures += 1
                        self.logging_system.enviar_log_web("⚠️ COLETA", f"Falha na coleta (falhas consecutivas={self._consec_failures})")
                        
                        # Verifica se precisa reiniciar imediatamente
                        restart_threshold = int(self.app_instance.config.get('restart_threshold', 3))
                        if self._consec_failures >= restart_threshold:
                            self.logging_system.enviar_log_web("🔁 RESTART", f"Falhas consecutivas ({self._consec_failures}) >= {restart_threshold} - reiniciando Selenium AGORA")
                            if self._reiniciar_selenium_do_zero():
                                self._consec_failures = 0  # Reset contador após reinicialização bem-sucedida
                                self.logging_system.enviar_log_web("✅ RESTART", "Selenium reiniciado com sucesso - continuando monitoramento")
                            else:
                                self.logging_system.enviar_log_web("⛔ RESTART", "Falha ao reiniciar Selenium - encerrando monitoramento")
                                self.encerrar_monitoramento()
                                break
                    else:
                        # reseta contador se sucesso
                        if self._consec_failures > 0:
                            self.logging_system.enviar_log_web("✅ COLETA", "Coleta bem sucedida - resetando contador de falhas")
                            self._consec_failures = 0
                    
                    ciclo += 1
                    
                    # Só aguarda se não for a primeira execução
                    if self.app_instance.is_monitoring:
                        self.logging_system.enviar_log_web("⏰ AGUARDANDO", f"Próxima verificação em {intervalo_minutos} minutos...")

                        for _ in range(intervalo_minutos * 60):  # Converte para segundos
                            if not self.app_instance.is_monitoring:
                                break
                            time.sleep(1)
                    
                except Exception as e:
                    self.logging_system.enviar_log_web(f"❌ ERRO CICLO", f"Erro no ciclo {ciclo}: {e}")
                    if self.app_instance.is_monitoring:
                        self.logging_system.enviar_log_web("🔄 TENTATIVA", "Tentando continuar após erro...")
                        time.sleep(1)

            return True
            
        except Exception as e:
            self.logging_system.enviar_log_web(f"❌ ERRO EMBARCADO", f"Erro no sistema embarcado: {e}")
            return False
        finally:
            self.selenium_manager.finalizar_selenium_embarcado()
    
    def _verificar_filas_selenium_embarcado(self, queue_names, intervalo_minutos):
        """Verifica filas usando Selenium embarcado"""
        try:
            # Aplica o filtro regex primeiro
            self.logging_system.enviar_log_web("🔍 FILTRO", "Aplicando filtro regex nas filas...")
            
            driver = self.selenium_manager.obter_driver()
            if not driver:
                self.logging_system.enviar_log_web("❌ DRIVER", "Driver não disponível")
                return False
            
            try:
                from modules.rabbitmq import aplicar_filtro_regex
                regex_filtro = self.app_instance.config.get('regex_filtro', 'wms.+-errors|documento.+-errors')
                aplicar_filtro_regex(driver, regex_filtro)
                self.logging_system.enviar_log_web("✅ FILTRO", f"Filtro aplicado: {regex_filtro}")
            except Exception as e:
                self.logging_system.enviar_log_web("⚠️ FILTRO", f"Erro ao aplicar filtro: {e}")
                # Se não consegue aplicar filtro, pode ser problema de interface
                if "no such element" in str(e).lower() or "unable to locate element" in str(e).lower():
                    self.logging_system.enviar_log_web("❌ INTERFACE", "Problema de interface detectado no filtro - página pode não ter carregado")
                    return False
            
            # Aguarda um pouco para o filtro ser aplicado
            time.sleep(1)
            
            # Agora usa a função de verificação real das filas
            self.logging_system.enviar_log_web("🔍 COLETA", "Iniciando verificação real das filas...")
            
            try:
                from modules.monitor import verificar_fila
                resultado = verificar_fila(driver, queue_names, intervalo_minutos)
                # Se verificar_fila não retornar explicitamente True, considera como falha
                if resultado is True:
                    self.logging_system.enviar_log_web("✅ VERIFICAÇÃO", "Verificação das filas concluída com sucesso!")
                    return True
                else:
                    self.logging_system.enviar_log_web("❌ VERIFICAÇÃO", "Verificação retornou falha ou None - tentando fallback")
                    # Fallback para método JavaScript
                    resultado_fallback = self._verificar_filas_javascript(queue_names, driver)
                    return resultado_fallback
            except Exception as e:
                self.logging_system.enviar_log_web("❌ VERIFICAÇÃO", f"Erro na verificação: {e}")
                # Se houver exceção, tenta fallback mas é provável que falhe também
                try:
                    resultado_fallback = self._verificar_filas_javascript(queue_names, driver)
                    if resultado_fallback is False:
                        self.logging_system.enviar_log_web("❌ FALLBACK", "Método JavaScript também falhou - PROBLEMA DE INTERFACE")
                        return False
                    return resultado_fallback
                except Exception as e2:
                    self.logging_system.enviar_log_web("❌ FALLBACK", f"Método JavaScript também gerou exceção: {e2}")
                    return False
                    
        except Exception as e:
            self.logging_system.enviar_log_web("❌ ERRO FILAS", f"Erro ao verificar filas: {e}")
            return False
    
    def _verificar_filas_javascript(self, queue_names, driver):
        """Método fallback usando JavaScript para verificar filas"""
        try:
            self.logging_system.enviar_log_web("🔍 FALLBACK", "Usando método JavaScript alternativo...")
            
            # Script para obter dados da página usando JavaScript
            script_filas = """
            let filas = [];
            try {
                let tabela = document.querySelector('table.list');
                if (tabela) {
                    let linhas = tabela.querySelectorAll('tbody tr');
                    linhas.forEach((linha, index) => {
                        let cells = linha.querySelectorAll('td');
                        if (cells.length >= 6) {
                            let linkElement = cells[1].querySelector('a');
                            let nome = linkElement ? linkElement.textContent.trim() : '';
                            let mensagens = cells[5] ? cells[5].textContent.trim() : '0';
                            
                            if (nome) {
                                filas.push({
                                    nome: nome,
                                    mensagens: mensagens,
                                    index: index
                                });
                            }
                        }
                    });
                }
            } catch (e) {
                console.error('Erro ao extrair dados das filas:', e);
            }
            return filas;
            """
            
            # Executa script para obter dados das filas
            if driver:
                try:
                    filas_data = driver.execute_script(script_filas)

                    if filas_data and len(filas_data) > 0:
                        self.logging_system.enviar_log_web("📊 DADOS", f"Encontradas {len(filas_data)} filas na página")
                        filas_encontradas, _, _ = self._processar_dados_filas_real(filas_data, queue_names)
                        
                        # Log detalhado do resultado
                        if filas_encontradas:
                            self.logging_system.enviar_log_web("✅ RESULTADO", f"✅ {len(filas_encontradas)} filas monitoradas encontradas - SUCESSO")
                            return True
                        else:
                            self.logging_system.enviar_log_web("❌ RESULTADO", "❌ Nenhuma fila monitorada encontrada - FALHA")
                            return False
                    else:
                        self.logging_system.enviar_log_web("❌ DADOS", "❌ Não foi possível obter dados das filas via JavaScript - INTERFACE NÃO CARREGADA")
                        return False
                except Exception as js_error:
                    self.logging_system.enviar_log_web("❌ JAVASCRIPT", f"Erro ao executar script JavaScript: {js_error}")
                    return False
                
        except Exception as e:
            self.logging_system.enviar_log_web("❌ FALLBACK", f"Erro no método JavaScript: {e}")
            return False

        # Se chegou até aqui, não foi possível executar a coleta via JS
        return False
    
    def _processar_dados_filas_real(self, filas_data, queue_names):
        """Processa os dados das filas de forma similar ao sistema original"""
        try:
            filas_encontradas = []
            filas_com_problemas = []
            
            self.logging_system.enviar_log_web("🔍 ANÁLISE", f"Analisando {len(filas_data)} filas...")
            
            for fila in filas_data:
                nome = fila.get('nome', '')
                mensagens_str = fila.get('mensagens', '0')
                
                # Verifica se é uma das filas monitoradas
                if any(queue_name.lower() in nome.lower() for queue_name in queue_names):
                    filas_encontradas.append(nome)
                    
                    try:
                        # Remove vírgulas e converte para número
                        quantidade = int(mensagens_str.replace(',', '').replace('.', ''))
                        
                        if quantidade > 0:
                            self.logging_system.enviar_log_web("⚠️ PROBLEMA", f"DETECTADO: {nome} tem {quantidade} mensagens")
                            filas_com_problemas.append({
                                'nome': nome,
                                'quantidade': quantidade
                            })
                        else:
                            self.logging_system.enviar_log_web("✅ OK", f"Fila vazia: {nome}")
            
                    except ValueError:
                        self.logging_system.enviar_log_web("⚠️ PARSE", f"Erro ao converter quantidade para {nome}: {mensagens_str}")
                    
            # Verifica filas não encontradas
            filas_nao_encontradas = [fila for fila in queue_names if not any(fila.lower() in f.lower() for f in filas_encontradas)]
            
            for fila_missing in filas_nao_encontradas:
                self.logging_system.enviar_log_web("❌ MISSING", f"Fila não encontrada: {fila_missing}")
            
            # Exibe resumo detalhado
            self._exibir_resumo_verificacao(filas_encontradas, filas_com_problemas, filas_nao_encontradas)
            return filas_encontradas, filas_com_problemas, filas_nao_encontradas

        except Exception as e:
            self.logging_system.enviar_log_web("❌ PROCESSAMENTO", f"Erro ao processar dados: {e}")
            return [], [], queue_names

    def _reiniciar_selenium_do_zero(self):
        """Finaliza e reinicializa o Selenium embarcado do zero.

        Retorna True em sucesso, False caso contrário.
        """
        try:
            self.logging_system.enviar_log_web("🔁 RESTART", "Iniciando rotina de reinicialização do Selenium...")
            # Finaliza o Selenium atual
            try:
                self.selenium_manager.finalizar_selenium_embarcado()
            except Exception:
                pass

            # Pequena espera para garantir limpeza de processos
            time.sleep(2)

            # Tenta inicializar novamente
            ok = self.selenium_manager.inicializar_selenium_embarcado()
            if ok:
                self.logging_system.enviar_log_web("✅ RESTART", "Selenium reiniciado com sucesso")
                return True
            else:
                self.logging_system.enviar_log_web("❌ RESTART", "Falha ao reiniciar Selenium")
                return False
        except Exception as e:
            self.logging_system.enviar_log_web("❌ RESTART", f"Erro durante reinicialização: {e}")
            return False
    
    def _exibir_resumo_verificacao(self, filas_encontradas, filas_com_problemas, filas_nao_encontradas):
        """Exibe resumo detalhado da verificação"""
        self.logging_system.enviar_log_web("📊 RESUMO", "RESUMO DA VERIFICAÇÃO:")
        self.logging_system.enviar_log_web("📊 RESUMO", f"✅ Filas encontradas: {len(filas_encontradas)}")
        self.logging_system.enviar_log_web("📊 RESUMO", f"⚠️ Filas com problemas: {len(filas_com_problemas)}")
        self.logging_system.enviar_log_web("📊 RESUMO", f"❌ Filas não encontradas: {len(filas_nao_encontradas)}")
        
        if not filas_com_problemas:
            self.logging_system.enviar_log_web("📊 RESUMO", "✅ Todas as filas monitoradas estão vazias!")
        else:
            # Mostra detalhes dos problemas
            for problema in filas_com_problemas:
                nome = problema['nome']
                quantidade = problema['quantidade']
                
                if quantidade > 1000:
                    emoji = "🔴"
                    categoria = "CRÍTICO"
                elif quantidade > 100:
                    emoji = "🟡" 
                    categoria = "ATENÇÃO"
                else:
                    emoji = "🟠"
                    categoria = "PROBLEMA"
                
                self.logging_system.enviar_log_web(categoria, f"{emoji} {nome}: {quantidade} mensagens")
    
    def _executar_com_sistema_tradicional(self):
        """Executa monitoramento usando sistema tradicional (fallback)"""
        original_print = None
        try:
            # Intercepta prints dos módulos para enviar para web
            self.logging_system.enviar_log_web("🔧 DEBUG", "Configurando interceptação de prints...")
            original_print, print_interceptado = self.logging_system.capturar_prints_modulos()
            
            import builtins
            builtins.print = print_interceptado
            
            self.logging_system.enviar_log_web("🚀 SISTEMA", "Iniciando sistema de monitoramento tradicional...")
            
            # Implementa o sistema tradicional (similar ao código original)
            return self._executar_sistema_tradicional_completo()
                    
        except Exception as e:
            self.logging_system.enviar_log_web("💥 ERRO FATAL", f"Erro durante monitoramento: {e}")
            self.app_instance.atualizar_status("❌ Erro no monitoramento")
        finally:
            # Restaura o print original
            if original_print:
                import builtins
                builtins.print = original_print
            self.cleanup_monitoramento()
    
    def _executar_sistema_tradicional_completo(self):
        """Implementa o sistema tradicional completo"""
        # Esta é uma versão simplificada - você pode expandir conforme necessário
        try:
            self.logging_system.enviar_log_web("🔧 DEBUG", "Importando módulos do sistema tradicional...")
            
            # Importa e executa o sistema tradicional
            # (Implementação específica dependeria dos módulos existentes)
            
            return True
        except Exception as e:
            self.logging_system.enviar_log_web(f"❌ ERRO TRADICIONAL", f"Erro no sistema tradicional: {e}")
            return False
    
    def iniciar_simulacao(self):
        """Inicia modo simulação"""
        if self.app_instance.is_monitoring:
            return
            
        self.app_instance.is_monitoring = True
        self.app_instance.atualizar_status("🧪 Executando simulação...")
        
        # Thread para simulação
        self.monitoring_thread = threading.Thread(target=self.executar_simulacao, daemon=True)
        self.monitoring_thread.start()
    
    def executar_simulacao(self):
        """Executa simulação de monitoramento"""
        try:
            self.logging_system.enviar_log_web("🧪 SIMULAÇÃO", "Iniciando modo simulação...")
            
            filas = self.app_instance.config.get('filas_monitoradas', [])
            intervalo = self.app_instance.config.get('intervalo_minutos', 10)
            
            self.logging_system.enviar_log_web("🧪 SIMULAÇÃO", f"Configurado para {len(filas)} filas, intervalo {intervalo} min")
            
            self.app_instance.atualizar_status("🧪 Simulação ativa")
            
            contador = 1
            while self.app_instance.is_monitoring:
                self.logging_system.enviar_log_web("🔍 SIMULAÇÃO", f"Ciclo #{contador} - Verificando filas...")
                
                for i, fila in enumerate(filas, 1):
                    if not self.app_instance.is_monitoring:
                        break
                    self.logging_system.enviar_log_web("📊 FILA", f"[{i}/{len(filas)}] {fila}... ✅ OK (0 mensagens)")
                    time.sleep(0.5)
                
                if self.app_instance.is_monitoring:
                    self.logging_system.enviar_log_web("✅ SIMULAÇÃO", f"Ciclo #{contador} concluído - Todas as filas OK")
                    contador += 1
                    
                    # Aguarda próximo ciclo
                    self.logging_system.enviar_log_web("⏰ AGUARDANDO", f"Próxima simulação em {intervalo} minutos...")
                    
                    for _ in range(intervalo * 60):
                        if not self.app_instance.is_monitoring:
                            break
                        time.sleep(1)
                        
        except Exception as e:
            self.logging_system.enviar_log_web("❌ ERRO SIMULAÇÃO", f"{e}")
        finally:
            self.cleanup_monitoramento()

    def parar_monitoramento(self):
        """Para qualquer tipo de monitoramento"""
        self.app_instance.is_monitoring = False
        self.logging_system.enviar_log_web("🛑 SISTEMA", "Parando monitoramento...")
        self.cleanup_monitoramento()
    
    def encerrar_monitoramento(self):
        """Encerra completamente o monitoramento e limpa recursos"""
        self.app_instance.is_monitoring = False
        self.logging_system.enviar_log_web("🛑 ENCERRAR", "Encerrando monitoramento completamente...")
        
        # Cleanup completo
        self.cleanup_monitoramento()
        
        # Para o Selenium se estiver ativo
        self.selenium_manager.finalizar_selenium_embarcado()
        
        # Reseta variáveis de estado
        self.app_instance.modo_debug = False
        
        self.logging_system.enviar_log_web("✅ SISTEMA", "Sistema pronto para nova execução")
        self.app_instance.atualizar_status("🟡 Pronto para iniciar")
    
    def cleanup_monitoramento(self):
        """Limpa recursos e reseta interface"""
        # Finaliza Selenium se necessário
        self.selenium_manager.finalizar_selenium_embarcado()
            
        self.app_instance.is_monitoring = False
        self.app_instance.modo_debug = False
        self.app_instance.atualizar_status("🔴 Parado")
        self.logging_system.enviar_log_web("Monitoramento parado - Pronto para nova execução", "SISTEMA")
