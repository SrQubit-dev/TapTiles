import sys
import os
from icoextract import IconExtractor, IconExtractorError
from PIL import Image
import pylnk3
import win32com.client
from pathlib import Path
import configparser

def get_icon(exe_path, png_path):
    if exe_path.endswith(".lnk"):
        exe_path = str(get_exe_from_lnk(exe_path))
        print("Extraído desde .lnk:", exe_path)
    
    elif exe_path.endswith(".url"):
        try:
            exe_path = str(get_exe_from_url(exe_path))
            print("Extraído desde .url:", exe_path)
        except Exception as e:
            print(f"No se pudo extraer ícono desde .url: {e}")
            return None

    app_name = Path(exe_path).stem
    print("appname:", app_name)

    png_path = os.path.join(png_path, f"{app_name}.png")

    
    try:
        if not os.path.isfile(png_path):
            if exe_path.endswith(".ico") and os.path.isfile(exe_path):
                # Si ya es un ícono, solo conviértelo
                with Image.open(exe_path) as img:
                    img.save(png_path)
            else:
                ico_path = png_path + ".temp.ico"
                extractor = IconExtractor(exe_path)
                extractor.export_icon(ico_path, num=0)

                with Image.open(ico_path) as img:
                    img.save(png_path)
                os.remove(ico_path)

        print(f"Ícono guardado en: {png_path}")
        return png_path
    except IconExtractorError as e:
        print(f"No se pudieron extraer íconos: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def get_exe_from_url(url_path):
    """
    Extrae la ruta del ícono desde un archivo .url
    """
    config = configparser.ConfigParser()
    config.read(url_path, encoding="utf-8")

    try:
        icon_path = config["InternetShortcut"]["IconFile"]
        return icon_path
    except KeyError:
        raise ValueError(f"No se pudo encontrar 'IconFile' en {url_path}")

def get_exe_from_lnk(desde_lnk):
    shell = win32com.client.Dispatch("WScript.Shell")
    acceso_directo = shell.CreateShortcut(str(desde_lnk))
    ruta_objetivo = acceso_directo.TargetPath
    return ruta_objetivo