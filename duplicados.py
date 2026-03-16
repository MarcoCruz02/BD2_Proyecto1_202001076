import csv
import os

# Rutas de archivos
carpeta = 'archivos_carga'
archivo_entrada = os.path.join(carpeta, 'jugador.csv')
archivo_salida = os.path.join(carpeta, 'jugadordepurado.csv')

# Set para detectar duplicados
personas_unicas = set()

# Lista para guardar filas únicas
filas_unicas = []

# Leer el CSV original
with open(archivo_entrada, newline='', encoding='utf-8') as csvfile:
    lector = csv.DictReader(csvfile)
    encabezados = lector.fieldnames  # Guardamos los nombres de las columnas
    
    for fila in lector:
        clave = (fila['nombre_completo'].strip(), fila['fecha_nacimiento'].strip())
        if clave not in personas_unicas:
            personas_unicas.add(clave)
            filas_unicas.append(fila)  # Guardamos la fila completa

# Escribir el nuevo CSV depurado
with open(archivo_salida, 'w', newline='', encoding='utf-8') as csvfile:
    escritor = csv.DictWriter(csvfile, fieldnames=encabezados)
    escritor.writeheader()
    escritor.writerows(filas_unicas)

print(f"Depuración completada. Se guardaron {len(filas_unicas)} filas únicas en '{archivo_salida}'.")