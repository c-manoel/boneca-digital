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
    """Boneca amigável feita só com formas do Pygame; sem arquivos externos."""
    x, y = center
    bob = math.sin(tick * 0.003) * 4 * scale
    s = scale
    # cabelo ao fundo e cabeça
    pygame.draw.ellipse(surface, COLORS["hair"], (x-47*s, y-116*s+bob, 94*s, 103*s))
    pygame.draw.ellipse(surface, COLORS["skin"], (x-39*s, y-111*s+bob, 78*s, 82*s))
    # franja
    pygame.draw.arc(surface, COLORS["hair"], (x-42*s, y-124*s+bob, 84*s, 63*s), 3.14, 6.20, max(4, int(12*s)))
    # orelhas
    pygame.draw.circle(surface, COLORS["skin"], (int(x-39*s), int(y-74*s+bob)), max(4,int(9*s)))
    pygame.draw.circle(surface, COLORS["skin"], (int(x+39*s), int(y-74*s+bob)), max(4,int(9*s)))
    # olhos e sorriso
    pygame.draw.circle(surface, COLORS["ink"], (int(x-14*s), int(y-78*s+bob)), max(2,int(3*s)))
    pygame.draw.circle(surface, COLORS["ink"], (int(x+14*s), int(y-78*s+bob)), max(2,int(3*s)))
    pygame.draw.arc(surface, COLORS["coral"], (x-12*s, y-72*s+bob, 24*s, 17*s), 3.35, 6.05, max(2,int(2*s)))
    # pescoço, vestido e braços
    pygame.draw.rect(surface, COLORS["skin"], (x-10*s, y-37*s+bob, 20*s, 25*s), border_radius=7)
    pygame.draw.ellipse(surface, COLORS["dress"], (x-47*s, y-21*s+bob, 94*s, 105*s))
    pygame.draw.line(surface, COLORS["skin"], (int(x-38*s),int(y-3*s+bob)), (int(x-64*s),int(y+34*s+bob)), max(5,int(13*s)))
    pygame.draw.line(surface, COLORS["skin"], (int(x+38*s),int(y-3*s+bob)), (int(x+64*s),int(y+34*s+bob)), max(5,int(13*s)))
    pygame.draw.circle(surface, COLORS["skin"], (int(x-65*s),int(y+36*s+bob)), max(5,int(8*s)))
    pygame.draw.circle(surface, COLORS["skin"], (int(x+65*s),int(y+36*s+bob)), max(5,int(8*s)))
    pygame.draw.line(surface, COLORS["ink"], (int(x-20*s),int(y+77*s+bob)), (int(x-23*s),int(y+103*s+bob)), max(4,int(9*s)))
    pygame.draw.line(surface, COLORS["ink"], (int(x+20*s),int(y+77*s+bob)), (int(x+23*s),int(y+103*s+bob)), max(4,int(9*s)))
    pygame.draw.ellipse(surface, COLORS["coral"], (x-45*s,y-80*s+bob,12*s,7*s))
    pygame.draw.ellipse(surface, COLORS["coral"], (x+33*s,y-80*s+bob,12*s,7*s))
