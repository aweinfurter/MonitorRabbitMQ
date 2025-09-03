# 🚨 Sistema de Alertas - MonitorRabbitMQ

## Como Funcionam os Alertas

O **MonitorRabbitMQ** possui um sistema robusto de alertas que garante que você seja notificado imediatamente quando há problemas nas filas, mesmo quando não está olhando para a tela.

### 🎯 Tipos de Alertas

#### 1. **Alerta de Filas com Problemas**
- **Quando aparece**: Quando uma ou mais filas monitoradas contêm mensagens
- **Conteúdo**: Lista detalhada das filas problemáticas com quantidade de mensagens
- **Exemplo**:
```
⚠️ ALERTA RabbitMQ - Filas com Problemas!

ALERTA: 3 fila(s) com mensagens!

===================================

🔴 wms-selecao-estoque-errors: 15 mensagens
🔴 wms-separacao-errors: 8 mensagens  
🔴 wms-picking-errors: 3 mensagens

⏰ Verificação realizada em: 03/09/2025 às 14:30:15
```

#### 2. **Alertas de Erro do Sistema**
- **Quando aparece**: Falhas de conexão, problemas de interface, etc.
- **Conteúdo**: Detalhes técnicos do erro e ações de recuperação
- **Tipos**:
  - ❌ Erro de Conexão
  - ❌ Erro de Interface  
  - ❌ Erro Inesperado

### 🖥️ Comportamento por Sistema Operacional

#### **Windows**
- **Popup nativo** usando MessageBox do Windows
- **Aparência**: Janela de diálogo padrão do Windows
- **Som**: Som de alerta padrão do sistema
- **Posição**: Centro da tela
- **Sempre visível**: Fica por cima de outras janelas

#### **Linux**
- **Múltiplas opções** (em ordem de preferência):
  1. **Zenity**: Diálogo gráfico padrão
  2. **KDialog**: Para ambientes KDE
  3. **Notify-Send**: Notificação na área de trabalho
  4. **Console**: Fallback para terminal
- **Instalação automática**: O sistema tenta diferentes métodos

#### **macOS**
- **AppleScript**: Diálogo nativo do macOS
- **Integração total**: Com Central de Notificações
- **Sem instalação adicional**: Funciona imediatamente

### ⚙️ Configuração dos Alertas

#### **Frequência**
- Configurável via interface web
- Padrão: **10 minutos** entre verificações
- Mínimo recomendado: 5 minutos
- Máximo: Ilimitado

#### **Filas Monitoradas**
- Selecione específicamente quais filas alertar
- Suporte a regex para filtros avançados
- Configuração via interface web

#### **Ambientes**
- **Staging**: Ambiente de desenvolvimento
- **Produção**: Ambiente crítico
- URLs configuráveis para cada ambiente

### 🔧 Personalização Avançada

#### **Modificar Mensagens de Alerta**
Edite o arquivo `src/modules/monitor.py`:

```python
# Linha ~431 - Personalizar título do alerta
popup(mensagem_completa, "🚨 MEU ALERTA PERSONALIZADO!")

# Linha ~470 - Personalizar alertas de erro
popup(mensagem_erro, "❌ MEU ALERTA DE ERRO!")
```

#### **Desabilitar Alertas (NÃO RECOMENDADO)**
Para desenvolvedores que queiram apenas logs:

```python
# Em monitor.py, comente as linhas:
# popup(mensagem_completa, "⚠️ ALERTA RabbitMQ - Filas com Problemas!")
# popup(mensagem_erro, titulo_erro)
```

### 📱 Testando os Alertas

#### **Teste Manual**
1. Configure uma fila com mensagens de erro no RabbitMQ
2. Inicie o monitoramento
3. Aguarde o intervalo configurado
4. O popup deve aparecer automaticamente

#### **Teste de Conectividade**
1. Desconecte da internet
2. O sistema detectará erro de conexão
3. Popup de erro aparecerá
4. Reconecte para testar recuperação

### 🚨 Importância dos Alertas

> **CRÍTICO**: Os alertas são a funcionalidade PRINCIPAL do sistema!
> 
> - **Sem alertas**: Problemas passam despercebidos
> - **Com alertas**: Ação imediata em problemas críticos
> - **Resultado**: Redução drástica no tempo de resposta

### 💡 Dicas de Uso

1. **Mantenha o sistema rodando**: Deixe em segundo plano
2. **Configure corretamente**: Teste todos os alertas
3. **Monitore logs**: Interface web para detalhes
4. **Não ignore alertas**: Aja imediatamente
5. **Teste regularmente**: Verifique se está funcionando

### 🔍 Solução de Problemas com Alertas

#### **Windows - Alertas não aparecem**
```bash
# Instale pywin32
pip install pywin32

# Ou execute como administrador
```

#### **Linux - Sem popups gráficos**
```bash
# Instale zenity ou kdialog
sudo apt-get install zenity

# Verifique variável DISPLAY
echo $DISPLAY
```

#### **macOS - Permissões negadas**
```bash
# Permita acesso à automação no AppleScript
# Sistema > Segurança > Privacidade > Automação
```

---

**🎯 Lembre-se**: Os alertas são sua primeira linha de defesa contra problemas críticos no RabbitMQ!
