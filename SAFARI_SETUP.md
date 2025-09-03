# 🦆 Configuração do Safari para macOS

## 📋 Resumo das Mudanças

O sistema foi atualizado para detectar automaticamente quando está sendo executado no macOS e usar o Safari como navegador padrão em vez do Chrome. Isso garante melhor compatibilidade com o sistema operacional da Apple.

## 🔍 Detecção Automática

O sistema agora:
- ✅ Detecta automaticamente o sistema operacional
- ✅ Usa Safari no macOS automaticamente
- ✅ Mantém Chrome como padrão no Windows/Linux
- ✅ Informa ao usuário qual navegador será usado
- ✅ Fornece instruções de configuração quando necessário

## ⚙️ Configuração Necessária no macOS

### 1. Habilitar Menu Desenvolver no Safari

1. Abra o **Safari**
2. Vá em **Safari > Preferências** (ou cmd+,)
3. Clique na aba **Avançado**
4. Marque a opção **"Mostrar menu Desenvolver na barra de menus"**

### 2. Permitir Automação Remota

1. No Safari, vá em **Desenvolver > Permitir Automação Remota**
2. Certifique-se de que esta opção esteja **marcada**

### 3. Configurações de Segurança (se necessário)

Se ainda houver problemas, você pode precisar:

1. Ir em **Preferências do Sistema > Segurança e Privacidade**
2. Na aba **Privacidade**, procurar por **Automação**
3. Permitir que o terminal/aplicação controle o Safari

## 🚀 Como Usar

O sistema funcionará automaticamente após a configuração:

```bash
# Execute normalmente como antes
python src/run_web.py
```

## 📝 Diferenças entre Navegadores

| Recurso | Chrome | Safari |
|---------|--------|--------|
| Modo Headless | ✅ Sim | ❌ Não |
| Configuração Manual | ❌ Não | ✅ Sim |
| Performance | ⚡ Rápido | 🐌 Moderado |
| Compatibilidade macOS | ⚠️ Boa | ✅ Excelente |
| Screenshots | ✅ Sim | ✅ Sim |

## 🔧 Logs Informativos

O sistema agora exibe logs informativos sobre qual navegador está sendo usado:

```
[Selenium] 🌐 Sistema detectado: macOS
[Selenium] 🔧 Navegador selecionado: Safari
[Selenium] ⚙️ Configuração necessária para Safari:
[Selenium]    • Abra Safari > Preferências > Avançado
[Selenium]    • Marque "Mostrar menu Desenvolver na barra de menus"
[Selenium]    • No menu Desenvolver, marque "Permitir Automação Remota"
```

## ⚠️ Limitações do Safari

- **Não suporta modo headless**: O Safari sempre será executado visualmente
- **Requer configuração manual**: Diferente do Chrome, precisa de configuração prévia
- **Performance**: Pode ser ligeiramente mais lento que o Chrome

## 🧪 Teste da Configuração

Para testar se tudo está funcionando corretamente, você pode usar o método de teste:

```python
from src.modules.selenium_embed import SeleniumEmbedded

# Criar instância
selenium = SeleniumEmbedded()

# Testar navegador
selenium.testar_navegador()
```

## 🆘 Solução de Problemas

### Erro: "Safari cannot be automated"

**Solução**: Verifique se a automação remota está habilitada no menu Desenvolver.

### Erro: "Safari not found"

**Solução**: Certifique-se de que o Safari está instalado (vem por padrão no macOS).

### Erro de permissões

**Solução**: Verifique as configurações de privacidade do sistema.

## 📞 Suporte

Se encontrar problemas:
1. Verifique se seguiu todos os passos de configuração
2. Consulte os logs do sistema para mensagens de erro específicas
3. Entre em contato: andre.weinfurter@totvs.com.br

---

**Nota**: Essas mudanças são totalmente compatíveis com versões anteriores. Usuários do Windows e Linux continuarão usando Chrome normalmente.
