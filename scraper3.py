from curl_cffi import requests
from bs4 import BeautifulSoup
import csv
import os
import concurrent.futures
import time
import re


# ----------------------------
# convertir fecha a YYYY-MM-DD
# ----------------------------

def convertir_fecha(fecha):

    meses = {
        "enero":"01","febrero":"02","marzo":"03","abril":"04",
        "mayo":"05","junio":"06","julio":"07","agosto":"08",
        "septiembre":"09","octubre":"10","noviembre":"11","diciembre":"12"
    }

    try:
        partes = fecha.lower().split()

        dia = partes[0]
        mes = meses[partes[2]]
        anio = partes[4]

        return f"{anio}-{mes}-{dia.zfill(2)}"

    except:
        return ""


def scrapear_jugador(url):

    for intento in range(3):

        try:

            r = requests.get(
                url,
                impersonate="chrome110",
                timeout=20
            )

            if r.status_code != 200:
                time.sleep(3)
                continue

            print("Status:", r.status_code, url)

            soup = BeautifulSoup(r.text,"html.parser")

            nombre = ""
            fecha = ""
            lugar = ""
            posicion = ""
            altura = ""
            apodo = ""
            pais = ""
            camisetas = ""
            url_social = ""

            tabla = soup.find("table")

            if tabla:

                filas = tabla.find_all("tr")

                for fila in filas:

                    tds = fila.find_all("td")

                    if len(tds) < 2:
                        continue

                    campo = tds[0].get_text(strip=True)
                    valor = tds[1].get_text(strip=True)

                    if "Nombre completo" in campo:
                        nombre = valor

                    elif "Fecha de Nacimiento" in campo:
                        fecha = convertir_fecha(valor)

                    elif "Lugar de nacimiento" in campo:
                        lugar = valor.replace(",","")

                    elif "Posición" in campo:
                        posicion = valor

                    elif "Números de camiseta" in campo:
                        camisetas = valor

                    elif "Altura" in campo:
                        match = re.search(r"\d\.\d+", valor)
                        if match:
                            altura = match.group()

                    elif "Apodo" in campo:
                        apodo = valor.replace(","," ")

                    elif "Redes Sociales" in campo:
                        link = tds[1].find("a")
                        if link:
                            url_social = link["href"]

            # nombre alternativo
            if not nombre:
                h2 = soup.find("h2",class_="t-enc-1")
                if h2:
                    nombre = h2.get_text(strip=True)

            # país
            h3 = soup.find("h3",string=re.compile("Selección"))

            if h3:
                cont = h3.find_next("p")
                if cont:
                    pais = cont.get_text(strip=True)

            return [
                nombre,
                fecha,
                lugar,
                posicion,
                altura,
                apodo,
                pais,
                camisetas,
                url_social
            ]

        except Exception as e:

            print("Reintento", intento+1, e)
            time.sleep(3)

    return None


def escanear_info_jugador(urls):

    resultados = []

    print("\n--- SCRAPING JUGADORES ---\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:

        futures = [executor.submit(scrapear_jugador, url) for url in urls]

        for future in concurrent.futures.as_completed(futures):

            data = future.result()

            if data:
                resultados.append(data)

    carpeta = "archivos_carga"
    os.makedirs(carpeta,exist_ok=True)

    ruta = os.path.join(carpeta,"jugador.csv")

    with open(ruta,"w",newline="",encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "nombre_completo",
            "fecha_nacimiento",
            "lugar_nacimiento",
            "posicion",
            "altura",
            "apodo",
            "nombre_pais",
            "numeros_camiseta",
            "url_perfil"
        ])

        writer.writerows(resultados)

    print("\nCSV generado:",ruta)

lista_urlsMund = [
    "https://www.losmundialesdefutbol.com/jugadores/angel_bossio.php",
    "https://www.losmundialesdefutbol.com/jugadores/juan_botasso.php",
    "https://www.losmundialesdefutbol.com/jugadores/fernando_paternoster.php",
    "https://www.losmundialesdefutbol.com/jugadores/rodolfo_orlandini.php",
    "https://www.losmundialesdefutbol.com/jugadores/ramon_muttis.php",
    "https://www.losmundialesdefutbol.com/jugadores/jose_della_torre.php",
    "https://www.losmundialesdefutbol.com/jugadores/adolfo_zumelzu.php",
    "https://www.losmundialesdefutbol.com/jugadores/alberto_chividini.php",
    "https://www.losmundialesdefutbol.com/jugadores/edmundo_piaggio.php",
    "https://www.losmundialesdefutbol.com/jugadores/luis_monti.php",
    "https://www.losmundialesdefutbol.com/jugadores/pedro_suarez.php",
    "https://www.losmundialesdefutbol.com/jugadores/juan_evaristo.php",
    "https://www.losmundialesdefutbol.com/jugadores/francisco_varallo.php",
    "https://www.losmundialesdefutbol.com/jugadores/carlos_spadaro.php",
    "https://www.losmundialesdefutbol.com/jugadores/alejandro_scopelli.php",
    "https://www.losmundialesdefutbol.com/jugadores/guillermo_stabile.php",
    "https://www.losmundialesdefutbol.com/jugadores/carlos_peucelle.php",
    "https://www.losmundialesdefutbol.com/jugadores/natalio_perinetti.php",
    "https://www.losmundialesdefutbol.com/jugadores/roberto_cerro.php",
    "https://www.losmundialesdefutbol.com/jugadores/manuel_ferreira.php",
    "https://www.losmundialesdefutbol.com/jugadores/mario_evaristo.php",
    "https://www.losmundialesdefutbol.com/jugadores/atilio_demaria.php",
    "https://www.losmundialesdefutbol.com/jugadores/cesar_espinoza.php"
]

link_messi = [
    "https://www.losmundialesdefutbol.com/jugadores/lionel_messi.php"
]

print("\n--- INICIANDO MAPEO DE ESTRUCTURA ---")


escanear_info_jugador(lista_urlsMund)

print("\n--- ESCANEO FINALIZADO ---")