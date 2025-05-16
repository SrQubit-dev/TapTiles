import winreg

def agregar_contexto_escritorio(nombre, comando):
    clave = fr"Software\Classes\Directory\Background\shell\{nombre}\command"

    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, clave)
        winreg.SetValue(key, '', winreg.REG_SZ, comando)

        winreg.CloseKey(key)
        print(f"✔️ '{nombre}' añadido al menú contextual del escritorio.")
    except Exception as e:
        print("❌ Error al escribir en el registro:", e)

def eliminar_contexto_escritorio(nombre):
    try:
        base_path = fr"Software\Classes\Directory\Background\shell\{nombre}"
        command_path = base_path + r"\command"

        # Primero elimina la subclave "command"
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, command_path)

        # Luego elimina la clave principal
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, base_path)

        print(f"🗑️ Clave '{nombre}' eliminada del menú contextual.")
    except FileNotFoundError:
        print(f"⚠️ La clave '{nombre}' no existe.")
    except PermissionError:
        print("❌ Acceso denegado. Ejecuta como administrador si estás usando HKEY_LOCAL_MACHINE.")
    except Exception as e:
        print("❌ Error inesperado:", e)

eliminar_contexto_escritorio("AbrirConMiApp")
# # Ruta al programa que quieres lanzar, %V representa la carpeta actual
# comando = r'"C:\games\AstroPlay Pro.exe" "%V"'
# agregar_contexto_escritorio("Abrir AstroPlay", comando)