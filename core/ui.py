"""Componentes visuais simples reutilizados pelas telas."""
import math
import pygame
from config.settings import COLORS


def draw_text(surface, text, size, color, center, bold=False):
    font = pygame.font.SysFont("dejavusans", size, bold=bold)
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))
    return image.get_rect(center=center)


def button(surface, rect, label, color, mouse_pos, font_size=23):
    rect = pygame.Rect(rect)
    hovered = rect.collidepoint(mouse_pos)
    fill = tuple(max(0, c - 15) for c in color) if hovered else color
    pygame.draw.rect(surface, COLORS["shadow"], rect.move(0, 5), border_radius=22)
    pygame.draw.rect(surface, fill, rect, border_radius=22)
    draw_text(surface, label, font_size, COLORS["white"], rect.center, True)
    return rect


def panel(surface, rect, color=COLORS["white"]):
    pygame.draw.rect(surface, COLORS["shadow"], pygame.Rect(rect).move(0, 5), border_radius=28)
    pygame.draw.rect(surface, color, rect, border_radius=28)


def draw_doll(surface, center, scale=1.0, tick=0):

    x, y = center
    bob = math.sin(tick * 0.003) * 4 * scale
    s = scale
    # cabelo ao fundo e cabeça
    pygame.draw.ellipse(surface, COLORS["hair"], (x-47*s, y-116*s+bob, 94*s, 103*s))
    pygame.draw.ellipse(surface, COLORS["skin"], (x-39*s, y-111*s+bob, 78*s, 82*s))
    # franja