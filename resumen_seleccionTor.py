import csv
import time
import random
import requests
from bs4 import BeautifulSoup

# Funciona con navegador Tor abierto y conectado a la red Tor

URL         = "https://www.losmundialesdefutbol.com/estadisticas/tabla_de_posiciones.php"
OUTPUT_FILE = "tabla_posiciones_mundiales.csv"

# Tor Browser expone un proxy SOCKS5 en este puerto por defecto
TOR_PROXY = {
    "http":  "socks5h://127.0.0.1:9150",
    "https": "socks5h://127.0.0.1:9150",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Referer": "https://www.losmundialesdefutbol.com/estadisticas.php",
}

CSV_COLUMNS = [
    "nom_pais", "mundiales", "titulos", "subcampeonatos",
    "pos_historica", "pts_historico", "pj_historico", "pg_historico",
    "pe_historico", "pp_historico", "gf_historico", "gc_historico", "dif_historica",
]

# ─── Verificar que Tor está activo ────────────────────────────────────────────

def verificar_tor() -> bool:
    try:
        r = requests.get(
            "https://check.torproject.org/api/ip",
            proxies=TOR_PROXY,
            timeout=15
        )
        data = r.json()
        if data.get("IsTor"):
            print(f"Tor activo — IP: {data.get('IP')}")
            return True
        else:
            print(f"Conectado pero NO es Tor — IP: {data.get('IP')}")
            return False
    except Exception as e:
        print(f"No se pudo conectar a Tor: {e}")
        print("Asegúrate de que Tor Browser esté abierto y conectado.")
        return False

# ─── Fetch ────────────────────────────────────────────────────────────────────

def fetch_html(url: str) -> str | None:
    try:
        time.sleep(random.uniform(2, 4))
        r = requests.get(url, headers=HEADERS, proxies=TOR_PROXY, timeout=30)
        print(f"   HTTP {r.status_code}")
        if r.status_code == 200:
            return r.text
        else:
            print(f"Bloqueado con código {r.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# ─── Parseo ───────────────────────────────────────────────────────────────────

def parsear_tabla(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    filas_datos = []

    total_tr = len(soup.find_all("tr"))
    total_td = len(soup.find_all("td"))
    print(f"🔍 <tr>: {total_tr} | <td>: {total_td}")

    for fila in soup.find_all("tr"):
        celdas = fila.find_all("td")
        if len(celdas) < 13:
            continue

        # Posición
        celda_pos = celdas[0]
        span_pos  = celda_pos.find("span")
        pos_texto = span_pos.get_text(strip=True) if span_pos else celda_pos.get_text(strip=True)
        pos_texto = pos_texto.replace(".", "").strip()
        if not pos_texto.isdigit():
            continue
        pos_historica = int(pos_texto)

        # País (el sitio duplica el nombre: "Brasil Brasil" → "Brasil")
        texto_pais = celdas[1].get_text(strip=True)
        palabras   = texto_pais.split()
        mitad      = len(palabras) // 2
        nom_pais   = " ".join(palabras[:mitad]) if mitad > 0 else texto_pais

        mundiales      = _int(celdas[2].get_text(strip=True))
        titulos        = len(celdas[3].find_all("img", alt="Copa Del Mundo"))
        sub_texto      = celdas[4].get_text(strip=True)
        subcampeonatos = 0 if sub_texto in ("-", "") else (int(sub_texto) if sub_texto.isdigit() else sub_texto.lower().count("subcampeón"))

        filas_datos.append({
            "nom_pais":       nom_pais,
            "mundiales":      mundiales,
            "titulos":        titulos,
            "subcampeonatos": subcampeonatos,
            "pos_historica":  pos_historica,
            "pts_historico":  _int(celdas[5].get_text(strip=True)),
            "pj_historico":   _int(celdas[6].get_text(strip=True)),
            "pg_historico":   _int(celdas[7].get_text(strip=True)),
            "pe_historico":   _int(celdas[8].get_text(strip=True)),
            "pp_historico":   _int(celdas[9].get_text(strip=True)),
            "gf_historico":   _int(celdas[10].get_text(strip=True)),
            "gc_historico":   _int(celdas[11].get_text(strip=True)),
            "dif_historica":  _int(celdas[12].get_text(strip=True)),
        })

    return filas_datos


def _int(v: str) -> int:
    v = v.strip()
    if v in ("-", "", "N/A"):
        return 0
    try:
        return int(v)
    except ValueError:
        return 0

# ─── Guardar CSV ──────────────────────────────────────────────────────────────

def guardar_csv(datos: list[dict], archivo: str):
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(datos)
    print(f"CSV guardado: {archivo}  ({len(datos)} filas)")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Scraper via Tor — Tabla de Posiciones Histórica\n")

    print("Verificando conexión Tor...")
    if not verificar_tor():
        return

    print(f"\n Descargando: {URL}")
    html = fetch_html(URL)

    if not html:
        return

    datos = parsear_tabla(html)

    if not datos:
        print(" No se encontraron datos en la tabla.")
        return

    print(f"\n{len(datos)} selecciones encontradas.\n")
    print("── Vista previa (primeras 5) ────────────────────────")
    print(",".join(CSV_COLUMNS))
    for fila in datos[:5]:
        print(",".join(str(fila[col]) for col in CSV_COLUMNS))
    print("...\n")

    guardar_csv(datos, OUTPUT_FILE)
    print("¡Listo!")


if __name__ == "__main__":
    main()