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

    urls_unicas = list(dict.fromkeys(lista_urlsMund))

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

    urls_unicas = list(dict.fromkeys(lista_urlsPartidos))

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
                tiempo_extra = 0
                penales = 0

                texto_bloque = bloque.get_text()

                extra = re.search(r"\(\s*(\d+\s*-\s*\d+)\s*\)", texto_bloque)

                if extra:
                    tiempo_extra = 1

                pen = re.search(r"(\d+\s*-\s*\d+)\s*por penales", texto_bloque)

                if pen:
                    penales = 1

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


def escanear_info_pos_final(lista_urlsPosFinal):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    urls_unicas = list(dict.fromkeys(lista_urlsPosFinal))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    for url in urls_unicas:

        print("\n====================================")
        print(f"URL: {url}")
        print("====================================")

        try:

            r = requests.get(url, headers=headers)
            r.encoding = "utf-8"

            soup = BeautifulSoup(r.text, "html.parser")

            tablas = soup.find_all("table")

            for tabla in tablas:

                filas = tabla.find_all("tr")

                for fila in filas[1:]:

                    celdas = fila.find_all("td")

                    if len(celdas) < 11:
                        continue

                    # POSICION
                    posicion_txt = celdas[0].text.strip()

                    posicion = re.sub(r"\D", "", posicion_txt)

                    posicion = int(posicion) if posicion else None

                    # ETAPA
                    etapa = celdas[2].text.strip() or None

                    # NUMEROS
                    def parse_int(valor):
                        try:
                            return int(valor.strip())
                        except:
                            return None

                    pts = parse_int(celdas[3].text)
                    pj = parse_int(celdas[4].text)
                    pg = parse_int(celdas[5].text)
                    pe = parse_int(celdas[6].text)
                    pp = parse_int(celdas[7].text)
                    gf = parse_int(celdas[8].text)
                    gc = parse_int(celdas[9].text)
                    dif = parse_int(celdas[10].text)

                    # CAMPEON / SUBCAMPEON
                    es_campeon = None
                    es_subcampeon = None

                    if posicion == 1:
                        es_campeon = 1
                        es_subcampeon = 0
                    elif posicion == 2:
                        es_campeon = 0
                        es_subcampeon = 1
                    else:
                        es_campeon = 0
                        es_subcampeon = 0

                    print("POSICION:", posicion)
                    print("ETAPA:", etapa)
                    print("PTS:", pts)
                    print("PJ:", pj)
                    print("PG:", pg)
                    print("PE:", pe)
                    print("PP:", pp)
                    print("GF:", gf)
                    print("GC:", gc)
                    print("DIF:", dif)
                    print("ES_CAMPEON:", es_campeon)
                    print("ES_SUBCAMPEON:", es_subcampeon)

                    print("----------------------------")

        except Exception as e:

            print("Error:", e)

        time.sleep(1)


def escanear_info_grupos(lista_urlsGrupos):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # eliminar duplicados sin perder orden
    urls_unicas = list(dict.fromkeys(lista_urlsGrupos))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    for url in urls_unicas:

        print("\n====================================")
        print(f"URL: {url}")
        print("====================================")

        try:

            r = requests.get(url, headers=headers)
            r.encoding = "utf-8"

            soup = BeautifulSoup(r.text, "html.parser")

            enlaces = soup.find_all("a", href=True)

            urls_grupos = []

            for enlace in enlaces:

                href = enlace["href"]

                if "_grupo_" in href:

                    if href.startswith("../"):
                        href = "https://www.losmundialesdefutbol.com/" + href.replace("../", "")

                    elif not href.startswith("http"):
                        href = "https://www.losmundialesdefutbol.com/mundiales/" + href

                    urls_grupos.append(href)

            # función para ordenar correctamente grupos numéricos o alfabéticos
            def ordenar_grupo(url):

                match = re.search(r'grupo_([^\.]+)', url)

                if not match:
                    return (2, url)

                valor = match.group(1)

                if valor.isdigit():
                    return (0, int(valor))

                return (1, valor)

            urls_grupos = sorted(set(urls_grupos), key=ordenar_grupo)

            print(f"Grupos encontrados: {len(urls_grupos)}")

            if len(urls_grupos) == 0:
                print("Este mundial no tiene fase de grupos")
                continue

            # analizar cada grupo
            for url_grupo in urls_grupos:

                print("\n--- Analizando grupo ---")
                print(url_grupo)

                r2 = requests.get(url_grupo, headers=headers)
                r2.encoding = "utf-8"

                soup2 = BeautifulSoup(r2.text, "html.parser")

                titulo = soup2.title.text.strip()

                # Ejemplo:
                # Mundial 1930 de Fútbol - Grupo 1, Primera Ronda

                if "-" in titulo:

                    parte = titulo.split("-")[1].strip()

                    if "," in parte:

                        nombre_grupo, fase = parte.split(",")

                        nombre_grupo = nombre_grupo.strip()
                        fase = fase.strip()

                    else:

                        nombre_grupo = parte.strip()
                        fase = None

                else:

                    nombre_grupo = None
                    fase = None

                print("NOMBRE_GRUPO:", nombre_grupo)
                print("FASE:", fase)

                print("----------------------")

        except Exception as e:

            print("Error:", e)

        time.sleep(1)


def escanear_info_participacion_grupo(lista_urlsParticipacionGr):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # eliminar duplicados sin perder orden
    urls_unicas = list(dict.fromkeys(lista_urlsParticipacionGr))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    def parse_int(valor):
        try:
            return int(valor.strip())
        except:
            return None

    for url in urls_unicas:

        print("\n====================================")
        print(f"URL: {url}")
        print("====================================")

        try:

            r = requests.get(url, headers=headers)
            r.encoding = "utf-8"

            soup = BeautifulSoup(r.text, "html.parser")

            enlaces = soup.find_all("a", href=True)

            urls_grupos = []

            for enlace in enlaces:

                href = enlace["href"]

                if "_grupo_" in href:

                    if href.startswith("../"):
                        href = "https://www.losmundialesdefutbol.com/" + href.replace("../", "")

                    elif not href.startswith("http"):
                        href = "https://www.losmundialesdefutbol.com/mundiales/" + href

                    urls_grupos.append(href)

            # ordenar grupos correctamente
            def ordenar_grupo(url):
                match = re.search(r'grupo_([^\.]+)', url)

                if not match:
                    return (2, url)

                valor = match.group(1)

                if valor.isdigit():
                    return (0, int(valor))

                return (1, valor)

            urls_grupos = sorted(set(urls_grupos), key=ordenar_grupo)

            print(f"Grupos encontrados: {len(urls_grupos)}")

            if len(urls_grupos) == 0:
                print("Este mundial no tiene fase de grupos")
                continue

            # analizar cada grupo
            for url_grupo in urls_grupos:

                print("\n--- Analizando grupo ---")
                print(url_grupo)

                r2 = requests.get(url_grupo, headers=headers)
                r2.encoding = "utf-8"

                soup2 = BeautifulSoup(r2.text, "html.parser")

                tabla = soup2.find("table")

                if not tabla:
                    print("No se encontró tabla de posiciones")
                    continue

                filas = tabla.find_all("tr")

                for fila in filas[1:]:

                    celdas = fila.find_all("td")

                    if len(celdas) < 11:
                        continue

                    # POSICION
                    posicion_txt = celdas[0].text.strip()
                    posicion_grupo = re.sub(r"\D", "", posicion_txt)
                    posicion_grupo = int(posicion_grupo) if posicion_grupo else None

                    # ESTADISTICAS
                    pts = parse_int(celdas[2].text)
                    pj = parse_int(celdas[3].text)
                    pg = parse_int(celdas[4].text)
                    pe = parse_int(celdas[5].text)
                    pp = parse_int(celdas[6].text)
                    gf = parse_int(celdas[7].text)
                    gc = parse_int(celdas[8].text)
                    dif = parse_int(celdas[9].text)

                    # CLASIFICO
                    clas_txt = celdas[10].text.strip().lower()

                    if clas_txt == "si":
                        clasifico = 1
                    elif clas_txt == "no":
                        clasifico = 0
                    else:
                        clasifico = None

                    # PRINT (luego lo usarás para insertar en BD)
                    print("POSICION_GRUPO:", posicion_grupo)
                    print("PTS:", pts)
                    print("PJ:", pj)
                    print("PG:", pg)
                    print("PE:", pe)
                    print("PP:", pp)
                    print("GF:", gf)
                    print("GC:", gc)
                    print("DIF:", dif)
                    print("CLASIFICO:", clasifico)

                    print("----------------------------")

        except Exception as e:

            print("Error:", e)

        time.sleep(1)

def escanear_info_resultado_penales(lista_urlsResPenales):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    urls_unicas = list(dict.fromkeys(lista_urlsResPenales))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    for url in urls_unicas:

        print("\n====================================")
        print(f"URL: {url}")
        print("====================================")

        try:

            r = requests.get(url, headers=headers)
            r.encoding = "utf-8"

            soup = BeautifulSoup(r.text, "html.parser")

            # cada bloque game es un partido
            partidos = soup.find_all("div", class_="game")

            for partido in partidos:

                bloque_partido = partido.find_parent("div", class_="rd-100")

                if not bloque_partido:
                    continue

                texto = bloque_partido.get_text(" ", strip=True)

                if "penales" not in texto.lower():

                    print("No existen penales para este partido")
                    print("----------------------")
                    continue

                marcador = None

                for div in bloque_partido.find_all("div"):

                    if div.text and " - " in div.text:

                        siguiente = div.find_next("div")

                        if siguiente and "penales" in siguiente.text.lower():

                            marcador = div.text.strip()
                            break

                if marcador:

                    match = re.search(r'(\d+)\s*-\s*(\d+)', marcador)

                    if match:

                        penales_local = int(match.group(1))
                        penales_visita = int(match.group(2))

                        print("PENALES_LOCAL:", penales_local)
                        print("PENALES_VISITA:", penales_visita)

                    else:

                        print("No se pudo interpretar el marcador de penales")

                else:

                    print("No existen penales para este partido")

                print("----------------------")

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
    "https://www.losmundialesdefutbol.com/mundiales/1930_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2018_resultados.php"
]   

lista_urlsPosFinal = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1934_posiciones_finales.php"
]

lista_urlsGrupos = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1934_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1938_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1950_mundial.php"
]

lista_urlsParticipacionGr = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1934_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1938_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1950_mundial.php"
]

lista_urlsResPenales = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2018_resultados.php"
] 

print("\n--- INICIANDO MAPEO DE ESTRUCTURA ---")

#escanear_nuevas_ramas(lista_urls)

#escanear_info_mundial(lista_urlsMund)
#escanear_info_partido(lista_urlsPartidos)
#escanear_info_pos_final(lista_urlsPosFinal)
#escanear_info_grupos(lista_urlsGrupos)
#escanear_info_participacion_grupo(lista_urlsParticipacionGr)
#escanear_info_resultado_penales(lista_urlsResPenales)

print("\n--- ESCANEO FINALIZADO ---")