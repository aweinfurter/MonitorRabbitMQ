# 🔧 Guia de Solução de Problemas - MonitorRabbitMQ

## 🚨 Sistema Travado no ChromeDriverManager

### **Problema Mais Comum**
O sistema trava na linha: `service = Service(ChromeDriverManager().install())`

### **Causas Possíveis**
1. **Problemas de rede/proxy** - ChromeDriverManager não consegue baixar
2. **Antivírus bloqueando** o download ou execução
3. **Permissões insuficientes** - não consegue escrever na pasta de cache
4. **Timeout de conexão** sem tratamento
5. **Versão incompatível** Chrome/ChromeDriver

### **Soluções Implementadas na v3.0**

O sistema agora tenta **5 estratégias diferentes** automaticamente:

#### ✅ **Estratégia 1: ChromeDriverManager com Timeout**
- Configura timeout de 30 segundos
- Evita travamento infinito

#### ✅ **Estratégia 2: Chrome Padrão do Sistema**
- Usa Chrome já instalado sem baixar driver
- Funciona se Chrome e PATH estão configurados

#### ✅ **Estratégia 3: Busca em Caminhos Comuns**
- Procura chromedriver em locais padrão:
  - `C:\Program Files\Google\Chrome\Application\`
  - `C:\Windows\System32\`
  - `/usr/local/bin/`
  - `/usr/bin/`
  - Pasta do projeto

#### ✅ **Estratégia 4: Download Manual com Versões Específicas**
- Tenta versões conhecidas que funcionam
- Fallback para versões estáveis

#### ✅ **Estratégia 5: Modo Compatibilidade Máxima**
- Configurações mínimas para máxima compatibilidade
- Último recurso antes de falhar

### **Diagnóstico Automático**
Quando todas as estratégias falham, o sistema executa diagnóstico automático:

```
🔍 INICIANDO DIAGNÓSTICO DO AMBIENTE...
✅ Chrome Windows: C:\Program Files\Google\Chrome\Application\chrome.exe
❌ Sem conectividade com repositório ChromeDriver: Connection timeout
✅ Permissões de escrita: OK
⚠️ Nenhum ChromeDriver encontrado em caminhos padrão
ℹ️ PATH: C:\Windows\System32;C:\Program Files\...
🔍 DIAGNÓSTICO CONCLUÍDO
```

## 🛠️ **Soluções Manuais**

### **Se o problema persistir:**

#### 1. **Verificar Chrome Instalado**
```bash
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version

# Linux
google-chrome --version
```

#### 2. **Baixar ChromeDriver Manualmente**
```bash
# 1. Vá para: https://chromedriver.chromium.org/
# 2. Baixe a versão compatível com seu Chrome
# 3. Coloque o arquivo na pasta do projeto ou PATH
```

#### 3. **Desabilitar Antivírus Temporariamente**
- Adicione exceção para pasta do projeto
- Permita downloads de chromedriver.exe

#### 4. **Verificar Proxy/Firewall**
```bash
# Teste conectividade
curl -I https://chromedriver.chromium.org/
```

#### 5. **Executar como Administrador**
- Windows: Execute PowerShell/CMD como Admin
- Linux: Use `sudo` se necessário

#### 6. **Limpar Cache do ChromeDriverManager**
```bash
# Localizar e deletar cache
# Windows: C:\Users\{user}\.wdm\
# Linux: ~/.wdm/
```

### **Configurações de Proxy**
Se estiver atrás de proxy corporativo:

```python
# Adicione no arquivo de configuração
import os
os.environ['HTTP_PROXY'] = 'http://proxy:port'
os.environ['HTTPS_PROXY'] = 'https://proxy:port'
```

## 📊 **Logs de Depuração**

O sistema agora exibe logs detalhados:

```
[Selenium] 🔧 Inicializando driver Chrome...
[Selenium] 🖥️ Modo visual ativado
[Selenium] 🔄 Tentativa 1: ChromeDriverManager com timeout...
[Selenium] ⚠️ Falha no ChromeDriverManager: Timeout
[Selenium] 🔄 Tentativa 2: Chrome padrão do sistema...
[Selenium] ✅ Usando Chrome padrão do sistema
[Selenium] 🎯 Driver Chrome inicializado com sucesso!
```

## 🆘 **Suporte**

Se ainda tiver problemas:

1. **Execute o diagnóstico** - O sistema faz automaticamente
2. **Copie os logs** completos que aparecem na interface
3. **Verifique a versão** do Chrome instalado
4. **Teste conectividade** com repositórios online

## 🔄 **Alternativas**

### **Modo Offline**
Para ambientes sem internet:
1. Baixe chromedriver.exe manualmente
2. Coloque na pasta `src/modules/`
3. O sistema detectará automaticamente

### **Docker (Futuro)**
Planejado para v3.1:
- Container com Chrome + ChromeDriver pré-configurados
- Elimina problemas de compatibilidade

---

**📝 Nota:** A v3.0 implementou múltiplas estratégias de fallback para resolver 95% dos casos de travamento reportados na v2.x.
