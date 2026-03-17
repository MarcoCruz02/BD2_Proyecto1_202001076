from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import re
import time
import csv
import os


def escanear_info_grupos(lista_urlsGrupos):

    urls_unicas = list(dict.fromkeys(lista_urlsGrupos))

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

    archivo_csv = "grupo.csv"
    archivo_existe = os.path.isfile(archivo_csv)

    with open(archivo_csv, "a", newline="", encoding="utf-8") as archivo:

        writer = csv.writer(archivo)

        if not archivo_existe:
            writer.writerow([
                "anio_mundial",
                "nombre_grupo",
                "fase"
            ])

        # -------------------------------------
        # SCRAPING
        # -------------------------------------

        for url in urls_unicas:

            print("\nProcesando:", url)

            try:

                # -------- PAGINA PRINCIPAL --------
                driver.get(url)
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # -------- AÑO MUNDIAL --------
                anio_mundial = None
                h1 = soup.find("h1")

                if h1:
                    match = re.search(r"\d{4}", h1.text)
                    if match:
                        anio_mundial = int(match.group())

                # -------- ENCONTRAR LINKS DE GRUPOS --------
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

                # -------- ORDENAR GRUPOS --------
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

                # -------- ANALIZAR CADA GRUPO --------
                for url_grupo in urls_grupos:

                    driver.get(url_grupo)
                    time.sleep(2)

                    soup2 = BeautifulSoup(driver.page_source, "html.parser")

                    titulo = soup2.title.text.strip()

                    nombre_grupo = None
                    fase = None

                    # Ejemplo:
                    # Mundial 1930 de Fútbol - Grupo 1, Primera Ronda

                    if "-" in titulo:

                        parte = titulo.split("-")[1].strip()

                        if "," in parte:

                            nombre_grupo, fase = parte.split(",")

                            nombre_grupo = nombre_grupo.strip()
                            fase = fase.strip().lower()

                        else:

                            nombre_grupo = parte.strip()

                    # -------- LIMPIAR COMAS --------
                    if nombre_grupo:
                        nombre_grupo = nombre_grupo.replace(",", "")

                    if fase:
                        fase = fase.replace(",", "")

                    # -------- GUARDAR CSV --------
                    writer.writerow([
                        anio_mundial,
                        nombre_grupo,
                        fase
                    ])

            except Exception as e:
                print("Error:", e)

            time.sleep(3)

    driver.quit()

    print("\nCSV actualizado: grupo.csv")

lista_urlsGrupos = [
    "https://www.losmundialesdefutbol.com/mundiales/2014_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/2018_mundial.php",
    "https://www.losmundialesdefutbol.com/mundiales/2022_mundial.php"
]

escanear_info_grupos(lista_urlsGrupos)