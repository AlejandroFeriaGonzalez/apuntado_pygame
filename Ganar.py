import sys
from itertools import chain

from funciones import *


class Ganar:
    def __init__(self, game, mesa):
        self.game = game
        self.mesa = mesa
        self.cartas_no_usadas = None
        self.K_RIGHT_presionada = False
        self.was_pressed = False
        self.forma_de_ganar = None  # toco | gano  # forma en que gano el jugador

        self.carta_activa = None
        self.rect_cartas_en_juego = None

        self.lista_cartas_en_espacios: list[list] = []

        self.font_letras = pygame.font.SysFont("impact", 30)
        self.surf_texto_comprobar = self.font_letras.render("comprobar", True, "white")
        self.rect_texto_comprobar = self.surf_texto_comprobar.get_rect()
        self.rect_texto_comprobar.center = (900, self.game.screen_rect.height - 250)

        self.surf_texto_entregar = self.font_letras.render("Entregar", True, "white")
        self.rect_texto_entregar = self.surf_texto_entregar.get_rect()
        self.rect_texto_entregar.center = (900, self.game.screen_rect.height - 200)

        widht_espacios = 700
        height_espacios = 100
        self.espacios = [
            pygame.Rect(0, 0, widht_espacios, height_espacios),
            pygame.Rect(0, 0, widht_espacios, height_espacios),
            pygame.Rect(0, 0, widht_espacios, height_espacios)
        ]

        self.color_espacios = ["red", "red", "red"]

        self.lista_cartas_en_espacios_verdes = []

        y = 50
        for espacio in self.espacios:
            espacio.midtop = 400, y
            y += 120

    def posicionar_cartas_mano(self):
        i = 10
        for clave in self.mesa.mano:
            self.mesa.dict_cartas[clave][1].topleft = (i, 500)
            # carta[1].topleft = (i, 500)
            i += 100

    def check_event(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.mesa.posicionar_cartas_mano()
            self.game.gameStateManager.set_state("mesa")

        if keys[pygame.K_RIGHT] and not self.K_RIGHT_presionada:
            self.lista_cartas_en_espacios_verdes.clear()
            self.color_espacios = ["red", "red", "red"]
            self.siguiente_mano()

        self.K_RIGHT_presionada = keys[pygame.K_RIGHT]

        # logica boton de comprobar
        if self.rect_texto_comprobar.collidepoint(mouse_x, mouse_y):
            self.surf_texto_comprobar = self.font_letras.render("comprobar", True, "blue")

            if pygame.mouse.get_pressed()[0] and not self.was_pressed:  # da click en comprobar

                self.cartas_en_espacios()
                for i, cartas_en_espacio in enumerate(self.lista_cartas_en_espacios):
                    if es_combinacion_valida(cartas_en_espacio):
                        self.color_espacios[i] = "green"
                    else:
                        self.color_espacios[i] = "red"
        else:
            self.surf_texto_comprobar = self.font_letras.render("comprobar", True, "white")

        # logica de boton de enviar, actualiza tabla
        if self.rect_texto_entregar.collidepoint(mouse_x, mouse_y):
            self.surf_texto_entregar = self.font_letras.render("Entregar", True, "blue")
            if pygame.mouse.get_pressed()[0] and not self.was_pressed:  # da click en comprobar

                self.cartas_en_espacios()
                self.lista_cartas_en_espacios_verdes.clear()
                for i, cartas_en_espacio in enumerate(self.lista_cartas_en_espacios):
                    # colorear espacios
                    if es_combinacion_valida(cartas_en_espacio):
                        self.color_espacios[i] = "green"
                        self.lista_cartas_en_espacios_verdes.append(cartas_en_espacio)  # '8D2', '5S', '7C
                    else:
                        self.color_espacios[i] = "red"

                if self.mesa.jugador_actual == self.mesa.num_jugador_que_termino_ronda:
                    # si es el jugador que toco
                    if all(x == "green" for x in self.color_espacios) or GANAR_NO_OBLIGATORIO:
                        print("gano")  # ningun jugador puede tomar otra carta
                        self.forma_de_ganar = "gano"
                        if all(x == "green" for x in self.color_espacios):
                            self.mesa.puntos_jugadores[self.mesa.jugador_actual] -= 10
                    else:
                        # salir
                        self.forma_de_ganar = "no_gano"
                        self.mesa.posicionar_cartas_mano()
                        self.game.gameStateManager.set_state("mesa")

                lista_plana = set(chain.from_iterable(self.lista_cartas_en_espacios_verdes))
                self.cartas_no_usadas = set(self.mesa.mano) - lista_plana
                if self.forma_de_ganar != "no_gano":
                    for carta in self.cartas_no_usadas:
                        valor = int(carta.removesuffix('2')[:-1])
                        if valor > 10:
                            valor = 10
                        if valor == 1:
                            valor = 10
                        self.mesa.puntos_jugadores[self.mesa.jugador_actual] += valor

                self.lista_cartas_en_espacios_verdes.clear()
                self.color_espacios = ["red", "red", "red"]

                if (self.mesa.num_jugador_que_termino_ronda - 1) % self.mesa.num_jugadores == self.mesa.jugador_actual:
                    # si el jugador que toco vuelve de nuevo significa que ya se termino la ronda

                    self.mesa.posicionar_cartas_mano()
                    self.mesa.nuevo_juego()
                    self.game.gameStateManager.set_state("mesa")

                self.siguiente_mano()

        else:
            self.surf_texto_entregar = self.font_letras.render("Entregar", True, "white")

        self.was_pressed = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            self.mover_carta(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def siguiente_mano(self):
        # si la carta no esta en la mesa la saca
        # list_cartas_en_mesa = self.mesa.mesa_verde_rect.collidelistall(self.mesa.list_rect_cartas)

        for clave in self.mesa.mano:  # sacar a las anteriores antes de poner las nuevas
            self.mesa.dict_cartas[clave][1].bottomright = (-1, -1)
        self.mesa.index += 1
        self.mesa.jugador_actual = self.mesa.index % self.mesa.num_jugadores
        self.mesa.mano = self.mesa.manos_jugadores[self.mesa.jugador_actual]
        self.mesa.texto_turno = self.mesa.font.render(
            f'Turno: {self.mesa.lista_nombres[self.mesa.jugador_actual]}', True, "white")

        # if self.forma_de_ganar == "toco":
        # el primer jugador no puede tomar carta del mazo

        self.posicionar_cartas_mano()  # cambia las cartas de la mano

    def mover_carta(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for carta in self.rect_cartas_en_juego:
                    if carta.collidepoint(event.pos):
                        self.carta_activa = carta
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.carta_activa = None
        if event.type == pygame.MOUSEMOTION:
            if self.carta_activa is not None:
                self.carta_activa.move_ip(event.rel)

    def cartas_en_espacios(self):
        # actualiza self.lista_cartas_en_espacios
        self.lista_cartas_en_espacios = []
        for i, espacio in enumerate(self.espacios):
            lista = []
            for carta in self.mesa.mano.items():
                if espacio.colliderect(carta[1][1]):
                    lista.append(carta[0])

            self.lista_cartas_en_espacios.append(lista)

    def uptade(self):
        # self.game.screen.fill((0, 0, 0))
        self.game.screen.blit(self.game.fondo, (0, 0))
        self.game.screen.blit(self.mesa.texto_turno, (0, 0))

        # lista de rects
        self.rect_cartas_en_juego = self.game.screen_rect.collideobjectsall(self.mesa.list_rect_cartas)

        self.game.screen.blit(self.surf_texto_comprobar, self.rect_texto_comprobar)
        self.game.screen.blit(self.surf_texto_entregar, self.rect_texto_entregar)
        for i, espacio in enumerate(self.espacios):
            pygame.draw.rect(self.game.screen, self.color_espacios[i], espacio)

        if self.mesa.mano:
            for clave in self.mesa.mano:
                self.game.screen.blit(self.mesa.dict_cartas[clave][0], self.mesa.dict_cartas[clave][1])

        pygame.display.update()
        self.game.clock.tick(FPS)

    def run(self):
        # print("ventana ganar")
        self.check_event()
        self.uptade()
