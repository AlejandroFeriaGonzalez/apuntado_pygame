import os

ruta_carpeta = r'C:\Users\Alejandro Feria\PycharmProjects\apuntado\data\copia'

for count, filename in enumerate(os.listdir(ruta_carpeta)):
    nuevo_nombre, extension = os.path.splitext(filename)
    nuevo_nombre_archivo = f"{nuevo_nombre}2{extension}"
    print(nuevo_nombre_archivo)
    os.rename(os.path.join(ruta_carpeta, filename), os.path.join(ruta_carpeta, nuevo_nombre_archivo))

