from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE = "https://www.losmundialesdefutbol.com/"

# iniciar edge
driver = webdriver.Edge(service=Service("msedgedriver.exe"))
# abrir página principal
driver.get(BASE + "mundiales.php")

time.sleep(3)

html = driver.page_source
soup = BeautifulSoup(html, "html.parser")

links = []

for a in soup.find_all("a", href=True):
    href = a["href"]
    if "mundiales/" in href and "_mundial.php" in href:
        links.append(BASE + href)

links = list(set(links))

print("Total mundiales encontrados:", len(links))

data = []

for link in links:

    print("Entrando a:", link)

    driver.get(link)

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    titulo = soup.find("h1")

    if titulo:
        titulo = titulo.text.strip()
    else:
        titulo = "N/A"

    texto = soup.get_text()

    data.append({
        "pagina": link,
        "titulo": titulo,
        "contenido": texto
    })

df = pd.DataFrame(data)

df.to_csv("mundiales.csv", index=False, encoding="utf-8")

driver.quit()

print("Scraping terminado")