# 🚀 Guia de Instalação Rápida - MonitorRabbitMQ

## Instalação Automática (Recomendada)

```bash
# 1. Clone o repositório
git clone <URL_DO_SEU_REPO>
cd MonitorRabbitMQ

# 2. Execute o setup automático
python setup.py
```

## Instalação Manual

### Windows
```cmd
# 1. Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar sistema
python src\run_web.py
```

### Linux/macOS
```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Executar sistema
python src/run_web.py
```

> **📱 Usuários de macOS**: O sistema detecta automaticamente o macOS e usa o Safari como navegador padrão. Consulte `SAFARI_SETUP.md` para instruções de configuração do Safari.

## Acesso

Após iniciar, acesse: **http://localhost:8083**

## ⚠️ Configuração Especial para macOS

Se você está usando **macOS**, o sistema usará automaticamente o Safari. Para configurar:

1. **Abra o Safari** > Preferências > Avançado
2. **Marque** "Mostrar menu Desenvolver na barra de menus"
3. **No menu Desenvolver**, marque "Permitir Automação Remota"

📖 **Documentação completa**: Consulte `SAFARI_SETUP.md` para informações detalhadas.

## Primeira Configuração

1. **Configure SSO** na tela inicial
2. **Selecione filas** para monitorar
3. **Defina intervalo** de verificação
4. **Inicie monitoramento**

## Suporte

📧 andre.weinfurter@totvs.com.br
📚 Consulte o README.md para documentação completa
