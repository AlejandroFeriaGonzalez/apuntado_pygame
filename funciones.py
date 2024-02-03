# Libreria de funciones reglas del juego
import pygame

from GLOBAL import *


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join(main_dir, "data", file)
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit(f'Could not load image "{file}" {pygame.get_error()}')
    return surface.convert()


def all_same(items):
    return all(x == items[0] for x in items)


def orden(numerodecarta: list[int]) -> bool:  # regla: JQK A23 son validos

    if 13 in numerodecarta and 1 in numerodecarta:  # creo que solo funciona para la terna QKA
        return True
    """la logica es la siguiente:
    los numeros ya estan ordenados, """


def es_terna(cartas_en_espacios: list[str]) -> bool:  # mismo valor sin importar el palo
    if len(cartas_en_espacios) < 3:
        return False

    lista_cartas = list(map(lambda x: x.removesuffix('2'), cartas_en_espacios))  # quita el 2 al final
    numeros = list(map(int, map(lambda x: x[:-1], lista_cartas)))

    if all_same(numeros) or orden(numeros):
        return True

    return False


def es_escarela(cartas_en_espacios: list[str]) -> bool:
    if len(cartas_en_espacios) < 3:
        return False

    lista_cartas = list(map(lambda x: x.removesuffix('2'), cartas_en_espacios))  # quita el 2 al final

    grupos = list(map(lambda x: x[-1], lista_cartas))

    if all_same(grupos):  # si tiene el mismo palo, verifica que los numeros sea consecutivos
        lista_cartas.sort(key=lambda x: x[:-1])
        numeros = list(map(int, map(lambda x: x[:-1], lista_cartas)))  # ordena por numeros y los convierte a int

        if list(range(min(numeros), max(numeros) + 1)) == numeros or orden(numeros):
            return True

    return False


def es_combinacion_valida(cartas_en_espacios: list[str]) -> bool:
    if es_terna(cartas_en_espacios) or es_escarela(cartas_en_espacios):
        return True
    return False

# for c in lista_cartas_en_espacios:
#     print(c, es_combinacion_valida(c))
