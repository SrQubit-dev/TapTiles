import os
import sys
import subprocess
import pygame
import win32api
import win32con
import win32gui
import winreg
import threading

from pygame.locals import *
from OpenGL.GL import *

from acrylic import *
from gl_tools import blit_surface_to_opengl
from get_icon import get_icon, get_exe_from_lnk
from save_load_data import save_folder_data, load_apps_from_folder
from SubMenus import *

# Colores y configuración inicial
fuchsia = (255, 0, 128)
run = True
app_rects, icon_paths, icon_sprites = [], [], []

folder_name = "Default Folder"
bg_color = "0, 255, 255"
border_color = "0, 255, 255"
bg_opacity = 32
show_text = True
use_blur = True

# crear lista de submenus
sub_menus = []

# Leer argumentos de línea de comandos
print(f"args: {sys.argv}")
for i, argument in enumerate(sys.argv):
    if argument == "--CodeName":
        folder_name = sys.argv[i + 1]
    elif argument == "--BgCol":
        bg_color = sys.argv[i + 1]
    elif argument == "--BorderCol":
        border_color = sys.argv[i + 1]
    elif argument == "--Opacity":
        bg_opacity = int(sys.argv[i + 1])
    elif argument == "--NoText":
        show_text = False
    elif argument == "--NoBlur":
        use_blur = False

# Convertir colores a tuplas de enteros
bg_color = [int(c) for c in bg_color.split(",")]
border_color = [int(c) for c in border_color.split(",")]

print("folder_name:", folder_name)
print("bg_color:", bg_color)
print("border_color:", border_color)
print("show_text:", show_text)

# Cargar apps
apps = load_apps_from_folder("data.json", folder_name)

def load_icons_thread():
    global app_rects, icon_paths, icon_sprites, apps
    updated_apps = []

    for i, app in enumerate(apps):
        if app.endswith(".lnk"):
            apps[i] = get_exe_from_lnk(app)
        updated_apps.append(apps[i])

    new_icon_paths = []
    for app in updated_apps:
        icon_path = get_icon(app, "icon_cache")
        new_icon_paths.append(icon_path)

    # Una vez terminado, pasamos al hilo principal
    pygame.event.post(pygame.event.Event(pygame.USEREVENT, {
        "icon_paths": new_icon_paths,
        "apps": updated_apps
    }))

def main():
    global app_rects, icon_paths, icon_sprites, apps , run
    # Crear carpeta de caché de íconos
    os.makedirs("icon_cache", exist_ok=True)

    # Inicializar Pygame y OpenGL
    pygame.init()
    pygame.display.set_mode((600, 600), DOUBLEBUF | OPENGL | NOFRAME | HIDDEN)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 600, 600, 0, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Superficie con transparencia
    surface = pygame.Surface((600, 600), pygame.SRCALPHA)

    # Preparar textura OpenGL
    glEnable(GL_TEXTURE_2D)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # Efectos de ventana (blur, transparencia)
    hwnd = pygame.display.get_wm_info()["window"]
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(
        hwnd,
        win32con.GWL_EXSTYLE,
        style | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | WS_EX_NOREDIRECTIONBITMAP
    )
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

    apply_acrylic_effect(hwnd, use_blur)




    # Fuentes
    title_font = pygame.font.Font("assets/Title_font.ttf", 32)
    app_font = pygame.font.SysFont(None, 12)

    title_surface = title_font.render(folder_name, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(300, 32))

    close_surface = title_font.render(" X ", True, (255, 255, 255))
    close_rect = close_surface.get_rect(center=(600 - 32, 32))


    threading.Thread(target=load_icons_thread, daemon=True).start()

    clock = pygame.time.Clock()
    pygame.display.set_mode((600, 600), DOUBLEBUF | OPENGL | NOFRAME | SHOWN)

    # Bucle principal
    while run:
        # Dibujar fondo
        pygame.draw.rect(surface, (0,0,0,0), (0, 0, 600, 600))
        pygame.draw.rect(surface, bg_color + [bg_opacity], (0, 0, 600, 600))
        pygame.draw.rect(surface, border_color, (0, 0, 600, 600), width=2)

        # Fondo del título
        pygame.draw.rect(surface, border_color + [128], (0, 0, 600, 64))
        pygame.draw.rect(surface, border_color, (0, 0, 600, 64), width=2)

        surface.blit(title_surface, title_rect)
        surface.blit(close_surface, close_rect)


        mouse_pos = pygame.mouse.get_pos()
        hover_sub_menu = False
        for menu in sub_menus:
            if menu.rect.collidepoint(mouse_pos):
                hover_sub_menu = True
            else:
                hover_sub_menu = False

        # Dibujar íconos
        for i, icon in enumerate(icon_sprites):
            x, y = app_rects[i].topleft
            back_rect = app_rects[i].inflate(30, 30)
            if back_rect.collidepoint(mouse_pos) and not hover_sub_menu:
                pygame.draw.rect(surface, border_color, back_rect, 2, border_radius=4)
            surface.blit(icon, (x, y))

        # Hover sobre botón de cerrar
        if close_rect.collidepoint(mouse_pos):
            pygame.draw.rect(surface, border_color, close_rect, 2, border_radius=4)

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.DROPFILE:
                file_path = event.file
                if file_path.endswith((".exe", ".url", ".lnk")):
                    print("Archivo arrastrado:", file_path)
                    apps.append(file_path)
                    save_folder_data("data.json", folder_name, apps)
                    threading.Thread(target=load_icons_thread, daemon=True).start()

            elif event.type == pygame.USEREVENT: # thread icon reciever
    	        icon_paths = event.icon_paths
    	        apps = event.apps
    	        app_rects.clear()
    	        icon_sprites.clear()

    	        icon_x, icon_y = 0, 1
    	        for icon in icon_paths:
    	            if icon:
    	                sprite = pygame.image.load(str(icon)).convert_alpha()
    	                icon_sprites.append(sprite)
    	                rect = pygame.Rect(icon_x * (64 + 32) + 30, icon_y * (64 + 32), 64, 64)
    	                app_rects.append(rect)
    	                icon_x += 1
    	                if icon_x == 6:
    	                    icon_x = 0
    	                    icon_y += 1

            for menu in sub_menus:
                menu.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN and not hover_sub_menu:
                if event.button == 1:
                    if close_rect.collidepoint(mouse_pos):
                        run = False
                    for i, app_rect in enumerate(app_rects):
                        if app_rect.inflate(30, 30).collidepoint(mouse_pos) and sub_menus == []:
                            os.startfile(apps[i])
                            run = False
                if event.button == 3:
                    for i, app_rect in enumerate(app_rects):
                        if app_rect.inflate(30, 30).collidepoint(mouse_pos):
                            print("open_context_menu , app: ",apps[i])
                            new_rect = app_rect
                            sub_menus.append(ContextMenu(surface,apps,i,new_rect,bg_color,border_color,sub_menus))

        # Renderizar submenus
        for menu in sub_menus:
            menu.render()

        # Render OpenGL
        glClear(GL_COLOR_BUFFER_BIT)
        blit_surface_to_opengl(surface)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    # Código que solo querés ejecutar si corrés main.py directamente
    main()  # o lo que uses para iniciar el programa