import os
import random
import sys
from itertools import chain

import pygame

from GLOBAL import *
from funciones import es_combinacion_valida

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


class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState

    def get_state(self):
        return self.currentState

    def set_state(self, state):
        self.currentState = state


class Mesa:
    def __init__(self, game: Game, lista_nombres: list):
        self.game = game
        self.cartas_en_juego = None
        self.carta_de_mazo = None
        self.cartas_repartidas = None
        self.tecla_N_presionada = False
        self.tecla_right_presionada = False
        self.carta_entregada_de_jugador = None
        self.clave_carta_entregada_de_jugador = None
        self.lista_nombres = lista_nombres
        self.num_jugadores = len(self.lista_nombres)
        self.jugador_actual = 0
        self.num_jugador_que_termino_ronda = None
        self.cartas_que_no_aparecen_mas = set()  # lista de cartas que se desecharon para que vuelvan a aparecer

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

        self.boton_carta = self.dict_cartas["backB"][0]
        self.rect_boton_carta = self.boton_carta.get_rect(center=(100, 100))
        self.was_pressed = False

        #  boton para ganar
        self.font = pygame.font.SysFont("impact", 20)
        self.surf_texto_ganar = self.font.render("TERMINAR RONDA", True, "white")
        self.rect_texto_ganer = self.surf_texto_ganar.get_rect()
        self.rect_texto_ganer.center = (900, 50)

        self.surf_texto_tabla = self.font.render("TABLA PUNTOS", True, "white")
        self.rect_texto_tabla = self.surf_texto_tabla.get_rect()
        self.rect_texto_tabla.center = (900, 100)

        self.carta_activa = None
        self.nombre_carta_activa = None

        self.mano: dict = {}
        self.list_rect_cartas_en_juego = None
        self.nombres_cartas_en_manos: list[list] = []

        self.manos_jugadores = []
        self.puntos_jugadores = [0] * self.num_jugadores
        self.index = 0

        self.texto_turno = self.font.render(
            f'Turno: {self.lista_nombres[self.jugador_actual]}', True, "white")

        self.nuevo_juego()
        self.carta_mazo_fue_entregada = False

    def check_events(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()

        if pygame.mouse.get_pressed()[0] and not self.was_pressed:  # cuando toca la carta volteada da una mano random
            if self.rect_boton_carta.collidepoint(mouse_x, mouse_y) and not self.carta_mazo_fue_entregada:
                self.carta_mazo_fue_entregada = True
                if self.carta_entregada_de_jugador:  # la carta entregada del jugador desaparece
                    self.carta_entregada_de_jugador[1].bottomright = -1, -1
                if self.cartas_repartidas:
                    self.tomar_carta_de_mazo()

            if self.rect_texto_ganer.collidepoint(mouse_x, mouse_y):
                self.actualizar_mano()
                self.num_jugador_que_termino_ronda = self.jugador_actual
                if self.carta_de_mazo and self.carta_de_mazo not in self.mano.values():
                    self.carta_de_mazo[1].bottomright = -1, -1
                self.game.states['ganar'] = Ganar(self.game, self)
                self.game.gameStateManager.set_state("ganar")

            if self.rect_texto_tabla.collidepoint(mouse_x, mouse_y):
                # print(self.lista_nombres)
                # print(self.puntos_jugadores)
                tabla = zip(self.lista_nombres, self.puntos_jugadores)
                out = "TABLA PUNTOS\n"
                for nombre, puntos in tabla:
                    out += f'{nombre}: {puntos}\n'
                print(out)
                fondo_tabla = pygame.font.SysFont("impact", 50)
                surf_tabla = fondo_tabla.render(out, True, "orange")
                self.game.screen.blit(surf_tabla, (400, 50))
                pygame.display.update()
                pygame.time.wait(2000)

            if self.game.flecha_rect.collidepoint(mouse_x, mouse_y):
                if (len(self.mesa_verde_rect.collidelistall(self.list_rect_cartas)) == 10 and
                        len(self.rect_carta_a_entregar.collidelistall(self.list_rect_cartas)) == 1):
                    self.siguiente_mano()

        self.was_pressed = pygame.mouse.get_pressed()[0]

        if keys[pygame.K_n] and not self.tecla_N_presionada:
            self.nuevo_juego()

        self.tecla_N_presionada = keys[pygame.K_n]

        for event in pygame.event.get():
            self.mover_carta(event)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if keys[pygame.K_SPACE]:
            self.game.gameStateManager.set_state("start")  # volver a pantalla de inicio

        if keys[pygame.K_RIGHT] and not self.tecla_right_presionada:
            #  para pasar tiene que tener exactamente 10 cartas en mano y entragar si o si una
            if (len(self.mesa_verde_rect.collidelistall(self.list_rect_cartas)) == 10 and
                    len(self.rect_carta_a_entregar.collidelistall(self.list_rect_cartas)) == 1):
                self.siguiente_mano()

        self.tecla_right_presionada = keys[pygame.K_RIGHT]

    def tomar_carta_de_mazo(self):
        while True:
            nueva_carta = random.choice(self.lista_claves[:-2])
            if nueva_carta in self.cartas_que_no_aparecen_mas:
                continue
            self.carta_de_mazo = self.dict_cartas[nueva_carta]  # suf y rect de la carta entregada
            self.cartas_que_no_aparecen_mas.add(nueva_carta)
            self.carta_de_mazo[1].center = 200, 200
            break

        if len(self.cartas_que_no_aparecen_mas) > 100:
            self.cartas_que_no_aparecen_mas = set(chain.from_iterable(self.nombres_cartas_en_manos))

    def nuevo_juego(self):
        self.cartas_que_no_aparecen_mas.clear()
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
                self.cartas_que_no_aparecen_mas.add(c)
            self.manos_jugadores.append(d)  # lista de diccionarios
            self.nombres_cartas_en_manos.append(list(d.keys()))
        self.mano = self.manos_jugadores[0]
        self.posicionar_cartas_mano()
        if self.carta_de_mazo:
            self.carta_de_mazo[1].bottomright = -1, -1
        self.carta_mazo_fue_entregada = False

    def siguiente_mano(self):
        # actualizar mano
        self.actualizar_mano()
        self.carta_mazo_fue_entregada = False
        for clave in self.mano:  # sacar a las anteriores antes de poner las nuevas
            self.dict_cartas[clave][1].bottomright = (-1, -1)

        self.index += 1
        self.jugador_actual = self.index % self.num_jugadores
        self.mano = self.manos_jugadores[self.jugador_actual]
        self.posicionar_cartas_mano()  # cambia las cartas de la mano
        # agregar carta extra, # saca la anterior
        if (self.carta_entregada_de_jugador  # si existe
                and not self.rect_carta_a_entregar.colliderect(self.carta_entregada_de_jugador[1])  # si no se entraga
                and self.carta_entregada_de_jugador not in self.mano.values()):  # si no esta en la mano
            self.carta_entregada_de_jugador[1].bottomright = -1, -1  # la saca

        num_carta_entregada = self.rect_carta_a_entregar.collidelist(self.list_rect_cartas)  # carta que el jug entrega
        if num_carta_entregada != -1:
            nomble_clave_carta = self.lista_claves[num_carta_entregada]
            self.carta_entregada_de_jugador = self.dict_cartas[nomble_clave_carta]
            # self.cartas_que_no_aparecen_mas.add(nomble_clave_carta)

            self.carta_entregada_de_jugador[1].center = 100, 300

        # la carta tomada del mazo si no fue seleccionada se va fuera
        if (self.carta_de_mazo and self.carta_de_mazo != self.carta_entregada_de_jugador and
                self.carta_de_mazo not in self.mano.values()):
            self.carta_de_mazo[1].bottomright = -1, -1

        self.texto_turno = self.font.render(
            f'Turno: {self.lista_nombres[self.jugador_actual]}', True, "white")

    def actualizar_mano(self):
        self.mano.clear()
        self.nombres_cartas_en_manos[self.jugador_actual].clear()
        # si la carta no esta en la mesa la saca
        list_cartas_en_mesa = self.mesa_verde_rect.collidelistall(self.list_rect_cartas)
        for num_carta in list_cartas_en_mesa:
            nomble_clave_carta = self.lista_claves[num_carta]
            self.mano[nomble_clave_carta] = self.dict_cartas[nomble_clave_carta]
            self.nombres_cartas_en_manos[self.jugador_actual].append(nomble_clave_carta)
            self.cartas_que_no_aparecen_mas.add(nomble_clave_carta)

    def mover_carta(self, event):
        # mover cualquier carta
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for carta in self.list_rect_cartas_en_juego:
                    if carta.collidepoint(event.pos):
                        self.carta_activa = carta
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.carta_activa = None
        if event.type == pygame.MOUSEMOTION:
            if self.carta_activa is not None:
                self.carta_activa.move_ip(event.rel)

    def posicionar_cartas_mano(self):
        i = 10
        for clave in self.mano:
            self.dict_cartas[clave][1].topleft = (i, 500)
            # carta[1].topleft = (i, 500)
            i += 100

    def uptade(self):

        for i, puntos_jugador in enumerate(self.puntos_jugadores):
            if puntos_jugador < -51:
                print(self.lista_nombres)
                print(self.puntos_jugadores)
                ganador = self.lista_nombres.pop(i)
                print("GANADOR:", ganador)
                sys.exit()
            if puntos_jugador > 100:
                print(self.lista_nombres)
                print(self.puntos_jugadores)
                perdedor = self.lista_nombres.pop(i)
                print("PERDEDOR:", perdedor)
                sys.exit()

        # self.game.screen.fill((0, 0, 0))
        self.game.screen.blit(self.game.fondo, (0, 0))
        self.game.screen.blit(self.game.flecha, self.game.flecha_rect)

        self.game.screen.blit(self.texto_turno, (0, 0))

        pygame.draw.rect(self.game.screen, "gray", self.mesa_verde_rect, 2)
        pygame.draw.rect(self.game.screen, "gray3", self.rect_carta_a_entregar, 2)

        self.game.screen.blit(self.surf_texto_ganar, self.rect_texto_ganer)
        self.game.screen.blit(self.surf_texto_tabla, self.rect_texto_tabla)

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

        if self.carta_entregada_de_jugador:
            self.game.screen.blit(self.carta_entregada_de_jugador[0], self.carta_entregada_de_jugador[1])

        if self.carta_de_mazo:
            self.game.screen.blit(self.carta_de_mazo[0], self.carta_de_mazo[1])

        self.game.screen.blit(self.boton_carta, self.rect_boton_carta)

        pygame.display.update()
        self.game.clock.tick(FPS)

    def run(self):
        self.check_events()
        self.uptade()


class Ganar:
    def __init__(self, game: Game, mesa: Mesa):
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


class Start:
    def __init__(self, game: Game):
        self.game = game
        self.font = pygame.font.SysFont("impact", 50)
        self.font2 = pygame.font.SysFont("impact", 100)
        self.surf_texto_inicio = self.font2.render("Apuntado", True, "red")
        self.rect_texto_inicio = self.surf_texto_inicio.get_rect()
        self.rect_texto_inicio.center = (self.game.screen_rect.centerx, 100)

        self.button_text = self.font.render("Iniciar", True, "white")
        self.button_text_rect = self.button_text.get_rect()
        self.button_text_rect.midbottom = (self.game.screen_rect.centerx, self.game.screen_rect.height - 30)
        self.was_pressed = False

        # input texto
        self.color_active = pygame.Color('lightblue3')
        self.color_passive = pygame.Color('gray15')
        self.color = self.color_passive

        self.base_font = pygame.font.Font(None, 32)
        self.label_num_jugadores = self.base_font.render("Numero de jugadores", True, "white")
        self.label_tokens = self.base_font.render("Tokens", True, "white")
        self.label_ok = self.base_font.render("OK", True, "white")
        self.rect_label_ok = self.label_ok.get_rect()

        self.texto_num_jugadores = ''
        self.num_jugadores = None  # int(self.texto_num_jugadores)
        self.rect_input_num_jugadores = pygame.Rect(200, 200, 140, 32)
        self.rect_input_num_jugadores.center = self.game.screen_rect.centerx, 200
        self.rect_label_ok.topleft = 650, self.rect_input_num_jugadores.y + 3

        self.active_input_num_jugadores = False

        self.lista_inputs_nombres = []
        self.lista_nombres: list[str] = []
        self.lista_colores = []
        self.lista_active_input: list[bool] = []
        self.lista_label_nombre_jugadores = []

    def crear_input_nombre(self):
        self.lista_nombres.clear()
        self.lista_inputs_nombres.clear()
        self.lista_colores.clear()
        self.lista_active_input.clear()
        self.lista_label_nombre_jugadores.clear()
        for i in range(self.num_jugadores):  # ejemplo: 0 - 4
            self.lista_nombres.append("")
            self.lista_inputs_nombres.append(pygame.Rect(self.rect_input_num_jugadores.x, 250 + 50 * i, 140, 32))
            self.lista_colores.append(self.color_passive)
            self.lista_active_input.append(False)
            self.lista_label_nombre_jugadores.append(
                self.base_font.render(f"Jugador {i + 1}", True, "white"))

    def check_event(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # input boton iniciar
        if self.button_text_rect.collidepoint(mouse_x, mouse_y):
            self.button_text = self.font.render("Iniciar", True, "blue")
            if pygame.mouse.get_pressed()[0] and not self.was_pressed:
                self.game.states['mesa'] = Mesa(self.game, self.lista_nombres)
                self.game.gameStateManager.set_state('mesa')
        else:
            self.button_text = self.font.render("Iniciar", True, "white")

        if self.rect_label_ok.collidepoint(mouse_x, mouse_y) and pygame.mouse.get_pressed()[0] and not self.was_pressed:
            try:
                self.num_jugadores = int(self.texto_num_jugadores)
                if self.num_jugadores <= 6:
                    self.crear_input_nombre()
                else:
                    print("Demasiados jugadores!!!")
            except ValueError:
                print("Tiene que ser un numero")

        self.was_pressed = pygame.mouse.get_pressed()[0]

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                # escribir el numero de jugadores
                if self.rect_input_num_jugadores.collidepoint(event.pos):
                    self.active_input_num_jugadores = True
                else:
                    self.active_input_num_jugadores = False

                for i, rect in enumerate(self.lista_inputs_nombres):
                    if rect.collidepoint(event.pos):
                        self.lista_active_input[i] = True
                    else:
                        self.lista_active_input[i] = False

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                if self.active_input_num_jugadores:
                    if keys[pygame.K_BACKSPACE]:
                        self.texto_num_jugadores = self.texto_num_jugadores[:-1]
                    else:
                        self.texto_num_jugadores += event.unicode

                for i, rect in enumerate(self.lista_active_input):
                    if self.lista_active_input[i]:
                        if keys[pygame.K_BACKSPACE]:
                            self.lista_nombres[i] = self.lista_nombres[i][:-1]
                        else:
                            self.lista_nombres[i] += event.unicode

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def uptade(self):
        # self.game.screen.fill((0, 0, 0))
        self.game.screen.blit(self.game.fondo, (0, 0))
        # num jugadores
        self.game.screen.blit(self.label_num_jugadores, (190, self.rect_input_num_jugadores.y + 3))
        self.game.screen.blit(self.label_tokens, (5, 5))
        self.game.screen.blit(self.label_ok, self.rect_label_ok)

        if self.active_input_num_jugadores:
            color = self.color_active
        else:
            color = self.color_passive
        pygame.draw.rect(self.game.screen, color, self.rect_input_num_jugadores, 2)

        text_surface = self.base_font.render(self.texto_num_jugadores, True, (255, 255, 255))
        self.game.screen.blit(text_surface, (self.rect_input_num_jugadores.x + 5, self.rect_input_num_jugadores.y + 5))
        self.rect_input_num_jugadores.width = max(200, text_surface.get_width() + 10)

        for i, rect in enumerate(self.lista_inputs_nombres):

            if self.lista_active_input[i]:
                self.lista_colores[i] = self.color_active
            else:
                self.lista_colores[i] = self.color_passive

            pygame.draw.rect(self.game.screen, self.lista_colores[i], rect, 2)
            nombre_surf = self.base_font.render(self.lista_nombres[i], True, (255, 255, 255))
            self.game.screen.blit(nombre_surf, (self.lista_inputs_nombres[i].x + 5,
                                                self.lista_inputs_nombres[i].y + 5))
            self.lista_inputs_nombres[i].width = max(200, nombre_surf.get_width() + 10)

            self.game.screen.blit(self.lista_label_nombre_jugadores[i], (300, 253 + 50 * i))

        #####################

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
