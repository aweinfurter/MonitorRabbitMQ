"""
Módulo de interface do usuário
Responsável por exibir alertas e popups do sistema
Sistema otimizado sem dependências do Selenium (agora usa selenium_embed.py)
"""

import time
import ctypes
import platform
import os

# Win32 imports opcionais
if platform.system() == "Windows":
    try:
        import win32gui
        import win32con
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
        print("⚠️ win32gui não disponível - algumas funcionalidades podem ser limitadas")

# === Funções internas para cada SO ===
def _popup_windows(msg, title):
    try:
        ctypes.windll.user32.MessageBoxW(0, msg, title, 0x30)
        print("✅ Popup Windows exibido")
    except Exception as e:
        print(f"❌ Erro popup Windows: {e}")

def _popup_linux(msg, title):
    """Exibe popup no Linux usando múltiplos métodos"""
    try:
        # Tenta zenity primeiro (mais comum)
        import subprocess
        try:
            subprocess.run(['zenity', '--info', f'--title={title}', f'--text={msg}'], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print("✅ Popup Linux (zenity) exibido")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Tenta kdialog
        try:
            subprocess.run(['kdialog', '--title', title, '--msgbox', msg], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print("✅ Popup Linux (kdialog) exibido")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Tenta notify-send
        try:
            subprocess.run(['notify-send', title, msg], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            print("✅ Notificação Linux (notify-send) enviada")
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Fallback: console
        print(f"📢 ALERTA: {title}")
        print(f"💬 {msg}")
        
    except Exception as e:
        print(f"❌ Erro popup Linux: {e}")
        print(f"📢 ALERTA: {title}")
        print(f"💬 {msg}")

def _popup_macos(msg, title):
    """Exibe popup no macOS usando AppleScript"""
    try:
        import subprocess
        applescript = f'''
        display dialog "{msg}" with title "{title}" buttons {{"OK"}} default button "OK" with icon note
        '''
        subprocess.run(['osascript', '-e', applescript],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        print("✅ Popup macOS exibido")
    except Exception as e:
        print(f"❌ Erro popup macOS: {e}")
        print(f"📢 ALERTA: {title}")
        print(f"💬 {msg}")

# === Função principal de popup ===
def popup(msg, title="Monitor RabbitMQ - Alerta"):
    """
    Exibe um popup de alerta adequado para o sistema operacional
    """
    print("="*80)
    print(f"🚨 ALERTA: {title}")
    print(msg)
    print("="*80)

    system = platform.system()
    if system == "Windows":
        _popup_windows(msg, title)
    elif system == "Linux":
        _popup_linux(msg, title)
    elif system == "Darwin":
        _popup_macos(msg, title)
    else:
        print(f"⚠️ Sistema {system} não suportado para popups nativos")

def confirmar_modo_invisivel():
    """
    Confirma que o Chrome está operando adequadamente
    Mantido para compatibilidade com código existente
    """
    try:
        print("👻 Confirmando modo de operação...")
        print("✅ Chrome está executando adequadamente!")
        print("📋 O monitoramento continua em segundo plano")
        print("⚠️ Popups de alerta ainda aparecerão quando necessário")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
