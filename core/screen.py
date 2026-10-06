"""Classe base para telas do protótipo."""
import pygame
from config.settings import COLORS
from core.ui import draw_text

class Screen:
    def __init__(self, app):
        self.app = app

    def background(self):
        self.app.surface.fill(COLORS["background"])
        # pequenos círculos decorativos discretos
        pygame.draw.circle(self.app.surface, (235, 229, 211), (65, 75), 22)
        pygame.draw.circle(self.app.surface, (228, 239, 231), (900, 95), 30)
        pygame.draw.circle(self.app.surface, (235, 229, 211), (880, 575), 18)

    def heading(self, title, subtitle=None):
        draw_text(self.app.surface, title, 34, COLORS["ink"], (480, 58), True)
        if subtitle:
            draw_text(self.app.surface, subtitle, 18, COLORS["muted"], (480, 94))

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self):
        self.background()
