from selenium import webdriver
from selenium.webdriver.edge.service import Service
from bs4 import BeautifulSoup
import re
import time
import csv
from datetime import datetime


def escanear_info_partido(lista_urlsPartidos):

    urls_unicas = list(dict.fromkeys(lista_urlsPartidos))
    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    # iniciar edge
    driver = webdriver.Edge(service=Service("msedgedriver.exe"))

    # crear csv
    with open("partidos_mundiales.csv", "w", newline="", encoding="utf-8") as archivo:

        writer = csv.writer(archivo)

        # encabezado
        writer.writerow([
            "anio_mundial",
            "grupo",
            "nom_pais_local",
            "nom_pais_visita",
            "fecha",
            "fase",
            "goles_local",
            "goles_visita",
            "tiempo_extra",
            "penales",
            "num_partido"
        ])

        for url in urls_unicas:

            print("\nProcesando:", url)

            try:

                driver.get(url)
                time.sleep(3)

                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # ---------------- AÑO MUNDIAL ----------------
                anio_mundial = None
                h2 = soup.find("h2", class_=re.compile("t-enc-1"))

                if h2:
                    anio = re.search(r"\d{4}", h2.text)
                    if anio:
                        anio_mundial = int(anio.group())

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

                    # ---------------- FASE Y GRUPO ----------------
                    fase = None
                    grupo = None

                    fase_tag = bloque.find("a", href=re.compile("grupo|final|fase"))

                    if fase_tag:

                        texto = fase_tag.text.strip()

                        # separar fase
                        f = re.search(r'^[^,]+', texto)
                        if f:
                            fase = f.group().strip().lower()

                        # separar grupo (soporta Grupo A o Grupo 1)
                        g = re.search(r'Grupo\s+[A-Z0-9]+', texto)
                        if g:
                            grupo = g.group().strip()

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

                    # ---------------- PAISES ----------------
                    paises = bloque.find_all("div", style=re.compile("width:\s*129px"))

                    if len(paises) >= 2:
                        nom_pais_local = paises[0].text.strip()
                        nom_pais_visita = paises[1].text.strip()
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

                    # ---------------- GUARDAR CSV ----------------
                    writer.writerow([
                        anio_mundial,
                        grupo,
                        nom_pais_local,
                        nom_pais_visita,
                        fecha_actual,
                        fase,
                        goles_local,
                        goles_visitante,
                        tiempo_extra,
                        penales,
                        num_partido
                    ])

            except Exception as e:
                print("Error:", e)

            time.sleep(1)

    driver.quit()

    print("\nCSV generado: partidos_mundiales.csv")

lista_urlsPartidos = [
    "https://www.losmundialesdefutbol.com/mundiales/1930_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1934_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1938_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1950_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1954_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1958_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1962_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1966_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1970_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1974_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1978_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1982_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1986_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1990_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1994_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/1998_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2002_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2006_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2010_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2014_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2018_resultados.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_resultados.php"
]  

escanear_info_partido(lista_urlsPartidos)