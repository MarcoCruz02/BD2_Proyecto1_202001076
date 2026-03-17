from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import re
import time
import csv
import os


def escanear_info_pos_final(lista_urlsPosFinal):

    urls_unicas = list(dict.fromkeys(lista_urlsPosFinal))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    # -------------------------------------
    # CONFIGURAR EDGE
    # -------------------------------------

    options = Options()
    options.add_argument("--log-level=3")

    driver = webdriver.Edge(
        service=Service("msedgedriver.exe"),
        options=options
    )

    # -------------------------------------
    # CSV
    # -------------------------------------

    archivo_csv = "posicion_final.csv"
    archivo_existe = os.path.isfile(archivo_csv)

    with open(archivo_csv, "a", newline="", encoding="utf-8") as archivo:

        writer = csv.writer(archivo)

        if not archivo_existe:
            writer.writerow([
                "anio_mundial",
                "nombre_pais",
                "posicion",
                "etapa",
                "pts",
                "pj",
                "pg",
                "pe",
                "pp",
                "gf",
                "gc",
                "dif",
                "es_campeon",
                "es_subcampeon"
            ])

        # -------------------------------------
        # SCRAPING
        # -------------------------------------

        for url in urls_unicas:

            print("\nProcesando:", url)

            try:

                driver.get(url)
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # ---------------- AÑO MUNDIAL ----------------
                anio_mundial = None
                h1 = soup.find("h1")

                if h1:
                    match = re.search(r"\d{4}", h1.text)
                    if match:
                        anio_mundial = int(match.group())

                tablas = soup.find_all("table")

                for tabla in tablas:

                    filas = tabla.find_all("tr")

                    for fila in filas[1:]:

                        celdas = fila.find_all("td")

                        if len(celdas) < 11:
                            continue

                        # ---------------- POSICION ----------------
                        posicion_txt = celdas[0].text.strip()
                        posicion = re.sub(r"\D", "", posicion_txt)
                        posicion = int(posicion) if posicion else None

                        # ---------------- NOMBRE PAIS ----------------
                        nombre_pais = None
                        link_pais = celdas[1].find("a")

                        if link_pais:
                            nombre_pais = link_pais.text.strip()
                            nombre_pais = nombre_pais.replace(",", "")

                        # ---------------- ETAPA ----------------
                        etapa = celdas[2].text.strip() or None

                        if etapa:
                            etapa = etapa.replace(",", "").lower()

                        # ---------------- NUMEROS ----------------
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

                        # ---------------- CAMPEON / SUBCAMPEON ----------------
                        if posicion == 1:
                            es_campeon = 1
                            es_subcampeon = 0
                        elif posicion == 2:
                            es_campeon = 0
                            es_subcampeon = 1
                        else:
                            es_campeon = 0
                            es_subcampeon = 0

                        # ---------------- GUARDAR CSV ----------------
                        writer.writerow([
                            anio_mundial,
                            nombre_pais,
                            posicion,
                            etapa,
                            pts,
                            pj,
                            pg,
                            pe,
                            pp,
                            gf,
                            gc,
                            dif,
                            es_campeon,
                            es_subcampeon
                        ])

            except Exception as e:
                print("Error:", e)

            time.sleep(1)

    driver.quit()

    print("\nCSV actualizado:", archivo_csv)

lista_urlsPosFinal = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1934_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1938_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1950_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1954_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1958_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1962_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1966_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1970_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1974_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1978_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1982_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1986_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1990_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1994_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/1998_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/2002_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/2006_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/2010_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/2014_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/2018_posiciones_finales.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_posiciones_finales.php"
]

escanear_info_pos_final(lista_urlsPosFinal)