import pygame
import win32gui
import win32ui
import win32con
import win32api
import ctypes

# Constantes necesarias
WS_EX_NOREDIRECTIONBITMAP = 0x00200000

ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
ACCENT_ENABLE_TRANSPARENTGRADIENT = 2

class ACCENTPOLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_int),
        ("AnimationId", ctypes.c_int)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.c_void_p),
        ("SizeOfData", ctypes.c_size_t)
    ]

def tint_only_transparent_pixels(surface, bg_color):
    """Applies a tint over non-transparent pixels only."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((*bg_color, 255))
    surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MAX)

def set_window_rounded(hwnd, width, height, radius):
    hrgn = win32gui.CreateRoundRectRgn(0, 0, width, height, radius, radius)
    win32gui.SetWindowRgn(hwnd, hrgn, True)

def apply_acrylic_effect(hwnd,use_blur):
    """
    Applies Windows 10/11 acrylic blur to the entire window,
    but you can combine it with a tinting overlay that only affects
    non-transparent regions in your app.
    """

    accent = ACCENTPOLICY()

    
    accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
    accent.AccentFlags = 1

    if not use_blur:
        accent.AccentState = ACCENT_ENABLE_TRANSPARENTGRADIENT
        accent.AccentFlags = 2

    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = 19  # WCA_ACCENT_POLICY
    data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.c_void_p)
    data.SizeOfData = ctypes.sizeof(accent)

    set_window_composition_attribute = ctypes.windll.user32.SetWindowCompositionAttribute
    set_window_composition_attribute(hwnd, ctypes.byref(data))


