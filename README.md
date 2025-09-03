# 🐰 MonitorRabbitMQ

![Version](https://img.shields.io/badge/version-v3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

Sistema automatizado de monitoramento de filas RabbitMQ com interface web moderna e intuitiva.

## 📋 Descrição

O **MonitorRabbitMQ** é uma ferramenta completa para monitoramento automatizado de filas RabbitMQ, desenvolvida especificamente para ambientes corporativos. Oferece:

- 🌐 **Interface Web Moderna**: Dashboard responsivo e intuitivo
- 🤖 **Automação Completa**: Login SSO automático e navegação inteligente
- 📊 **Monitoramento em Tempo Real**: Verificação contínua das filas configuradas
- � **Alertas Imediatos**: Popups automáticos quando detecta problemas nas filas
- �🔐 **Segurança**: Gerenciamento seguro de credenciais com criptografia
- 📱 **Multi-plataforma**: Funciona em Windows, Linux e macOS
- 🎯 **Configuração Flexível**: Interface web para configuração completa

## 🚀 Funcionalidades

### Monitoramento Automático
- Verificação periódica de filas RabbitMQ
- Detecção automática de problemas e erros
- **🚨 Alertas instantâneos via popup do sistema**
- Relatórios em tempo real via interface web
- Suporte a múltiplos ambientes (Staging/Produção)

### Interface Web
- Dashboard moderno e responsivo
- Configuração completa via interface
- Logs em tempo real
- Screenshots automáticos do navegador
- Controle de modo visual/headless

### Segurança
- Credenciais SSO armazenadas de forma segura
- Criptografia de senhas
- Separação de configurações sensíveis
- Tokens MFA mantidos apenas em memória

### Automação Selenium
- Login SSO automático
- Preenchimento automático de MFA
- Navegação inteligente no RabbitMQ
- Captura automática de dados das filas

### 🚨 Sistema de Alertas Críticos
- **Popups automáticos** quando filas contêm mensagens de erro
- **Notificações nativas do SO** (Windows, Linux, macOS)
- **Alertas em tempo real** - não precisa ficar olhando logs
- **Informações detalhadas** sobre filas problemáticas
- **Múltiplos canais**: Popup + logs + interface web

> 📋 **Veja [ALERTAS.md](ALERTAS.md) para guia completo dos alertas**

## 📦 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Google Chrome/Chromium instalado
- Acesso às URLs do RabbitMQ

### Instalação via Git

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/MonitorRabbitMQ.git
cd MonitorRabbitMQ

# Crie um ambiente virtual (recomendado)
python -m venv venv

# Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### Instalação Manual

```bash
# Instale as dependências principais
pip install Flask>=2.0.0
pip install selenium>=4.0.0
pip install webdriver-manager>=3.8.0
pip install Pillow>=9.0.0
pip install requests>=2.25.0
```

### 🖥️ Compatibilidade Multi-plataforma

O sistema detecta automaticamente seu sistema operacional e usa o navegador mais adequado:

| Sistema | Navegador Padrão | Modo Headless | Configuração |
|---------|------------------|---------------|--------------|
| Windows | Chrome | ✅ Sim | Automática |
| Linux | Chrome | ✅ Sim | Automática |
| macOS | Safari | ❌ Não | Manual* |

> **⚠️ Usuários de macOS**: É necessária configuração manual do Safari. Consulte [`SAFARI_SETUP.md`](SAFARI_SETUP.md) para instruções detalhadas.

## 🎯 Uso

### Inicialização

```bash
# Navegue até a pasta do projeto
cd MonitorRabbitMQ

# Execute o sistema
python src/run_web.py
```

O sistema iniciará automaticamente:
- 🌐 Servidor web na porta `8083`
- 🖥️ Navegador abrirá automaticamente
- 📱 Interface acessível em `http://localhost:8083`

### Primeira Configuração

1. **Acesse a Interface**: O navegador abrirá automaticamente na página de configuração
2. **Configure SSO**: 
   - Usuário SSO
   - Senha SSO (será criptografada automaticamente)
   - Token MFA (opcional)
3. **Configure RabbitMQ**:
   - Usuário RabbitMQ
   - Senha RabbitMQ
   - Ambiente (Staging/Produção)
4. **Selecione Filas**: Escolha quais filas monitorar
5. **Defina Intervalo**: Configure intervalo de verificação (em minutos)
6. **🧪 Teste os Alertas**: Execute `python test_alertas.py` para verificar

### Monitoramento

1. **Inicie Monitoramento**: Clique em "Iniciar Monitoramento Real"
2. **Acompanhe Logs**: Visualize logs em tempo real na interface
3. **Screenshots**: Veja capturas automáticas do navegador
4. **Controles**: 
   - Pause/retome o monitoramento
   - Alterne modo visual/headless
   - Capture screenshots manuais

## 📁 Estrutura do Projeto

```
MonitorRabbitMQ/
├── src/                          # Código fonte principal
│   ├── run_web.py               # Script de inicialização
│   ├── web_app.py               # Aplicação web principal
│   ├── version.py               # Informações de versão
│   ├── modules/                 # Módulos especializados
│   │   ├── config_manager.py    # Gerenciamento de configurações
│   │   ├── config.py            # Interface de configuração
│   │   ├── web_routes.py        # Rotas da aplicação web
│   │   ├── web_logging.py       # Sistema de logs
│   │   ├── selenium_manager.py  # Gerenciamento Selenium
│   │   ├── selenium_embed.py    # Selenium embarcado
│   │   ├── monitoring_engine.py # Motor de monitoramento
│   │   ├── rabbitmq.py          # Integração RabbitMQ
│   │   ├── sso_auth.py          # Autenticação SSO
│   │   ├── ui.py                # Sistema de alertas/popups
│   │   └── monitor.py           # Funções de monitoramento
│   └── templates/               # Templates HTML
│       ├── configuracao.html    # Página de configuração
│       ├── monitoramento.html   # Dashboard de monitoramento
│       └── static/              # Recursos estáticos (CSS/JS)
├── requirements.txt             # Dependências Python
├── README.md                   # Este arquivo
├── ALERTAS.md                  # Guia completo dos alertas
├── test_alertas.py             # Teste do sistema de alertas
└── config.txt                 # Configurações (criado automaticamente)
```

## ⚙️ Configuração Avançada

### Arquivos de Configuração

O sistema utiliza dois arquivos de configuração:

- **`config.txt`**: Configurações gerais (filas, intervalos, etc.)
- **`sso_config.json`**: Credenciais SSO (criptografadas automaticamente)

### Variáveis de Ambiente

```bash
# Porta do servidor web (padrão: 8083)
export MONITOR_PORT=8083

# Modo debug
export MONITOR_DEBUG=false
```

### Configuração de Alertas

**Windows:**
```bash
# Popups nativos automáticos (MessageBox)
# Instale pywin32 para melhor compatibilidade:
pip install pywin32
```

**Linux:**
```bash
# Instale um dos sistemas de notificação:
sudo apt-get install zenity          # Ubuntu/Debian
sudo yum install zenity              # CentOS/RHEL
# OU
sudo apt-get install kdialog         # KDE
# OU 
sudo apt-get install libnotify-bin   # notify-send
```

**macOS:**
```bash
# AppleScript nativo (já incluído no sistema)
# Nenhuma instalação adicional necessária
```

### Personalização de Filas

Edite o arquivo `config.txt` ou use a interface web para:
- Adicionar/remover filas
- Configurar regex de filtros
- Definir ambientes personalizados

## 🔧 Desenvolvimento

### Estrutura Modular

O projeto segue uma arquitetura modular:

- **`web_app.py`**: Orquestração principal
- **`web_routes.py`**: Rotas e endpoints
- **`config_manager.py`**: Gerenciamento seguro de configurações
- **`selenium_manager.py`**: Automação web
- **`monitoring_engine.py`**: Lógica de monitoramento

### Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 🐛 Solução de Problemas

### Problemas Comuns

**Erro de importação de módulos:**
```bash
# Certifique-se de estar no diretório correto
cd MonitorRabbitMQ
python src/run_web.py
```

**Chrome/Chromium não encontrado:**
```bash
# Instale o Google Chrome ou configure o path manualmente
# O webdriver-manager baixará automaticamente o ChromeDriver
```

**Problemas de permissão:**
```bash
# Execute com permissões adequadas
# Windows: Execute como Administrador se necessário
# Linux/macOS: Verifique permissões de execução
```

**Porta já em uso:**
```bash
# Mude a porta no arquivo run_web.py
# Ou pare outros serviços na porta 8083
```

### Logs e Debug

- **Logs Web**: Visualize na interface em tempo real
- **Logs Console**: Execute com `MONITOR_DEBUG=true`
- **Screenshots**: Capturas automáticas para debug visual

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👨‍💻 Autor

**André Weinfurter** - TOTVS  
📧 Email: andre.weinfurter@totvs.com.br

## 🙏 Agradecimentos

- Equipe TOTVS Supply & Logística
- Comunidade Python e Selenium
- Contribuidores do projeto

---

⭐ **Se este projeto foi útil, deixe uma estrela!** ⭐
