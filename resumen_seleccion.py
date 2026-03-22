import csv
import random
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ─── Configuración ────────────────────────────────────────────────────────────

URL         = "https://www.losmundialesdefutbol.com/estadisticas/tabla_de_posiciones.php"
OUTPUT_FILE = "tabla_posiciones_mundiales.csv"

CSV_COLUMNS = [
    "nom_pais", "mundiales", "titulos", "subcampeonatos",
    "pos_historica", "pts_historico", "pj_historico", "pg_historico",
    "pe_historico", "pp_historico", "gf_historico", "gc_historico", "dif_historica",
]

STEALTH_SCRIPTS = [
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
    "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})",
    "Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en']})",
    "window.chrome = { runtime: {} };",
]

# ─── Fetch con Playwright ─────────────────────────────────────────────────────

def fetch_html_stealth(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="es-ES",
            timezone_id="America/Guatemala",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
        )

        for script in STEALTH_SCRIPTS:
            context.add_init_script(script)

        page = context.new_page()

        print(f"Navegando a: {url}")

        # Esperar a networkidle para asegurarse que todo el JS cargó
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Esperar específicamente a que exista una fila de datos en la tabla
        try:
            page.wait_for_selector("table tr td", timeout=15000)
            print("Tabla detectada en la página.")
        except Exception:
            print("No se detectó tabla, intentando igual...")

        time.sleep(random.uniform(2, 3))

        html = page.content()

        # DEBUG: guardar HTML para inspección
        with open("debug_pagina.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(" HTML guardado en debug_pagina.html para inspección.")

        browser.close()
        return html

# ─── Parseo ───────

def parsear_tabla(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    filas_datos = []

    # DEBUG: contar cuántas filas <tr> y <td> hay en total
    total_tr = len(soup.find_all("tr"))
    total_td = len(soup.find_all("td"))
    print(f" DEBUG — Total <tr>: {total_tr} | Total <td>: {total_td}")

    for fila in soup.find_all("tr"):
        celdas = fila.find_all("td")

        if len(celdas) < 13:
            continue

        # ── Posición histórica ───────
        celda_pos = celdas[0]
        span_pos  = celda_pos.find("span")
        pos_texto = span_pos.get_text(strip=True) if span_pos else celda_pos.get_text(strip=True)
        pos_texto = pos_texto.replace(".", "").strip()

        # DEBUG primeras filas con 13+ celdas
        if len(filas_datos) < 3:
            print(f"   Fila candidata → pos_texto='{pos_texto}' | celdas[1]='{celdas[1].get_text(strip=True)[:30]}'")

        if not pos_texto.isdigit():
            continue

        pos_historica = int(pos_texto)

        # ── Nombre del país ───────
        texto_pais = celdas[1].get_text(strip=True)
        palabras   = texto_pais.split()
        mitad      = len(palabras) // 2
        nom_pais   = " ".join(palabras[:mitad]) if mitad > 0 else texto_pais

        # ── Mundiales ───────
        mundiales = _int(celdas[2].get_text(strip=True))

        # ── Títulos ───────
        titulos = len(celdas[3].find_all("img", alt="Copa Del Mundo"))

        # ── Subcampeonatos ───────
        sub_texto = celdas[4].get_text(strip=True)
        if sub_texto in ("-", ""):
            subcampeonatos = 0
        elif sub_texto.isdigit():
            subcampeonatos = int(sub_texto)
        else:
            subcampeonatos = sub_texto.lower().count("subcampeón")

        # ── Estadísticas ───────
        pts = _int(celdas[5].get_text(strip=True))
        pj  = _int(celdas[6].get_text(strip=True))
        pg  = _int(celdas[7].get_text(strip=True))
        pe  = _int(celdas[8].get_text(strip=True))
        pp  = _int(celdas[9].get_text(strip=True))
        gf  = _int(celdas[10].get_text(strip=True))
        gc  = _int(celdas[11].get_text(strip=True))
        dif = _int(celdas[12].get_text(strip=True))

        filas_datos.append({
            "nom_pais":       nom_pais,
            "mundiales":      mundiales,
            "titulos":        titulos,
            "subcampeonatos": subcampeonatos,
            "pos_historica":  pos_historica,
            "pts_historico":  pts,
            "pj_historico":   pj,
            "pg_historico":   pg,
            "pe_historico":   pe,
            "pp_historico":   pp,
            "gf_historico":   gf,
            "gc_historico":   gc,
            "dif_historica":  dif,
        })

    return filas_datos


def _int(valor: str) -> int:
    valor = valor.strip()
    if valor in ("-", "", "N/A"):
        return 0
    try:
        return int(valor)
    except ValueError:
        return 0

# ─── Guardar CSV ──────

def guardar_csv(datos: list[dict], archivo: str):
    with open(archivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(datos)
    print(f"CSV guardado: {archivo}  ({len(datos)} filas)")

# ─── Main ────

def main():
    print("Scraper Stealth — Tabla de Posiciones Histórica\n")

    html  = fetch_html_stealth(URL)
    datos = parsear_tabla(html)

    if not datos:
        print("\nNo se encontraron datos.")
        print("   Revisa debug_pagina.html para ver qué devolvió el sitio.")
        print("   Busca en ese archivo si hay texto como '403', 'blocked', 'captcha', o si la tabla existe.")
        return

    print(f"\n{len(datos)} selecciones encontradas.\n")

    print("── Vista previa (primeras 5 filas) ──────────────────")
    print(",".join(CSV_COLUMNS))
    for fila in datos[:5]:
        print(",".join(str(fila[col]) for col in CSV_COLUMNS))
    print("...\n")

    guardar_csv(datos, OUTPUT_FILE)
    print("¡Listo!")


if __name__ == "__main__":
    main()
