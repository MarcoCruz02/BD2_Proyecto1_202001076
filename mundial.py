from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from bs4 import BeautifulSoup
import re
import time
import csv
import os
from datetime import datetime


def escanear_info_mundial(lista_urlsMund):

    urls_unicas = list(dict.fromkeys(lista_urlsMund))

    print(f"\nSe analizarán {len(urls_unicas)} páginas\n")

    # -------------------------------------
    # CONFIGURAR EDGE
    # -------------------------------------

    options = Options()
    options.add_argument("--log-level=3")  # oculta logs molestos

    driver = webdriver.Edge(
        service=Service("msedgedriver.exe"),
        options=options
    )

    # -------------------------------------
    # CREAR RUTA DEL CSV
    # -------------------------------------

    carpeta = "archivos_carga"
    os.makedirs(carpeta, exist_ok=True)

    ruta_csv = os.path.join(carpeta, "mundial.csv")

    # -------------------------------------
    # CREAR CSV
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

                # -------- PAGINA PRINCIPAL --------
                driver.get(url)
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, "html.parser")

                # -------- AÑO --------
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

                # -------- PAGINA RESULTADOS --------
                url_resultados = f"https://www.losmundialesdefutbol.com/mundiales/{anio}_resultados.php"

                driver.get(url_resultados)
                time.sleep(3)

                soup2 = BeautifulSoup(driver.page_source, "html.parser")

                fechas = []

                for h3 in soup2.find_all("h3"):

                    if "Fecha:" in h3.text:

                        fecha_txt = h3.find("strong").text.strip()

                        try:
                            # normalizar y convertir
                            fecha = datetime.strptime(
                                fecha_txt.title(),
                                "%d-%b-%Y"
                            )
                            fechas.append(fecha)
                        except:
                            continue

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

            except Exception as e:
                print("Error al analizar la página:", e)

            time.sleep(1)

    driver.quit()

    print(f"\nCSV generado en: {ruta_csv}")

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

escanear_info_mundial(lista_urlsMund)