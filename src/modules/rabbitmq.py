"""
Módulo do RabbitMQ
Responsável por navegação, monitoramento e extração de dados das filas
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def definir_autorefresh(driver, timeout=30):
    """Define auto-refresh para 30 segundos"""
    try:
        print("⏳ Aguardando dropdown de auto-refresh aparecer...")
        wait = WebDriverWait(driver, timeout)
        select_element = wait.until(EC.presence_of_element_located((By.ID, "update-every")))
        print("✅ Dropdown de auto-refresh encontrado!")
        dropdown = Select(select_element)
        dropdown.select_by_value("30000")
        print("✅ Auto-refresh definido para 30 segundos.")
        return True
    except Exception as e:
        print(f"❌ Erro ao esperar dropdown de auto-refresh: {e}")
        return False

def navegar_para_queues(driver, timeout=30):
    """Navega automaticamente para a aba de Queues após o login"""
    try:
        print("🔍 Detectando aba 'Queues'...")
        
        # Aguarda até aparecer o menu (máximo 30 segundos)
        wait = WebDriverWait(driver, timeout)
        
        # Primeiro tenta encontrar o link dentro do menu
        queues_link = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#menu #queues-and-streams a[href='#/queues']"))
        )
        
        print("✅ Aba 'Queues' encontrada!")
        print("🖱️ Clicando na aba 'Queues'...")
        
        # Clica na aba de queues
        queues_link.click()
        
        print("✅ Navegação para 'Queues' concluída!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao navegar para Queues: {e}")
        print("Tente clicar manualmente na aba 'Queues'.")
        return False

def aplicar_filtro_regex(driver, regex):
    """Aplica filtro regex na interface do RabbitMQ"""
    try:
        print(f"🔍 Aplicando filtro regex: {regex}")
        
        # Campo de filtro
        input_filtro = driver.find_element(By.ID, "queues-name")
        input_filtro.send_keys(regex)
        input_filtro.send_keys(Keys.RETURN)
        
        # Aguarda um pouco para o campo processar
        time.sleep(1)
        
        # Checkbox de regex
        checkbox = driver.find_element(By.ID, "queues-filter-regex-mode")
        if not checkbox.is_selected():
            checkbox.click()
            print("✅ Checkbox de regex ativado.")
        else:
            print("✅ Checkbox de regex já estava ativado.")
            
        # Aguarda o filtro ser aplicado
        time.sleep(1)
        print("✅ Filtro aplicado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao aplicar filtro: {e}")
        print("Continuando sem filtro...")

def voltar_para_queues(driver):
    """Volta para a página de queues com múltiplas tentativas"""
    print("🔙 Voltando para a página de filas...")
    
    # Tentativa 1: Clica no link do menu
    try:
        queues_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#menu #queues-and-streams a[href='#/queues']"))
        )
        queues_link.click()
        print("✅ Voltou via link do menu")
        return True
    except Exception as e:
        print(f"⚠️ Erro ao voltar via menu: {e}")
    
    # Tentativa 2: Navega diretamente pela URL
    try:
        print("🔄 Tentando voltar via URL direta...")
        driver.get("https://message-broker.totvs.app/#/queues")
        time.sleep(5)
        print("✅ Voltou via URL direta")
        return True
    except Exception as e:
        print(f"❌ Erro ao voltar via URL: {e}")
        return False

def extrair_exception_de_celula(exc_row):
    """Extrai apenas o nome da exceção (com limite de caracteres)"""
    try:
        abbr_tag = exc_row.find_element(By.CSS_SELECTOR, "td abbr")
        
        # CORREÇÃO: Pega o TEXT da tag, não o title
        # O conteúdo está dentro da tag: <abbr>Cannot find one "separacao_estoque".</abbr>
        exception_text = abbr_tag.text.strip()
        
        # Se o text estiver vazio, aí sim tenta o title como fallback
        if not exception_text:
            exception_text = abbr_tag.get_attribute("title") or ""
        
        if exception_text:
            # Verifica se é erro de bash/reprocessamento
            if "Batch update returned unexpected row count from update" in exception_text.lower() or exception_text.strip().startswith("Batch"):
                return "Erro de reprocessamento de fila"
            
            # Se contém pacote Java (com pontos), pega apenas a última parte
            if '.' in exception_text and any(java_keyword in exception_text.lower() for java_keyword in ['exception', 'error', 'com.', 'org.', 'java.']):
                # Exemplo: com.totvs.sl.wms.query.estoque.exception.WMSEstoqueNaoEncontradoException
                nome_exception = exception_text.split('.')[-1].strip()
                # Limita a 80 caracteres
                if len(nome_exception) > 80:
                    nome_exception = nome_exception[:77] + "..."
            else:
                # Para outros tipos de erro (não Java), pega a primeira linha
                linhas = exception_text.strip().split('\n')
                nome_exception = linhas[0].strip()
                
                # Remove aspas se existirem no final
                if nome_exception.endswith('.'):
                    nome_exception = nome_exception[:-1]
                
                # Limita a 100 caracteres para exceções não-Java
                if len(nome_exception) > 100:
                    nome_exception = nome_exception[:97] + "..."
            
            return nome_exception if nome_exception else None
        
        return None
    except Exception:
        return None

def processar_headers_table(headers_mini_table):
    """Processa a tabela de headers para encontrar exceções"""
    excecoes = []
    try:
        exception_rows = headers_mini_table.find_elements(By.XPATH, ".//tr[th[text()='exception:']]")
        for exc_row in exception_rows:
            exception_text = extrair_exception_de_celula(exc_row)
            if exception_text:
                excecoes.append(exception_text)
    except Exception:
        pass
    return excecoes

def extrair_excecoes_de_message_box(box):
    """Extrai exceções de uma caixa de mensagem seguindo a estrutura correta"""
    excecoes = []
    try:
        # Busca a table.facts dentro da box
        facts_table = box.find_element(By.CSS_SELECTOR, "table.facts")
        
        # Busca todas as linhas com th="properties"
        properties_rows = facts_table.find_elements(By.XPATH, ".//tr[th[contains(text(), 'properties') or contains(text(), 'Properties')]]")
        
        for prop_row in properties_rows:
            try:
                # Busca a table.mini dentro da célula td
                mini_table = prop_row.find_element(By.CSS_SELECTOR, "td table.mini")
                
                # Busca linhas com th="headers:"
                headers_rows = mini_table.find_elements(By.XPATH, ".//tr[th[contains(text(), 'headers')]]")
                
                for header_row in headers_rows:
                    try:
                        # Busca a segunda table.mini (headers)
                        headers_mini_table = header_row.find_element(By.CSS_SELECTOR, "td table.mini")
                        
                        # Busca linhas com th="exception:"
                        exception_rows = headers_mini_table.find_elements(By.XPATH, ".//tr[th[contains(text(), 'exception')]]")
                        
                        for exc_row in exception_rows:
                            exception_text = extrair_exception_de_celula(exc_row)
                            if exception_text:
                                excecoes.append(exception_text)
                                
                    except Exception:
                        continue
            except Exception:
                continue
                
    except Exception:
        pass
    return excecoes
