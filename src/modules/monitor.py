"""
Módulo de monitoramento de filas
Responsável por verificar o status das filas e extrair exceções
"""

import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .rabbitmq import extrair_excecoes_de_message_box, voltar_para_queues
from .ui import popup

def extrair_excecoes_fila(driver, nome_fila, quantidade_mensagens):
    """Extrai as exceções das mensagens de uma fila específica"""
    try:
        print(f"🔍 Entrando na fila {nome_fila} para extrair exceções...")
        
        # Garante que estamos na página de queues antes de começar
        try:
            current_url = driver.current_url
            if "#/queues" not in current_url:
                print("🔄 Navegando de volta para a página de queues primeiro...")
                voltar_para_queues(driver)
        except:
            voltar_para_queues(driver)
        
        # MELHORIA: Aguarda explicitamente que a tabela esteja completamente carregada
        try:
            print("⏳ Aguardando tabela carregar completamente...")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.list tbody tr"))
            )
        except:
            print("⚠️ Timeout aguardando tabela, continuando...")
        
        # SOLUÇÃO DEFINITIVA: Busca e clique em operação única para evitar stale elements
        sucesso_clique = False
        for tentativa in range(3):
            try:
                print(f"🔍 Tentativa {tentativa + 1}: Buscando e clicando na fila {nome_fila}")
                
                # ESTRATÉGIA 1: XPath direto com clique via JavaScript (mais confiável)
                try:
                    xpath_selector = f"//table[@class='list']//a[contains(text(), '{nome_fila}')]"
                    print(f"🎯 Usando XPath: {xpath_selector}")
                    
                    # Busca e clica em uma única operação via JavaScript
                    clique_js_script = f"""
                    var xpath = "{xpath_selector}";
                    var result = document.evaluate(xpath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null);
                    var link = result.singleNodeValue;
                    if (link && link.offsetParent !== null) {{
                        link.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                        setTimeout(function() {{
                            link.click();
                        }}, 1000);
                        return true;
                    }}
                    return false;
                    """
                    
                    resultado = driver.execute_script(clique_js_script)
                    if resultado:
                        print(f"✅ Clique via JavaScript XPath realizado na fila {nome_fila}")
                        time.sleep(1)  # Aguarda o clique ser processado
                        sucesso_clique = True
                        break
                    else:
                        print("⚠️ Link não encontrado ou não visível via XPath JavaScript")
                
                except Exception as e_js_xpath:
                    print(f"⚠️ Erro no clique JavaScript XPath: {e_js_xpath}")
                
                # ESTRATÉGIA 2: Clique por índice se o XPath falhar
                if not sucesso_clique:
                    try:
                        print("🔄 Tentando estratégia por índice na tabela...")
                        
                        # Script para encontrar por texto e clicar pelo índice
                        clique_por_indice_script = f"""
                        var tabela = document.querySelector('table.list tbody');
                        if (!tabela) return false;
                        
                        var linhas = tabela.querySelectorAll('tr');
                        for (var i = 0; i < linhas.length; i++) {{
                            var links = linhas[i].querySelectorAll('a');
                            for (var j = 0; j < links.length; j++) {{
                                if (links[j].textContent.includes('{nome_fila}') && links[j].offsetParent !== null) {{
                                    links[j].scrollIntoView({{behavior: 'smooth', block: 'center'}});
                                    setTimeout(function() {{
                                        links[j].click();
                                    }}, 1000);
                                    return true;
                                }}
                            }}
                        }}
                        return false;
                        """
                        
                        resultado = driver.execute_script(clique_por_indice_script)
                        if resultado:
                            print(f"✅ Clique por índice realizado na fila {nome_fila}")
                            time.sleep(1)
                            sucesso_clique = True
                            break
                        else:
                            print("⚠️ Link não encontrado via índice")
                    
                    except Exception as e_indice:
                        print(f"⚠️ Erro no clique por índice: {e_indice}")
                
                # ESTRATÉGIA 3: Busca tradicional como último recurso
                if not sucesso_clique:
                    try:
                        print("🔄 Tentando busca tradicional como último recurso...")
                        
                        # Aguarda elemento estar presente e clicável
                        link_element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, nome_fila))
                        )
                        
                        # Scroll e clique imediato
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link_element)
                        
                        # Tenta clique normal primeiro
                        try:
                            link_element.click()
                            print(f"✅ Clique tradicional realizado na fila {nome_fila}")
                            sucesso_clique = True
                            break
                        except:
                            # Se falhar, usa JavaScript no elemento encontrado
                            driver.execute_script("arguments[0].click();", link_element)
                            print(f"✅ Clique JavaScript tradicional realizado na fila {nome_fila}")
                            sucesso_clique = True
                            break
                            
                    except Exception as e_tradicional:
                        print(f"⚠️ Busca tradicional falhou: {e_tradicional}")
                
                # Se todas as estratégias falharam nesta tentativa
                if not sucesso_clique:
                    print(f"⚠️ Tentativa {tentativa + 1} falhou com todas as estratégias")
                    if tentativa < 2:  # Se não for a última tentativa
                        print("🔄 Recarregando página para próxima tentativa...")
                        driver.refresh()
                        time.sleep(5)
                        
                        # Aguarda tabela recarregar
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "table.list tbody tr"))
                            )
                        except:
                            pass
                
            except Exception as e:
                print(f"⚠️ Erro na tentativa {tentativa + 1}: {e}")
                continue
        
        if not sucesso_clique:
            print(f"❌ Não foi possível clicar no link da fila {nome_fila} após 3 tentativas")
            return []
        
        # Aguarda a página carregar
        print("⏳ Aguardando página da fila carregar...")
        time.sleep(1)
        
        # Verifica e expande a seção "Get messages" se necessário
        try:
            print("🎯 Verificando seção 'Get messages'...")
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-hidden"))
            )
            
            sections = driver.find_elements(By.CSS_SELECTOR, "div.section-hidden")
            get_messages_section = None
            
            for section in sections:
                try:
                    h2_element = section.find_element(By.CSS_SELECTOR, "h2")
                    if "Get messages" in h2_element.text:
                        get_messages_section = section
                        break
                except:
                    continue
            
            if not get_messages_section:
                print("❌ Seção 'Get messages' não encontrada")
                voltar_para_queues(driver)
                return []
            
            # Verifica se precisa expandir
            classes_secao = get_messages_section.get_attribute("class")
            if "section-visible" in classes_secao:
                print("✅ Seção 'Get messages' já está visível!")
            else:
                print("🖱️ Expandindo seção 'Get messages'...")
                h2_clickable = get_messages_section.find_element(By.CSS_SELECTOR, "h2")
                driver.execute_script("arguments[0].click();", h2_clickable)
                time.sleep(3)
                
        except Exception as e:
            print(f"❌ Erro com seção 'Get messages': {e}")
            voltar_para_queues(driver)
            return []
        
        # Preenche o formulário
        try:
            print("🔍 Preenchendo formulário...")
            campo_messages = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.NAME, "count"))
            )
            campo_messages.clear()
            campo_messages.send_keys(str(quantidade_mensagens))
            
            botao_get_messages = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="submit" and @value="Get Message(s)"]'))
            )
            botao_get_messages.click()
            print("✅ Mensagens solicitadas")
        except Exception as e:
            print(f"❌ Erro ao preencher formulário: {e}")
            voltar_para_queues(driver)
            return []
        
        # Aguarda as mensagens carregarem
        print("⏳ Aguardando mensagens carregarem...")
        time.sleep(1)
        
        # BUSCA CORRETA: Dentro da div#msg-wrapper
        excecoes = []
        try:
            print("🔍 Procurando div#msg-wrapper...")
            
            # Aguarda o msg-wrapper aparecer
            msg_wrapper = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "msg-wrapper"))
            )
            print("✅ msg-wrapper encontrado!")
            
            # Busca as caixas de mensagem dentro do msg-wrapper
            message_boxes = msg_wrapper.find_elements(By.CSS_SELECTOR, "div.box")
            print(f"📦 Encontradas {len(message_boxes)} caixas de mensagem")
            
            if len(message_boxes) == 0:
                print("⚠️ Nenhuma caixa de mensagem encontrada dentro do msg-wrapper")
            else:
                for i, box in enumerate(message_boxes):
                    try:
                        print(f"📋 Processando caixa {i+1}/{len(message_boxes)}")
                        excecoes_box = extrair_excecoes_de_message_box(box)
                        excecoes.extend(excecoes_box)
                        print(f"✅ Extraídas {len(excecoes_box)} exceções da caixa {i+1}")
                    except Exception as e:
                        print(f"⚠️ Erro ao processar caixa {i+1}: {e}")
                        continue
                        
        except Exception as e:
            print(f"⚠️ Erro ao buscar msg-wrapper: {e}")
        
        # Volta para a página de queues
        voltar_para_queues(driver)
        
        print(f"✅ Extraídas {len(excecoes)} exceções da fila {nome_fila}")
        return excecoes
        
    except Exception as e:
        print(f"❌ Erro geral ao extrair exceções da fila {nome_fila}: {e}")
        try:
            voltar_para_queues(driver)
        except:
            pass
        return []

def processar_linha_fila(row, filas_encontradas, filas_com_problemas, queue_names):
    """Processa uma linha da tabela de filas - APENAS COLETA, NÃO EXTRAI EXCEÇÕES"""
    try:
        cols = row.find_elements(By.TAG_NAME, "td")
        if len(cols) < 6:
            return

        link = cols[1].find_elements(By.TAG_NAME, "a")
        if link:
            nome_fila = link[0].text.strip()
            if nome_fila in queue_names:
                filas_encontradas.add(nome_fila)
                valor_fila_ready = cols[5].text.strip()  # TOTAL
                valor_fila_total = cols[7].text.strip()  # READY
                quantidade_ready = int(valor_fila_ready)
                quantidade_total = int(valor_fila_total)
                quantidade = max(quantidade_ready, quantidade_total)

                if quantidade > 0:
                    
                    print(f"⚠️  PROBLEMA DETECTADO: {nome_fila} tem {quantidade} mensagens")
                    # Apenas salva os dados, não extrai exceções ainda
                    filas_com_problemas.append({
                        'nome': nome_fila,
                        'quantidade': quantidade
                    })
                else:
                    print(f"[OK] Fila vazia: {nome_fila}: {quantidade}")
    except Exception as e:
        print(f"❌ Erro ao processar linha: {e}")

def extrair_excecoes_todas_filas(driver, filas_com_problemas):
    """Extrai exceções de todas as filas com problemas"""
    print(f"\n🔍 INICIANDO EXTRAÇÃO DE EXCEÇÕES DE {len(filas_com_problemas)} FILAS...")
    filas_com_detalhes = []
    
    for i, fila_info in enumerate(filas_com_problemas, 1):
        nome_fila = fila_info['nome']
        quantidade = fila_info['quantidade']
        
        print(f"\n📋 [{i}/{len(filas_com_problemas)}] Processando fila: {nome_fila}")
        
        # Extrai as exceções desta fila específica
        excecoes = extrair_excecoes_fila(driver, nome_fila, quantidade)
        
        # Monta o texto resumido da fila - CONTABILIZA OCORRÊNCIAS DE CADA EXCEÇÃO
        fila_texto = f"{nome_fila}: {quantidade} mensagens"
        if excecoes:
            # Conta ocorrências de cada tipo de exceção
            contador_excecoes = {}
            for exc in excecoes:
                if exc in contador_excecoes:
                    contador_excecoes[exc] += 1
                else:
                    contador_excecoes[exc] = 1
            
            # Ordena por nome da exceção
            excecoes_ordenadas = sorted(contador_excecoes.items())
            total_excecoes = len(excecoes)
            tipos_unicos = len(contador_excecoes)
            
            fila_texto += f"\nExceções: {total_excecoes} total, {tipos_unicos} tipo(s) diferentes:"
            for j, (exc, count) in enumerate(excecoes_ordenadas, 1):
                fila_texto += f"\n  {j}. {exc} ({count}x)"
        else:
            fila_texto += "\n  (Não foi possível extrair exceções)"
        
        filas_com_detalhes.append(fila_texto)
        
        # Aguarda um pouco entre filas para não sobrecarregar
        time.sleep(1)
    
    print(f"\n✅ EXTRAÇÃO COMPLETA! Processadas {len(filas_com_detalhes)} filas com problemas.")
    return filas_com_detalhes

def verificar_fila(driver, queue_names, intervalo_minutos):
    """Função principal de verificação das filas"""
    import ctypes
    
    try:        
        print("\n🔍 ETAPA 1: COLETANDO FILAS COM PROBLEMAS...")
        
        # Verifica se a página está acessível
        try:
            current_url = driver.current_url
            if "message-broker.totvs.app" not in current_url:
                raise Exception("Não está na página do RabbitMQ")
        except Exception as e:
            raise Exception(f"Problema de conectividade: {e}")
        # Verifica se consegue encontrar a tabela
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, "table.list tbody tr")
            if len(rows) == 0:
                raise Exception("Tabela de filas não encontrada ou vazia")
        except Exception as e:
            raise Exception(f"Erro ao acessar tabela de filas: {e}")
        
        filas_encontradas = set()
        filas_com_problemas = []
        
        print(f"🔍 Encontradas {len(rows)} linhas na tabela")
        
        # ETAPA 1: Coleta apenas as filas com problemas
        for i, row in enumerate(rows):
            try:
                processar_linha_fila(row, filas_encontradas, filas_com_problemas, queue_names)
            except Exception as e:
                print(f"⚠️ Erro ao processar linha {i}: {e}")
                continue
                
        # Verifica filas não encontradas
        filas_nao_encontradas = []
        for fila in queue_names:
            if fila not in filas_encontradas:
                filas_nao_encontradas.append(fila)
                print(f"❌ Fila não encontrada: {fila}")
        
        print("\n📊 RESUMO DA COLETA:")
        print(f"✅ Filas encontradas: {len(filas_encontradas)}")
        print(f"⚠️ Filas com problemas: {len(filas_com_problemas)}")
        print(f"❌ Filas não encontradas: {len(filas_nao_encontradas)}")

        # ETAPA 2: Se há filas com problemas, extrai as exceções
        if filas_com_problemas:
            print("\n🔍 ETAPA 2: EXTRAINDO EXCEÇÕES DE TODAS AS FILAS...")
            filas_com_detalhes = extrair_excecoes_todas_filas(driver, filas_com_problemas)
            
            # ETAPA 3: Mostra o alerta final
            print("\n🚨 ETAPA 3: EXIBINDO ALERTA FINAL...")
            total_filas_problemas = len(filas_com_detalhes)
            
            # Adiciona timestamp ao alerta
            agora = datetime.now()
            timestamp_formatado = agora.strftime("%d/%m/%Y às %H:%M:%S")
            
            mensagem_completa = f"ALERTA: {total_filas_problemas} fila(s) com mensagens!\n\n"
            mensagem_completa += "\n" + "="*35 + "\n"
            mensagem_completa += "\n\n".join(filas_com_detalhes)
            mensagem_completa += f"\n\n⏰ Verificação realizada em: {timestamp_formatado}"
            
            # POPUP CRÍTICO - Principal funcionalidade do sistema!
            popup(mensagem_completa, "⚠️ ALERTA RabbitMQ - Filas com Problemas!")
            print(f"\n🔄 Monitorando a cada {intervalo_minutos} minutos...")
            print("🛑 Use Ctrl+C para encerrar.")
        else:
            print("✅ Todas as filas monitoradas estão vazias!")
        
        # Registra data e hora da última verificação
        agora = datetime.now()
        timestamp_formatado = agora.strftime("%d/%m/%Y às %H:%M:%S")
        print(f"\n⏰ Última verificação: {timestamp_formatado}")
            
    except Exception as e:
        print(f"❌ Erro geral na verificação: {e}")
        
        # Adiciona timestamp ao erro
        agora = datetime.now()
        timestamp_formatado = agora.strftime("%d/%m/%Y às %H:%M:%S")
        
        # Classifica o tipo de erro e mostra alerta específico
        erro_str = str(e).lower()
        
        if "conectividade" in erro_str or "connection" in erro_str or "timeout" in erro_str:
            titulo_erro = "❌ Erro de Conexão - RabbitMQ"
            tipo_erro = "PROBLEMA DE CONEXÃO"
            mensagem_erro = f"Não foi possível conectar ao RabbitMQ:\n\n{e}\n\n⏰ Tentativa em: {timestamp_formatado}\n\n🔄 O monitoramento continuará tentando na próxima verificação."
        elif "tabela" in erro_str or "filas não encontrada" in erro_str:
            titulo_erro = "❌ Erro de Interface - RabbitMQ"
            tipo_erro = "PROBLEMA NA INTERFACE"
            mensagem_erro = f"Interface do RabbitMQ não carregou corretamente:\n\n{e}\n\n⏰ Tentativa em: {timestamp_formatado}\n\n🔄 O monitoramento continuará tentando na próxima verificação."
        else:
            titulo_erro = "❌ Erro Geral - RabbitMQ"
            tipo_erro = "ERRO INESPERADO"
            mensagem_erro = f"Erro inesperado durante a verificação:\n\n{e}\n\n⏰ Tentativa em: {timestamp_formatado}\n\n🔄 O monitoramento continuará tentando na próxima verificação."
        
        print(f"\n🚨 {tipo_erro} DETECTADO!")
        print(f"📄 Detalhes: {e}")
        print(f"⏰ Horário: {timestamp_formatado}")
        
        # POPUP CRÍTICO - Mostra alerta para erros críticos
        popup(mensagem_erro, titulo_erro)
        
        # Tenta recuperar a conexão
        try:
            print("🔄 Tentando recuperar conexão...")
            driver.get("https://message-broker.totvs.app/#/queues")
            time.sleep(1)
            print("✅ Conexão recuperada!")
        except Exception as recovery_error:
            print(f"❌ Falha na recuperação: {recovery_error}")
            pass
