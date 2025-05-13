import os
import pygame
import win32api
import win32con
import win32gui
import subprocess
import sys
import winreg

from get_icon import get_icon
from get_icon import get_exe_from_lnk

from save_load_data import save_folder_data 
from save_load_data import load_apps_from_folder

# args :
# 0 = folder_name
# 1 = bg_color
# 2 = show_text

os.makedirs("icon_cache", exist_ok=True)

fuchsia = (255, 0, 128)
run = True

app_rects = []
icon_paths = []
icon_sprites = []

folder_name = "Default Folder"
bg_color = "50, 0, 0"
border_color = "100, 0, 0"
show_text = True

print(f"args: {sys.argv}")
for i,argument in enumerate(sys.argv):
	if argument == "--CodeName":
		folder_name = sys.argv[i+1]

	if argument == "--BgCol":
		bg_color = sys.argv[i+1]

	if argument == "--BorderCol":
		border_color = sys.argv[i+1]

	if argument == "--NoText":
		show_text = False

bg_color = bg_color.split(",")
border_color = border_color.split(",")

for i,col in enumerate(bg_color):
	bg_color[i] = int(col)

for i,col in enumerate(border_color):
	border_color[i] = int(col)

print("folder_name: ",folder_name)
print("bg_color: ",bg_color)
print("border_color: ",border_color)
print("show_text: ",show_text)

pygame.init()
surface = pygame.display.set_mode((600,600),pygame.NOFRAME)

hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
# Set window transparency color
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

surface.fill(fuchsia)
pygame.draw.rect(surface,bg_color,(0,0,600,600),border_radius=50)
pygame.draw.rect(surface,border_color,(0,0,600,600),width=5,border_radius=50)
pygame.display.update()

title_font = pygame.font.SysFont(None, 36)
app_font = pygame.font.SysFont(None, 12)

title_surface = title_font.render(folder_name, True, (255, 255, 255))
title_rect = title_surface.get_rect(center=(300, 32))

apps = load_apps_from_folder("data.json",folder_name)

def lerp_color(color1, color2, t):
    return tuple(
        int(a + (b - a) * t) for a, b in zip(color1, color2)
    )

def get_apps():
	global app_rects ,icon_paths ,icon_sprites
	for i,app in enumerate(apps):
		if ".lnk" in app:
			apps[i] = get_exe_from_lnk(app)

	print(apps)

	app_rects = []
	icon_paths = []
	icon_sprites = []

	for app in apps :
		icon_paths.append(get_icon(app,r"icon_cache"))

	icon_x = 0
	icon_y = 1
	for i,icon in enumerate(icon_paths):
		if icon:
			print("icon: ",icon)
			if icon_x == 6:
				icon_x = 0
				icon_y += 1
			sprite = pygame.image.load(str(icon)).convert_alpha()
			sprite = pygame.transform.scale(sprite,(64,64))
			icon_sprites.append(sprite)
			app_rects.append(pygame.Rect(icon_x*(64+32)+30 , icon_y*(64+32), 64 , 64))
			icon_x += 1

get_apps()

while run:
	surface.fill(fuchsia)
	pygame.draw.rect(surface,bg_color,(0,0,600,600),border_radius=32)
	pygame.draw.rect(surface,border_color,(0,0,600,600),width=5,border_radius=32)
	surface.blit(title_surface, title_rect)

	for i,icon in enumerate(icon_sprites):
		x = app_rects[i].x
		y = app_rects[i].y
		back_rect = app_rects[i].copy()
		back_rect.inflate_ip(30,30)
		if back_rect.collidepoint(pygame.mouse.get_pos()):
			pygame.draw.rect(surface,lerp_color(border_color,bg_color,0.2),back_rect,10,border_radius=2)
			pygame.draw.rect(surface,lerp_color(border_color,bg_color,0.4),back_rect,8,border_radius=4)
			pygame.draw.rect(surface,lerp_color(border_color,bg_color,0.6),back_rect,6,border_radius=6)
			pygame.draw.rect(surface,lerp_color(border_color,bg_color,0.8),back_rect,4,border_radius=8)
			pygame.draw.rect(surface,lerp_color(border_color,bg_color,1),back_rect,2,border_radius=10)

			back_rect.inflate_ip(20,20)
			pygame.draw.rect(surface,bg_color,back_rect,10,border_radius=20)
		surface.blit(icon,(x,y))
			

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

		if event.type == pygame.DROPFILE:
			ruta_archivo = event.file
			if ".exe" in ruta_archivo or ".url" in ruta_archivo or ".lnk" in ruta_archivo:
				print("Archivo arrastrado:", ruta_archivo)
				apps.append(ruta_archivo)
				save_folder_data("data.json",folder_name,apps)
				get_apps()

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				for i,app_rect in enumerate(app_rects):
					if app_rect.collidepoint(pygame.mouse.get_pos()):
						# subprocess.Popen([apps[i]],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
						os.startfile(apps[i])
						run = False

	pygame.display.update()