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
            pygame.display.set_caption(f"{self.clock.get_fps() :.1f}")
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
        self.carta_de_mazo = None
        self.cartas_repartidas = None
        self.tecla_presionada = False
        self.carta_entregada = None
        self.num_jugadores = 2
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

        # self.mesa_verde = pygame.Surface((SCREEN_WIDTH, 200))
        # self.mesa_verde.fill("green")
        self.mesa_verde_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 200)
        self.mesa_verde_rect.topleft = (0, SCREEN_HEIGHT - 200)

        self.rect_carta_a_entregar = pygame.Rect(0, 0, 80, 100)
        self.rect_carta_a_entregar.center = 900, 300

        self.button_text = self.dict_cartas["backB"][0]
        self.button_rect = self.button_text.get_rect(center=(100, 100))
        self.was_pressed = False

        self.carta_activa = None
        self.nombre_carta_activa = None

        self.mano: dict = {}
        self.list_rect_cartas_en_juego = None

        self.manos_jugadores = []
        self.index = 0

    def check_events(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        # cuando toca la carta volteada da una mano random
        if self.button_rect.collidepoint(mouse_x, mouse_y):  # tomar carta del mazo
            if pygame.mouse.get_pressed()[0] and not self.was_pressed:

                if self.cartas_repartidas:
                    while True:
                        nueva_carta = random.choice(self.lista_claves[:-2])
                        if nueva_carta in self.cartas_repartidas:
                            continue
                        self.carta_de_mazo = self.dict_cartas[nueva_carta]  # suf y rect de la carta entregada
                        self.carta_de_mazo[1].center = 200, 200
                        # print(self.carta_de_mazo[1].x, self.carta_de_mazo[1].y)
                        break

        self.was_pressed = pygame.mouse.get_pressed()[0]

        if keys[pygame.K_n]:
            if not self.tecla_presionada:
                if self.manos_jugadores:  # envia la cartas que estaban antes fuera del mapa
                    for mano in self.manos_jugadores:
                        for clave in mano:
                            self.dict_cartas[clave][1].bottomright = -1, -1

                self.manos_jugadores.clear()
                self.cartas_repartidas = random.sample(self.lista_claves[:-2], 10 * self.num_jugadores)
                for i in range(0, len(self.cartas_repartidas), 10):
                    d = {}
                    for c in self.cartas_repartidas[i: i + 10]:
                        d[c] = self.dict_cartas[c]
                    self.manos_jugadores.append(d)  # lista de diccionarios

                self.mano = self.manos_jugadores[0]
                self.posicionar_cartas_mano()

        self.tecla_presionada = keys[pygame.K_n]

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for carta in self.list_rect_cartas_en_juego:
                        if carta.collidepoint(event.pos):
                            self.carta_activa = carta

            if keys[pygame.K_SPACE]:
                self.game.gameStateManager.set_state("start")
            if keys[pygame.K_RIGHT]:
                if self.mano:
                    # actualizar mano
                    self.mano.clear()
                    # si la carta no esta en la mesa la saca
                    list_cartas_en_mesa = self.mesa_verde_rect.collidelistall(self.list_rect_cartas)
                    for num_carta in list_cartas_en_mesa:
                        nomble_clave_carta = self.lista_claves[num_carta]
                        self.mano[nomble_clave_carta] = self.dict_cartas[nomble_clave_carta]

                    for clave in self.mano:  # sacar a las anteriores antes de poner las nuevas
                        self.dict_cartas[clave][1].bottomright = (-1, -1)

                    self.index += 1
                    self.mano = self.manos_jugadores[self.index % self.num_jugadores]
                    self.posicionar_cartas_mano()  # cambia las cartas de la mano

                # agregar carta extra, # saca la anterior
                if self.carta_entregada and not self.rect_carta_a_entregar.colliderect(self.carta_entregada[1]):
                    self.carta_entregada[1].bottomright = -1, -1

                num_carta_entregada = self.rect_carta_a_entregar.collidelist(self.list_rect_cartas)
                if num_carta_entregada != -1:
                    nomble_clave_carta = self.lista_claves[num_carta_entregada]
                    self.carta_entregada = self.dict_cartas[nomble_clave_carta]
                    self.carta_entregada[1].center = 100, 300

                # la carta tomada del mazo si no fue seleccionada se va fuera
                if self.carta_de_mazo != self.carta_entregada and self.carta_de_mazo not in self.mano.values():
                    self.carta_de_mazo[1].bottomright = -1, -1

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.carta_activa = None

            if event.type == pygame.MOUSEMOTION:
                if self.carta_activa is not None:
                    self.carta_activa.move_ip(event.rel)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def posicionar_cartas_mano(self):
        i = 10
        for clave in self.mano:
            self.dict_cartas[clave][1].topleft = (i, 500)
            # carta[1].topleft = (i, 500)
            i += 100

    def uptade(self):

        self.game.screen.fill((0, 0, 0))
        pygame.draw.rect(self.game.screen, "green", self.mesa_verde_rect)
        pygame.draw.rect(self.game.screen, "green", self.rect_carta_a_entregar)

        self.list_rect_cartas_en_juego = self.game.screen_rect.collideobjectsall(self.list_rect_cartas)

        # * ver nombre de las cartas en el cuadro verde
        # list_cartas_en_mesa = self.mesa_verde_rect.collidelistall(self.list_rect_cartas)
        # for num_carta in list_cartas_en_mesa:
        #     self.nombre_carta_activa = self.lista_claves[num_carta]
        #     print(self.nombre_carta_activa, end=", ")  # rect
        # print()

        if self.mano:
            for clave in self.mano:
                self.game.screen.blit(self.dict_cartas[clave][0], self.dict_cartas[clave][1])

        if self.carta_entregada:
            self.game.screen.blit(self.carta_entregada[0], self.carta_entregada[1])

        if self.carta_de_mazo:
            self.game.screen.blit(self.carta_de_mazo[0], self.carta_de_mazo[1])

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
    mygame = Game()
    mygame.run()
