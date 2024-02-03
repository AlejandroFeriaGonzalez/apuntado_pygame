import pygame

from GLOBAL import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("freesans", 20)

        file = os.path.join(main_dir, "data", "fondo.png")
        self.fondo = pygame.image.load(file).convert()

        file_flecha = os.path.join(main_dir, "data", "flecha.png")
        flecha = pygame.image.load(file_flecha).convert_alpha()
        self.flecha = pygame.transform.scale(flecha, (50, 50))
        self.flecha_rect = self.flecha.get_rect()
        self.flecha_rect.topleft = (self.screen_rect.right - 50, self.screen_rect.centery - 50)

        self.ruta_cartas = os.path.join(main_dir, "data", "Cards")
        pygame.display.set_caption("Move Cards")

        self.gameStateManager = GameStateManager('start')
        self.start = Start(self)
        # self.mesa = Mesa(self)
        # self.ganar = Ganar(self, self.mesa)

        self.states = {
            'start': self.start
        }

        # self.states = {
        #     'start': self.start,
        #     'mesa': self.mesa,
        #     'ganar': self.ganar
        # }

    def run(self):
        while True:
            pygame.display.set_caption(f"{self.clock.get_fps() :.1f}")
            self.states[self.gameStateManager.get_state()].run()
