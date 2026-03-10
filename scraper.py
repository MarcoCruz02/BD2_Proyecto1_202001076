import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime

# Tabla munial
def escanear_info_mundial(lista_urlsMund):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    urls_unicas = list(set(lista_urlsMund))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    for url in urls_unicas:

        print("\n====================================")
        print(f"URL: {url}")
        print("====================================")

        try:

            r = requests.get(url, headers=headers)
            r.encoding = "utf-8"

            soup = BeautifulSoup(r.text, "html.parser")

            # -------- AÑO DESDE TITLE --------
            titulo = soup.title.text

            match = re.search(r"\b(19|20)\d{2}\b", titulo)

            if not match:
                print("No se encontró año en el título")
                continue

            anio = match.group()

            texto = soup.get_text()

            # -------- CAMPEON --------
            campeon_tag = soup.find("strong", string="Campeón")

            if campeon_tag:
                campeon = campeon_tag.find_next("a").text.strip()
            else:
                campeon = "No encontrado"

            # -------- NUMEROS --------
            selecciones = re.search(r"Selecciones:\s*(\d+)", texto)
            partidos = re.search(r"Partidos:\s*(\d+)", texto)
            goles = re.search(r"Goles:\s*(\d+)", texto)

            selecciones = selecciones.group(1) if selecciones else "?"
            partidos = partidos.group(1) if partidos else "?"
            goles = goles.group(1) if goles else "?"

            # -------- URL RESULTADOS --------
            base = "https://www.losmundialesdefutbol.com/mundiales/"
            url_resultados = f"{base}{anio}_resultados.php"

            r2 = requests.get(url_resultados, headers=headers)
            r2.encoding = "utf-8"

            soup2 = BeautifulSoup(r2.text, "html.parser")

            fechas = []

            for h3 in soup2.find_all("h3"):

                if "Fecha:" in h3.text:

                    fecha_txt = h3.find("strong").text.strip()

                    fecha = datetime.strptime(fecha_txt, "%d-%b-%Y")

                    fechas.append(fecha)

            if fechas:
                fecha_inicio = min(fechas).strftime("%Y-%m-%d")
                fecha_fin = max(fechas).strftime("%Y-%m-%d")
            else:
                fecha_inicio = "?"
                fecha_fin = "?"

            # -------- PRINT --------

            print("AÑO:", anio)
            print("CAMPEON:", campeon)
            print("NUM_EQUIPOS:", selecciones)
            print("NUM_PARTIDOS:", partidos)
            print("GOLES_TOTALES:", goles)
            print("FECHA_INICIO:", fecha_inicio)
            print("FECHA_FIN:", fecha_fin)

        except Exception as e:
            print("Error al analizar la página:", e)

        time.sleep(1)
        
# Tabla partidos
def escanear_info_partido(lista_urlsPartidos):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    urls_unicas = list(set(lista_urlsPartidos))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    for url in urls_unicas:

        print("\n====================================")
        print(f"URL: {url}")
        print("====================================")

        try:

            r = requests.get(url, headers=headers)
            r.encoding = "utf-8"

            soup = BeautifulSoup(r.text, "html.parser")

            fecha_actual = None

            bloques = soup.find_all("div", class_=re.compile("overflow-x-auto"))

            for bloque in bloques:

                # ---------------- FECHA ----------------
                h3 = bloque.find("h3")

                if h3 and "Fecha:" in h3.text:

                    fecha_txt = h3.find("strong").text.strip()

                    fecha_actual = datetime.strptime(
                        fecha_txt, "%d-%b-%Y"
                    ).strftime("%Y-%m-%d")

                # ---------------- NUMERO PARTIDO ----------------
                num_tag = bloque.find("strong")

                if not num_tag:
                    continue

                num_partido = num_tag.text.strip()

                if not num_partido.isdigit():
                    continue

                num_partido = int(num_partido)

                # ---------------- FASE ----------------
                fase_tag = bloque.find("a", href=re.compile("grupo|final|fase"))

                if fase_tag:
                    fase = fase_tag.text.strip()
                else:
                    fase = "?"

                # ---------------- RESULTADO ----------------
                marcador = bloque.find("a", href=re.compile("../partidos"))

                if not marcador:
                    continue

                resultado = marcador.text.strip()

                goles = re.findall(r"\d+", resultado)

                if len(goles) >= 2:
                    goles_local = int(goles[0])
                    goles_visitante = int(goles[1])
                else:
                    continue

                # ---------------- TIEMPO EXTRA ----------------
                tiempo_extra = -1
                penales = -1

                texto_bloque = bloque.get_text()

                extra = re.search(r"\(\s*(\d+\s*-\s*\d+)\s*\)", texto_bloque)

                if extra:
                    tiempo_extra = extra.group(1)

                pen = re.search(r"(\d+\s*-\s*\d+)\s*por penales", texto_bloque)

                if pen:
                    penales = pen.group(1)

                # ---------------- PRINT ----------------

                print("NUM_PARTIDO:", num_partido)
                print("FECHA:", fecha_actual)
                print("FASE:", fase)
                print("GOLES_LOCAL:", goles_local)
                print("GOLES_VISITANTE:", goles_visitante)
                print("TIEMPO_EXTRA:", tiempo_extra)
                print("PENALES:", penales)
                print("-----------------------------------")

        except Exception as e:
            print("Error:", e)

        time.sleep(1)

def escanear_nuevas_ramas(urls):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    urls_unicas = list(set(urls))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    for url in urls_unicas:

        # Detectar categoría
        partes_url = url.split("/")
        if len(partes_url) > 3:
            categoria = partes_url[-2].upper()
        else:
            categoria = "GENERAL"

        print("\n====================================")
        print(f"CATEGORIA: {categoria}")
        print(f"URL: {url}")
        print("====================================")

        try:

            respuesta = requests.get(url, headers=headers, timeout=5)
            respuesta.encoding = "utf-8"

            if respuesta.status_code != 200:
                print("Error HTTP:", respuesta.status_code)
                continue

            soup = BeautifulSoup(respuesta.text, "html.parser")

            tablas = soup.find_all("table")

            print(f"Tablas detectadas: {len(tablas)}")

            for i, tabla in enumerate(tablas, start=1):

                print(f"\n--- TABLA {i} ---")

                filas = tabla.find_all("tr")

                if len(filas) < 2:
                    print("Tabla ignorada (sin datos suficientes)")
                    continue

                # Cabeceras
                cabeceras = [
                    " ".join(celda.text.split())
                    for celda in filas[0].find_all(["th", "td"])
                    if celda.text.strip()
                ]

                if not cabeceras:
                    print("No se detectaron atributos")
                    continue

                print("ATRIBUTOS:")
                for c in cabeceras:
                    print(" -", c)

                # Buscar primer registro real
                registro = []

                for fila in filas[1:]:
                    celdas = [
                        " ".join(td.text.split())
                        for td in fila.find_all(["td", "th"])
                        if td.text.strip()
                    ]

                    if celdas:
                        registro = celdas
                        break

                if registro:
                    print("\nREGISTRO EJEMPLO:")
                    for r in registro:
                        print(" >", r)
                else:
                    print("No se encontró ejemplo de datos")

        except Exception as e:
            print("Error al analizar la página:", e)

        # Pequeña pausa para no saturar el servidor
        time.sleep(1)


# ---- LISTA DE URLs ----

lista_urls = [
    "https://www.losmundialesdefutbol.com/mundiales.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_mundial.php",
    "https://www.losmundialesdefutbol.com/selecciones/argentina_seleccion.php",
    "https://www.losmundialesdefutbol.com/estadisticas/tabla_de_posiciones.php",
    "https://www.losmundialesdefutbol.com/selecciones/argentina_goleadores.php",
    "https://www.losmundialesdefutbol.com/selecciones/argentina_mundiales.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_premios.php",
    "https://www.losmundialesdefutbol.com/jugadores/lionel_messi.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_goleadores.php",
    "https://www.losmundialesdefutbol.com/historial/argentina_vs_francia.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_fase_final.php",
    "https://www.losmundialesdefutbol.com/historial/holanda_vs_estados_unidos.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_posiciones_finales.php"
]

lista_urlsMund = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1934_mundial.php"
]

lista_urlsPartidos = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_resultados.php"
]   

print("\n--- INICIANDO MAPEO DE ESTRUCTURA ---")

#escanear_nuevas_ramas(lista_urls)
escanear_info_mundial(lista_urlsMund)
escanear_info_partido(lista_urlsPartidos)

print("\n--- ESCANEO FINALIZADO ---")