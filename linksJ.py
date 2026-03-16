import asyncio
import os
from playwright.async_api import async_playwright
from playwright_stealth import stealth # Importación estándar

async def extraer_jugadores_con_sigilo():
    url_mundial = "https://www.losmundialesdefutbol.com/mundiales/1930_mundial.php"
    lista_jugadores = set()
    
    # Carpeta para guardar la sesión
    user_data_dir = os.path.join(os.getcwd(), "perfil_bot")

    async with async_playwright() as p:
        # Abrimos visible para que el servidor "confíe" más en la conexión inicial
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False, 
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = context.pages[0]
        
        # Aplicar sigilo (Llamada corregida y más compatible)
        await stealth(page)

        print(f"🚀 Accediendo a: {url_mundial}")
        
        try:
            # Ir a la página
            await page.goto(url_mundial, wait_until="networkidle", timeout=60000)
            
            # Pausa de seguridad para que la tabla se dibuje
            await asyncio.sleep(5)

            # EXTRAER LINKS DE PLANTELES
            urls_planteles = await page.evaluate('''() => {
                return Array.from(document.links)
                    .map(a => a.href)
                    .filter(href => href.includes('/planteles/'));
            }''')
            
            urls_planteles = list(set(urls_planteles))
            print(f"✅ Equipos detectados: {len(urls_planteles)}")

            for url_equipo in urls_planteles:
                print(f"   📂 Procesando equipo: {url_equipo.split('/')[-1]}")
                await page.goto(url_equipo, wait_until="domcontentloaded")
                
                # Extraer perfiles de jugadores
                links_perfiles = await page.evaluate('''() => {
                    return Array.from(document.links)
                        .map(a => a.href)
                        .filter(href => href.includes('/jugadores/'));
                }''')
                
                for link in links_perfiles:
                    # Guardamos con el formato solicitado
                    lista_jugadores.add(f'"{link}"')
                
                await asyncio.sleep(1)

        except Exception as e:
            print(f"⚠️ Error: {e}")

        await context.close()

    # Guardar resultados
    if lista_jugadores:
        with open("jugadoresPL.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(lista_jugadores)))
        print(f"\n✨ ¡CONSEGUIDO! {len(lista_jugadores)} links guardados en jugadoresPL.txt")
    else:
        print("\n❌ Sigue devolviendo 0. Por favor, mira la ventana del navegador cuando se abra.")

# Invocación directa sin el bloque if __name__
asyncio.run(extraer_jugadores_con_sigilo())