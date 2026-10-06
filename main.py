"""Entrada da Boneca Digital Interativa. Execute com: python main.py"""
import pygame
from config.settings import WIDTH, HEIGHT, FPS, TITLE, COLORS
from screens.experience import Home, Intro, Mood, Body, End


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.ticks = 0
        self.mouse = (0, 0)
        self.running = True
        self.screens = {
            "home": Home(self), "intro": Intro(self), "mood": Mood(self),
            "body": Body(self), "end": End(self),
        }
        self.current = self.screens["home"]

    def show(self, name):
        self.current = self.screens[name]

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.ticks = pygame.time.get_ticks()
            self.mouse = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.current.handle_event(event)
            self.current.update(dt)
            self.current.draw()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    App().run()
