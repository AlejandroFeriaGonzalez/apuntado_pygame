import os
import random
import sys

import pygame
from pygame import Event

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


def main():
    pygame.init()
    fps = pygame.time.Clock()
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 640

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen_rect = screen.get_rect()
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)

    ruta_cartas = os.path.join(main_dir, "data", "Cards")
    pygame.display.set_caption("Move Cards")
    boxes = []
    images = []
    dict_cartas = {}
    list_rect_cartas = []

    for img in os.listdir(ruta_cartas):
        file = os.path.join(main_dir, "data", "Cards", img)
        image = load_image(file)
        object_rect = image.get_rect()
        object_rect.bottomright = (-1, -1)  # se ponen fuera del mapa
        boxes.append(object_rect)
        images.append(image)

        dict_cartas[img.removesuffix(".png")] = (image, object_rect)
        list_rect_cartas.append(object_rect)

    lista_claves = list(dict_cartas.keys())
    carta_activa = None
    nombre_carta_activa = None
    running = True

    mano: list[tuple[pygame.Surface, pygame.Rect]] = random.sample(list(dict_cartas.items()), 10)
    list_cartas_en_juego = None

    i = 10
    for clave, carta in mano:
        carta[1].topleft = (i, 500)
        i += 100

    while running:
        screen.fill(BLACK)
        event: Event

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for num_carta in list_cartas_en_juego:
                        nombre_carta_activa = lista_claves[num_carta]
                        carta = dict_cartas[nombre_carta_activa][1]  # rect
                        if carta.collidepoint(event.pos):
                            carta_activa = carta
                            print(nombre_carta_activa)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    carta_activa = None

            if event.type == pygame.MOUSEMOTION:
                if carta_activa is not None:
                    carta_activa.move_ip(event.rel)
                    # dict_cartas[carta_activa][1].move_ip(event.rel)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # mostrar todas las cartas
        # for image, rect in dict_cartas.values():
        #     screen.blit(image, rect)

        for clave, carta in mano:
            screen.blit(carta[0], carta[1])

        list_cartas_en_juego = screen_rect.collidelistall(list_rect_cartas)
        # print(screen_rect.collidelistall(list_rect_cartas))

        pygame.display.update()
        fps.tick(20)


if __name__ == "__main__":
    main()
