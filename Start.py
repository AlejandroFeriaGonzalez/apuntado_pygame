import sys

import pygame

from GLOBAL import *
from Game import Game
from Mesa import Mesa


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
