import pygame
from pygame.locals import *
from OpenGL.GL import *

def blit_surface_to_opengl(surf):
    """Renderiza una pygame.Surface con alpha usando OpenGL"""
    data = pygame.image.tostring(surf, "RGBA", True)
    width, height = surf.get_size()

    # Crear textura
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1); glVertex2f(0, 0)
    glTexCoord2f(1, 1); glVertex2f(width, 0)
    glTexCoord2f(1, 0); glVertex2f(width, height)
    glTexCoord2f(0, 0); glVertex2f(0, height)
    glEnd()