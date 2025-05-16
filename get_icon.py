import sys
import os
from icoextract import IconExtractor, IconExtractorError
from PIL import Image , ImageFilter , ImageOps
import win32com.client
from pathlib import Path
import numpy as np
import pygame
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
                    img = img.resize((64,64))
                    img.save(png_path)
            else:
                ico_path = png_path + ".temp.ico"
                extractor = IconExtractor(exe_path)
                extractor.export_icon(ico_path, num=0)

                with Image.open(ico_path) as img:
                    img = img.resize((64,64))
                    img.save(png_path)
                os.remove(ico_path)

        print(f"Ícono guardado en: {png_path}")
        return png_path
    except IconExtractorError as e:
        print(f"No se pudieron extraer íconos: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

def round_alpha(img,threshold):
    data = np.array(img)
    data[:, :, 3] = np.where(data[:, :, 3] >= threshold, 255, 0)
    clean_img = Image.fromarray(data, mode="RGBA")
    return clean_img

def add_shadow(image, offset=(5, 5), background_color=(0, 0, 0, 0),shadow_color=(0, 0, 0, 200), blur_radius=0 ):
    # Crear una imagen negra con la misma forma
    shadow = Image.new("RGBA", image.size, shadow_color)

    # Crear máscara a partir del canal alfa de la imagen original
    mask = image.split()[3]

    # Aplicar la máscara al color de sombra
    adjusted_mask = mask.point(lambda p: p * (shadow_color[3] / 255))
    shadow.putalpha(adjusted_mask)

    # Crear un lienzo más grande para la sombra + original
    total_size = (image.width + abs(offset[0]) + blur_radius * 2,
                  image.height + abs(offset[1]) + blur_radius * 2)
    final_image = Image.new("RGBA", total_size, background_color)

    # Posición de la sombra
    shadow_position = (blur_radius + max(offset[0], 0),
                       blur_radius + max(offset[1], 0))
    
    # Aplicar desenfoque
    blurred_shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))

    # Pegar sombra
    final_image.paste(blurred_shadow, shadow_position, blurred_shadow)

    # Posición de la imagen original
    image_position = (blur_radius - min(offset[0], 0),
                      blur_radius - min(offset[1], 0))

    # Pegar imagen original encima
    final_image.paste(image, image_position, image)

    return final_image

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


#blur surface with correct alpha----------

def surface_to_array_alpha(surface):
    """Convierte surface en array (RGBA)"""
    arr = pygame.surfarray.pixels3d(surface).astype(np.float32)
    alpha = pygame.surfarray.pixels_alpha(surface).astype(np.float32)
    alpha = alpha[:, :, None] / 255.0
    rgba = np.dstack((arr, alpha * 255))
    return rgba, alpha

def array_to_surface(rgba):
    """Convierte array RGBA a Surface"""
    rgb = rgba[..., :3].astype(np.uint8)
    alpha = rgba[..., 3].astype(np.uint8)
    surface = pygame.Surface((rgb.shape[0], rgb.shape[1]), pygame.SRCALPHA)
    pygame.surfarray.blit_array(surface, rgb)
    pygame.surfarray.pixels_alpha(surface)[:, :] = alpha
    return surface

def premultiply_alpha(rgba, alpha):
    premultiplied = rgba.copy()
    premultiplied[..., :3] *= alpha  # RGB * alpha
    return premultiplied

def unpremultiply_alpha(rgba, alpha_blurred):
    result = np.zeros_like(rgba)
    with np.errstate(divide='ignore', invalid='ignore'):
        result[..., :3] = np.where(alpha_blurred != 0, rgba[..., :3] / alpha_blurred, 0)
    result[..., 3] = alpha_blurred[..., 0] * 255
    return np.clip(result, 0, 255)

def blur_surface_pygame(surface, radius=3):
    # Paso 1: convertir a array y pre-multiplicar alpha
    rgba, alpha = surface_to_array_alpha(surface)
    premult = premultiply_alpha(rgba, alpha)
    premult_surface = array_to_surface(np.dstack((premult[..., :3], np.full_like(alpha, 255))))

    # Paso 2: aplicar blur a RGB (pre-multiplicado)
    blurred_rgb_surf = pygame.transform.box_blur(premult_surface, radius)
    blurred_rgb = pygame.surfarray.array3d(blurred_rgb_surf).astype(np.float32)

    # Paso 3: blur al alpha por separado
    alpha_surface = array_to_surface(np.dstack((alpha * 255, alpha * 255, alpha * 255, alpha * 255)))
    blurred_alpha_surf = pygame.transform.box_blur(alpha_surface, radius)
    blurred_alpha = pygame.surfarray.pixels_alpha(blurred_alpha_surf).astype(np.float32) / 255.0
    blurred_alpha = blurred_alpha[:, :, None]

    # Paso 4: un-premultiply
    rgba_blurred = np.dstack((blurred_rgb, blurred_alpha * 255))
    final = unpremultiply_alpha(rgba_blurred, blurred_alpha)

    return array_to_surface(final)