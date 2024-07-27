import os
import random
import sys
from itertools import chain

import pygame

from GLOBAL import *
from Ganar import Ganar
from funciones import *
from Game import Game

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
