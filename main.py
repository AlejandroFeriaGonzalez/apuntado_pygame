import os
import random
import sys

import pygame

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
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 640

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    screen_rect = screen.get_rect()

    ruta_cartas = os.path.join(main_dir, "data", "Cards")
    pygame.display.set_caption("Move Cards")
    boxes = []
    dict_cartas = {}
    list_rect_cartas = []

    mesa_verde = pygame.Surface((800, 200))
    mesa_verde.fill("green")
    mesa_verde_rect = mesa_verde.get_rect()
    mesa_verde_rect.topleft = (0, 440)

    for img in os.listdir(ruta_cartas):
        file = os.path.join(main_dir, "data", "Cards", img)
        image = load_image(file)
        object_rect = image.get_rect()
        object_rect.bottomright = (-1, -1)  # se ponen fuera del mapa
        boxes.append(object_rect)

        dict_cartas[img.removesuffix(".png")] = (image, object_rect)
        list_rect_cartas.append(object_rect)

    lista_claves = list(dict_cartas.keys())
    carta_activa = None
    nombre_carta_activa = None
    running = True

    mano = None
    list_cartas_en_juego = None

    button_text = dict_cartas["backB"][0]
    button_rect = button_text.get_rect(center=(100, 100))
    was_pressed = False

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.fill((0, 0, 0))
        screen.blit(mesa_verde, mesa_verde_rect)


        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for num_carta in list_cartas_en_juego:
                        nombre_carta_activa = lista_claves[num_carta]
                        carta = dict_cartas[nombre_carta_activa][1]  # rect
                        if carta.collidepoint(event.pos):
                            carta_activa = carta
                            # print(nombre_carta_activa)

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    carta_activa = None

            if event.type == pygame.MOUSEMOTION:
                if carta_activa is not None:
                    carta_activa.move_ip(event.rel)

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if mano:
            for clave, carta in mano:
                screen.blit(carta[0], carta[1])

        list_cartas_en_juego = screen_rect.collidelistall(list_rect_cartas)
        # for num_carta in list_cartas_en_juego:
        #     nombre_carta_activa = lista_claves[num_carta]
        #     print(nombre_carta_activa, end=", ")  # rect
        # print()

        list_cartas_en_mesa = mesa_verde_rect.collidelistall(list_rect_cartas)
        for num_carta in list_cartas_en_mesa:
            nombre_carta_activa = lista_claves[num_carta]
            print(nombre_carta_activa, end=", ")  # rect
        print()

        # * boton

        if button_rect.collidepoint(mouse_x, mouse_y):
            if pygame.mouse.get_pressed()[0] and not was_pressed:

                if mano:
                    for clave, carta in mano:
                        carta[1].bottomright = (-1, -1)

                mano = random.sample(list(dict_cartas.items())[:-2], 10)
                i = 10
                for clave, carta in mano:
                    carta[1].topleft = (i, 500)
                    i += 100

        was_pressed = pygame.mouse.get_pressed()[0]

        screen.blit(button_text, button_rect)


        pygame.display.update()
        fps.tick(20)


if __name__ == "__main__":
    main()
