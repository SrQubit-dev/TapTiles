#sub_menus
import os
import pygame
import threading

from get_icon import blur_surface_pygame
from main_app import load_icons_thread

class ContextMenu:
	def __init__ (self,surface,apps,app_index,app_rect,bg_color,border_color,parent_list):
		self.apps = apps
		self.app_index = app_index
		self.app_rect = app_rect #add margin to rect
		self.bg_color = bg_color
		self.border_color = border_color
		self.x = app_rect.left
		self.y = app_rect.bottom
		self.parent_list = parent_list

		self.surface = surface
		self.blur_surface  = pygame.transform.scale(surface,(150,150))
		self.blur_surface = blur_surface_pygame(self.blur_surface ,2)
		self.blur_surface = blur_surface_pygame(self.blur_surface ,2)
		self.blur_surface  = pygame.transform.smoothscale(self.blur_surface,(600,600))

		self.rect = pygame.Rect(self.x,self.y,128,128)

		self.options = [
			"Open",
			"Remove",
		]
		self.option_texts = []

		self.font = pygame.font.SysFont(None, 28)
		self.option_objects = []
		for i,option in enumerate(self.options):
			text_surface = self.font.render(option, True, (255, 255, 255))
			text_rect = text_surface.get_rect()
			text_rect.left = self.rect.left + 8
			text_rect.top = self.rect.top + i*28 + 8
			self.option_objects.append([text_surface,text_rect])

	def render(self):
		pygame.draw.rect(self.surface,(0,0,0,0),self.rect)
		self.surface.blit(self.blur_surface,(self.x,self.y),self.rect)
		pygame.draw.rect(self.surface,self.border_color,self.rect,2)

		mouse_pos = pygame.mouse.get_pos()
		for text_surf,text_rect in self.option_objects:
			self.surface.blit(text_surf,text_rect)
			if text_rect.collidepoint(mouse_pos):
				pygame.draw.rect(self.surface,self.border_color,text_rect.inflate((8,8)),2)

	def handle_event(self,event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			mouse_pos = pygame.mouse.get_pos()
			if self.rect.collidepoint(mouse_pos):
				for i,text in enumerate(self.option_objects):
					text_surface,text_rect = text
					if text_rect.collidepoint(mouse_pos):
						if self.options[i] == "Open":
							os.startfile(self.apps[self.app_index])

						if self.options[i] == "Remove":
							self.apps.pop(self.app_index)
							threading.Thread(target=load_icons_thread, daemon=True).start()
			else:
				self.parent_list.remove(self)