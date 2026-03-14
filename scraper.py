import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import re
from datetime import datetime
import requests
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

def convertir_fecha(fecha_txt):

    meses = {
        "enero":"January","febrero":"February","marzo":"March","abril":"April",
        "mayo":"May","junio":"June","julio":"July","agosto":"August",
        "septiembre":"September","octubre":"October","noviembre":"November","diciembre":"December"
    }

    try:
        for esp,eng in meses.items():
            fecha_txt = fecha_txt.replace(esp,eng)

        fecha = datetime.strptime(fecha_txt,"%d de %B de %Y")
        return fecha.strftime("%Y-%m-%d")
    except:
        return ""

def crear_session():

    session = requests.Session()

    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500,502,503,504]
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    return session


def crear_session2():

    session = requests.Session()

    retry = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500,502,503,504]
    )

    adapter = HTTPAdapter(max_retries=retry)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # HEADERS DE NAVEGADOR REAL
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Connection": "keep-alive"
    })

    return session


# Extra para extraer jugador de forma mas rapida
def scrapear_jugador(url_jugador, session):

    resultados = []

    try:

        r = session.get(url_jugador, timeout=10)

        soup = BeautifulSoup(r.text, "html.parser")

        h3 = soup.find("h3", string=re.compile("Detalle de Mundiales"))

        if not h3:
            return resultados

        tabla = h3.find_next("table")

        filas = tabla.find_all("tr")

        for fila in filas:

            tds = fila.find_all("td")

            if len(tds) < 15:
                continue

            try:

                texto = tds[1].get_text(strip=True)
                numero = re.search(r"\d+", texto)

                num_camiseta = int(numero.group()) if numero else None
                partidos_jugados = int(tds[3].text.strip())
                fue_capitan = int(tds[5].text.strip())
                goles = int(tds[7].text.strip())
                tarjetas_amarillas = int(tds[9].text.strip())
                tarjetas_rojas = int(tds[10].text.strip())
                pos_final_seleccion = int(tds[14].text.strip())

                resultados.append({
                    "num_camiseta": num_camiseta,
                    "partidos_jugados": partidos_jugados,
                    "goles": goles,
                    "tarjetas_amarillas": tarjetas_amarillas,
                    "tarjetas_rojas": tarjetas_rojas,
                    "fue_capitan": fue_capitan,
                    "pos_final_seleccion": pos_final_seleccion
                })

            except:
                continue

    except:
        pass

    return resultados

# Para tabla jugador
def scrapear_perfil_jugador(url_jugador, session):

    try:

        r = session.get(url_jugador, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        nombre = ""
        fecha = ""
        lugar = ""
        posicion = ""
        altura = ""
        apodo = ""
        numeros = ""
        pais = ""

        # nombre fallback
        h2 = soup.find("h2")

        if h2:
            nombre = h2.text.strip()

        tabla = soup.find("table")

        if tabla:

            for fila in tabla.find_all("tr"):

                tds = fila.find_all("td")

                if len(tds) < 2:
                    continue

                campo = tds[0].text.strip()
                valor = tds[1].text.strip()

                if "Nombre completo" in campo:
                    nombre = valor

                elif "Fecha de Nacimiento" in campo:
                    fecha = convertir_fecha(valor)

                elif "Lugar de nacimiento" in campo:
                    lugar = valor

                elif "Posición" in campo:
                    posicion = valor

                elif "Altura" in campo:
                    altura = valor

                elif "Apodo" in campo:
                    apodo = valor

                elif "Números de camiseta" in campo:
                    numeros = valor

        sel = soup.find("h3", string=re.compile("Selección"))

        if sel:

            a = sel.find_next("a")

            if a:
                pais = a.text.strip()

        return [
            nombre,
            fecha,
            lugar,
            posicion,
            altura,
            apodo,
            pais,
            numeros,
            url_jugador
        ]

    except:
        return None


# Tabla munial
def escanear_info_mundial(lista_urlsMund):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    urls_unicas = list(dict.fromkeys(lista_urlsMund))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    # -------------------------------------
    # CREAR RUTA DEL CSV
    # -------------------------------------

    carpeta = "archivos_carga"
    os.makedirs(carpeta, exist_ok=True)

    ruta_csv = os.path.join(carpeta, "mundial.csv")

    # -------------------------------------
    # CREAR CSV Y ESCRIBIR ENCABEZADOS
    # -------------------------------------

    with open(ruta_csv, mode="w", newline="", encoding="utf-8") as archivo:

        writer = csv.writer(archivo)

        writer.writerow([
            "anio",
            "fecha_inicio",
            "fecha_fin",
            "num_equipos",
            "num_partidos",
            "total_goles"
        ])

        # -------------------------------------
        # SCRAPING
        # -------------------------------------

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

                anio = int(match.group())

                texto = soup.get_text()

                # -------- NUMEROS --------

                selecciones = re.search(r"Selecciones:\s*(\d+)", texto)
                partidos = re.search(r"Partidos:\s*(\d+)", texto)
                goles = re.search(r"Goles:\s*(\d+)", texto)

                selecciones = int(selecciones.group(1)) if selecciones else None
                partidos = int(partidos.group(1)) if partidos else None
                goles = int(goles.group(1)) if goles else None

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
                    fecha_inicio = None
                    fecha_fin = None

                # -------- GUARDAR EN CSV --------

                writer.writerow([
                    anio,
                    fecha_inicio,
                    fecha_fin,
                    selecciones,
                    partidos,
                    goles
                ])

                # -------- PRINT --------

                #print("AÑO:", anio)
                #print("NUM_EQUIPOS:", selecciones)
                #print("NUM_PARTIDOS:", partidos)
                #print("GOLES_TOTALES:", goles)
                #print("FECHA_INICIO:", fecha_inicio)
                #print("FECHA_FIN:", fecha_fin)

            except Exception as e:
                print("Error al analizar la página:", e)

            time.sleep(1)

    print(f"\nCSV generado en: {ruta_csv}")
        
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


def escanear_info_premio(lista_urlsPremios):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    urls_unicas = list(dict.fromkeys(lista_urlsPremios))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    for url in urls_unicas:

        print("\n====================================")
        print(f"URL: {url}")
        print("====================================")

        try:

            r = requests.get(url, headers=headers)
            r.encoding = "utf-8"

            soup = BeautifulSoup(r.text, "html.parser")

            premios = soup.find_all("p", class_="negri")

            for premio in premios:

                categoria = premio.text.strip()

                # -------- EQUIPO IDEAL --------
                if categoria == "Equipo Ideal":

                    contenedor = premio.find_parent("div", class_="overflow-x-auto")

                    posiciones = contenedor.find_all("div", class_=re.compile("rd-100-25"))

                    for pos in posiciones:

                        texto = pos.get_text()

                        if ":" not in texto:
                            continue

                        tipo = texto.split(":")[0].strip().lower()

                        jugadores = pos.find_all("a")

                        for _ in jugadores:

                            print("NOMBRE_PREMIO:", "Equipo Ideal")
                            print("TIPO_PREMIO:", tipo)
                            print("-----------------------------------")

                    continue

                # -------- PREMIOS NORMALES --------

                ganador_tag = premio.find_next("p", class_="margen-b0")

                if not ganador_tag:
                    continue

                texto = ganador_tag.get_text(strip=True)

                if texto == "-":

                    print(f"No se otorgó premio para categoria: {categoria}")
                    print("-----------------------------------")
                    continue

                if "Balón" in categoria:
                    tipo_premio = "mejor jugador"

                elif "Botín" in categoria:
                    tipo_premio = "goleador"

                elif "Guante de Oro" in categoria:
                    tipo_premio = "mejor arquero"

                elif "Mejor Jugador Joven" in categoria:
                    tipo_premio = "jugador"

                elif "FIFA Fair Play" in categoria:
                    tipo_premio = "equipo"

                else:
                    tipo_premio = None

                print("NOMBRE_PREMIO:", categoria)
                print("TIPO_PREMIO:", tipo_premio)
                print("-----------------------------------")

        except Exception as e:
            print("Error:", e)

        time.sleep(1)


def escanear_info_participacion_jugador_mundial(lista_urls):

    session = crear_session()

    jugadores_global = set()

    print("\n--- MAPEO DE JUGADORES ---\n")

    # ----------------------------------------
    # RECOLECTAR TODOS LOS JUGADORES
    # ----------------------------------------

    for url_mundial in lista_urls:

        try:

            r = session.get(url_mundial, timeout=10)

            soup = BeautifulSoup(r.text, "html.parser")

            h3 = soup.find("h3", string=re.compile("Grupos y Planteles"))

            if not h3:
                continue

            tabla = h3.find_next("table")

            for a in tabla.find_all("a", href=True):

                if "planteles" not in a["href"]:
                    continue

                url_plantel = "https://www.losmundialesdefutbol.com/" + a["href"].replace("../","")

                r2 = session.get(url_plantel, timeout=10)

                soup2 = BeautifulSoup(r2.text, "html.parser")

                jugadores = soup2.select("a[href*='../jugadores']")

                for j in jugadores:

                    url_jugador = "https://www.losmundialesdefutbol.com/jugadores/" + j["href"].split("/")[-1]

                    jugadores_global.add(url_jugador)

        except:
            continue

    print("Jugadores únicos encontrados:", len(jugadores_global))

    # ----------------------------------------
    # SCRAPING PARALELO
    # ----------------------------------------

    resultados_totales = []

    print("\n--- SCRAPING PARALELO ---\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:

        futures = [
            executor.submit(scrapear_jugador, jugador, session)
            for jugador in jugadores_global
        ]

        for future in concurrent.futures.as_completed(futures):

            datos = future.result()

            if datos:
                resultados_totales.extend(datos)

    # ----------------------------------------
    # IMPRIMIR RESULTADOS
    # ----------------------------------------

    print("\n--- RESULTADOS ---\n")

    for r in resultados_totales:

        print("--------------------------------")
        print("NUM_CAMISETA:", r["num_camiseta"])
        print("PARTIDOS_JUGADOS:", r["partidos_jugados"])
        print("GOLES:", r["goles"])
        print("TARJETAS_AMARILLAS:", r["tarjetas_amarillas"])
        print("TARJETAS_ROJAS:", r["tarjetas_rojas"])
        print("FUE_CAPITAN:", r["fue_capitan"])
        print("POS_FINAL_SELECCION:", r["pos_final_seleccion"])
        print("--------------------------------")


def escanear_info_jugador(lista_urlsMund):

    session = crear_session2()

    jugadores_global = set()

    print("\n--- MAPEO DE JUGADORES (DEBUG) ---\n")

    for url_mundial in lista_urlsMund:

        print("\n==============================")
        print("MUNDIAL:", url_mundial)

        try:

            r = session.get(url_mundial, timeout=10)

            print("Status code:", r.status_code)

            soup = BeautifulSoup(r.text, "html.parser")

            # ------------------------------------
            # BUSCAR PLANTELES
            # ------------------------------------

            planteles = soup.select("a[href*='planteles']")

            print("Links que contienen 'planteles':", len(planteles))

            for a in planteles:

                print("Link detectado:", a["href"])

            # ------------------------------------

            for a in planteles:

                if "jugadores.php" not in a["href"]:
                    continue

                url_plantel = "https://www.losmundialesdefutbol.com/" + a["href"].replace("../","")

                print("\nEntrando a plantel:", url_plantel)

                try:

                    r2 = session.get(url_plantel, timeout=10)

                    print("Status plantel:", r2.status_code)

                    soup2 = BeautifulSoup(r2.text, "html.parser")

                    jugadores = soup2.select("a[href*='../jugadores']")

                    print("Jugadores encontrados en plantel:", len(jugadores))

                    for j in jugadores:

                        url_jugador = "https://www.losmundialesdefutbol.com/jugadores/" + j["href"].split("/")[-1]

                        print("Jugador detectado:", url_jugador)

                        jugadores_global.add(url_jugador)

                except Exception as e:

                    print("ERROR entrando a plantel:", e)

        except Exception as e:

            print("ERROR cargando mundial:", e)

    print("\n==============================")
    print("Jugadores únicos encontrados:", len(jugadores_global))


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
    "https://www.losmundialesdefutbol.com/mundiales/1934_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1938_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1950_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1954_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1958_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1962_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1966_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1970_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1974_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1978_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1982_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1986_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1990_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1994_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/1998_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/2002_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/2006_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/2010_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/2014_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/2018_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_mundial.php"
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

lista_urlsPremios = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_premios.php",
    "https://www.losmundialesdefutbol.com/mundiales/2018_premios.php"
]

lista_urlsPremios = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_premios.php",
    "https://www.losmundialesdefutbol.com/mundiales/2018_premios.php"
]

lista_urlsParticipacionJugadorMundial = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_mundial.php"
]

print("\n--- INICIANDO MAPEO DE ESTRUCTURA ---")

#escanear_nuevas_ramas(lista_urls)

#escanear_info_mundial(lista_urlsMund)
#escanear_info_partido(lista_urlsPartidos)
#escanear_info_pos_final(lista_urlsPosFinal)
#escanear_info_grupos(lista_urlsGrupos)
#escanear_info_participacion_grupo(lista_urlsParticipacionGr)
#escanear_info_resultado_penales(lista_urlsResPenales)
#escanear_info_premio(lista_urlsPremios)
#escanear_info_participacion_jugador_mundial(lista_urlsParticipacionJugadorMundial)
#escanear_info_jugador(lista_urlsMund)

print("\n--- ESCANEO FINALIZADO ---")