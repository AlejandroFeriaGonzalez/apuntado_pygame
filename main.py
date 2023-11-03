import os
import random
import sys

import pygame

from GLOBAL import *

# ('C:\\Users\\Alejandro Feria\\PycharmProjects\\apuntado', 'main.py')
main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit(f'Could not load image "{file}" {pygame.get_error()}')
    return surface.convert()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen_rect = self.screen.get_rect()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("freesans", 20)

        self.ruta_cartas = os.path.join(main_dir, "data", "Cards")
        pygame.display.set_caption("Move Cards")

        self.gameStateManager = GameStateManager('start')
        self.start = Start(self)
        self.mesa = Mesa(self)

        self.states = {
            'start': self.start,
            'mesa': self.mesa
        }

    def run(self):
        while True:
            self.states[self.gameStateManager.get_state()].run()


class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState

    def get_state(self):
        return self.currentState

    def set_state(self, state):
        self.currentState = state


class Mesa:
    def __init__(self, game: Game):
        self.game = game

        self.list_rect_cartas = []
        self.dict_cartas = {}

        # cargar imagenes
        for img in os.listdir(self.game.ruta_cartas):
            file = os.path.join(main_dir, "data", "Cards", img)
            image = load_image(file)
            object_rect = image.get_rect()
            object_rect.bottomright = (-1, -1)  # se ponen fuera del mapa

            self.dict_cartas[img.removesuffix(".png")] = (image, object_rect)
            self.list_rect_cartas.append(object_rect)

        self.lista_claves = list(self.dict_cartas.keys())

        self.mesa_verde = pygame.Surface((SCREEN_WIDTH, 200))
        self.mesa_verde.fill("green")
        self.mesa_verde_rect = self.mesa_verde.get_rect()
        self.mesa_verde_rect.topleft = (0, SCREEN_HEIGHT - 200)

        self.button_text = self.dict_cartas["backB"][0]
        self.button_rect = self.button_text.get_rect(center=(100, 100))
        self.was_pressed = False

        self.lista_claves = list(self.dict_cartas.keys())
        self.carta_activa = None
        self.nombre_carta_activa = None

        self.mano = None
        self.list_cartas_en_juego = None

    def check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for num_carta in self.list_cartas_en_juego:
                        self.nombre_carta_activa = self.lista_claves[num_carta]
                        carta = self.dict_cartas[self.nombre_carta_activa][1]  # rect
                        if carta.collidepoint(event.pos):
                            self.carta_activa = carta
                            # print(nombre_carta_activa)
            if event.type == pygame.KEYDOWN:
                self.game.gameStateManager.set_state("start")

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.carta_activa = None

            if event.type == pygame.MOUSEMOTION:
                if self.carta_activa is not None:
                    self.carta_activa.move_ip(event.rel)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def uptade(self):
        self.game.screen.fill((0, 0, 0))
        self.game.screen.blit(self.mesa_verde, self.mesa_verde_rect)

        self.list_cartas_en_juego = self.game.screen_rect.collidelistall(self.list_rect_cartas)

        list_cartas_en_mesa = self.mesa_verde_rect.collidelistall(self.list_rect_cartas)
        for num_carta in list_cartas_en_mesa:
            self.nombre_carta_activa = self.lista_claves[num_carta]
        #     print(self.nombre_carta_activa, end=", ")  # rect
        # print()

        if self.mano:
            for clave, carta in self.mano:
                self.game.screen.blit(carta[0], carta[1])

        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.button_rect.collidepoint(mouse_x, mouse_y):
            if pygame.mouse.get_pressed()[0] and not self.was_pressed:

                if self.mano:
                    for clave, carta in self.mano:
                        carta[1].bottomright = (-1, -1)

                self.mano = random.sample(list(self.dict_cartas.items())[:-2], 10)
                i = 10
                for clave, carta in self.mano:
                    carta[1].topleft = (i, 500)
                    i += 100

        self.was_pressed = pygame.mouse.get_pressed()[0]

        self.game.screen.blit(self.button_text, self.button_rect)

        pygame.display.update()
        self.game.clock.tick(FPS)

    def run(self):
        self.check_events()
        self.uptade()


class Start:
    def __init__(self, game: Game):
        self.game = game
        self.font = pygame.font.SysFont("impact", 100)
        self.surf_texto_inicio = self.font.render("Apuntado", True, "red")
        self.rect_texto_inicio = self.surf_texto_inicio.get_rect()
        self.rect_texto_inicio.center = (self.game.screen_rect.centerx, 100)

        self.button_text = self.font.render("Iniciar", True, "white")
        self.button_text_rect = self.button_text.get_rect()
        self.button_text_rect.center = (self.game.screen_rect.centerx, self.game.screen_rect.centery)
        self.was_pressed = False

    def check_event(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.button_text_rect.collidepoint(mouse_x, mouse_y):
            self.button_text = self.font.render("Iniciar", True, "blue")
            if pygame.mouse.get_pressed()[0] and not self.was_pressed:
                self.game.gameStateManager.set_state('mesa')
        else:
            self.button_text = self.font.render("Iniciar", True, "white")

        self.was_pressed = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                self.game.gameStateManager.set_state('mesa')

    def uptade(self):
        self.game.screen.fill((0, 0, 0))

        self.game.screen.blit(self.surf_texto_inicio, self.rect_texto_inicio)
        self.game.screen.blit(self.button_text, self.button_text_rect)

        pygame.display.update()
        self.game.clock.tick(FPS)

    def run(self):
        self.check_event()
        self.uptade()


if __name__ == "__main__":
    game = Game()
    game.run()
