from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import re
import time
import csv
import os
import random


def escanear_info_participacion_grupo(lista_urlsParticipacionGr):

    urls_unicas = list(dict.fromkeys(lista_urlsParticipacionGr))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    # -------------------------------------
    # CONFIGURAR EDGE (ANTI-BLOQUEO)
    # -------------------------------------

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--log-level=3")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Edge(
        service=Service("msedgedriver.exe"),
        options=options
    )

    # -------------------------------------
    # CSV
    # -------------------------------------

    archivo_csv = "participacion_grupo.csv"
    archivo_existe = os.path.isfile(archivo_csv)

    with open(archivo_csv, "a", newline="", encoding="utf-8") as archivo:

        writer = csv.writer(archivo)

        if not archivo_existe:
            writer.writerow([
                "anio_mundial",
                "nombre_grupo",
                "nombre_pais",
                "posicion_grupo",
                "pts",
                "pj",
                "pg",
                "pe",
                "pp",
                "gf",
                "gc",
                "dif",
                "clasifico"
            ])

        # -------------------------------------
        # FUNCIONES AUXILIARES
        # -------------------------------------

        def parse_int(valor):
            try:
                return int(valor.strip())
            except:
                return None

        def esperar():
            time.sleep(random.uniform(2, 4))  # comportamiento humano

        # -------------------------------------
        # SCRAPING
        # -------------------------------------

        for url in urls_unicas:

            try:
                driver.get(url)
                esperar()

                soup = BeautifulSoup(driver.page_source, "html.parser")

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

                # -------- ORDENAR --------
                def ordenar_grupo(url):
                    match = re.search(r'grupo_([^\.]+)', url)

                    if not match:
                        return (2, url)

                    valor = match.group(1)

                    if valor.isdigit():
                        return (0, int(valor))

                    return (1, valor)

                urls_grupos = sorted(set(urls_grupos), key=ordenar_grupo)

                if len(urls_grupos) == 0:
                    continue

                # -------------------------------------
                # ANALIZAR CADA GRUPO
                # -------------------------------------

                for url_grupo in urls_grupos:

                    driver.get(url_grupo)
                    esperar()

                    soup2 = BeautifulSoup(driver.page_source, "html.parser")

                    # -------- EXTRAER TEXTO PRINCIPAL --------
                    encabezado = soup2.find("p", class_="t-enc-1")

                    anio_mundial = None
                    nombre_grupo = None

                    if encabezado:
                        texto = encabezado.text.strip()

                        # Año
                        match_anio = re.search(r"\d{4}", texto)
                        if match_anio:
                            anio_mundial = int(match_anio.group())

                        # Grupo
                        match_grupo = re.search(r"(Grupo\s+\w+)", texto)
                        if match_grupo:
                            nombre_grupo = match_grupo.group().strip()

                    # -------- TABLA --------
                    tabla = soup2.find("table")

                    if not tabla:
                        continue

                    filas = tabla.find_all("tr")

                    for fila in filas[1:]:

                        celdas = fila.find_all("td")

                        if len(celdas) < 11:
                            continue

                        # -------- NOMBRE PAIS --------
                        nombre_pais = celdas[1].text.strip()
                        nombre_pais = nombre_pais.replace("\n", "").strip()

                        # -------- POSICION --------
                        posicion_txt = celdas[0].text.strip()
                        posicion_grupo = re.sub(r"\D", "", posicion_txt)
                        posicion_grupo = int(posicion_grupo) if posicion_grupo else None

                        # -------- ESTADISTICAS --------
                        pts = parse_int(celdas[2].text)
                        pj = parse_int(celdas[3].text)
                        pg = parse_int(celdas[4].text)
                        pe = parse_int(celdas[5].text)
                        pp = parse_int(celdas[6].text)
                        gf = parse_int(celdas[7].text)
                        gc = parse_int(celdas[8].text)
                        dif = parse_int(celdas[9].text)

                        # -------- CLASIFICO --------
                        clas_txt = celdas[10].text.strip().lower()

                        if clas_txt == "si":
                            clasifico = 1
                        elif clas_txt == "no":
                            clasifico = 0
                        else:
                            clasifico = None

                        # -------- LIMPIEZA CSV --------
                        if nombre_pais:
                            nombre_pais = nombre_pais.replace(",", "")

                        if nombre_grupo:
                            nombre_grupo = nombre_grupo.replace(",", "")

                        # -------- GUARDAR --------
                        writer.writerow([
                            anio_mundial,
                            nombre_grupo,
                            nombre_pais,
                            posicion_grupo,
                            pts,
                            pj,
                            pg,
                            pe,
                            pp,
                            gf,
                            gc,
                            dif,
                            clasifico
                        ])

            except Exception as e:
                print("Error:", e)

            esperar()

    driver.quit()

    print("\nCSV generado: participacion_grupo.csv")



lista_urlsParticipacionGr = [
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

escanear_info_participacion_grupo(lista_urlsParticipacionGr)

