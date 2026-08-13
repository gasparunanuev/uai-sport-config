"""Genera los iconos de la PWA renderizando con Playwright.

Se corre a mano cuando cambia la identidad visual, no en cada deploy:
    python tools/generar-iconos.py
Requiere el venv de uai-sport-bot (playwright).
"""
import pathlib
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# safe: proporcion del lado que ocupa el contenido. Android recorta los iconos
# maskable a un circulo, asi que ahi el contenido va mas chico.
PLANTILLA = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
<style>
  html,body{{margin:0;padding:0}}
  .icono{{
    width:{lado}px;height:{lado}px;position:relative;overflow:hidden;
    background:radial-gradient(120% 120% at 30% 10%, #141b2b 0%, #070a11 70%);
    display:flex;flex-direction:column;align-items:center;justify-content:center;
    {radio}
  }}
  .marca{{
    font-family:'Bebas Neue',sans-serif;color:#fff;line-height:.82;
    font-size:{fuente}px;letter-spacing:{track}px;text-indent:{track}px;
  }}
  .barra{{
    width:{barra}px;height:{alto}px;background:#00e676;border-radius:{alto}px;
    margin-top:{gap}px;box-shadow:0 0 {glow}px rgba(0,230,118,.55);
  }}
</style></head>
<body><div class="icono"><div class="marca">UAI</div><div class="barra"></div></div></body></html>
"""


def render(pagina, lado, salida, safe=0.62, redondeado=False):
    contenido = lado * safe
    html = PLANTILLA.format(
        lado=lado,
        radio=f"border-radius:{lado * 0.22:.0f}px;" if redondeado else "",
        fuente=contenido * 0.62,
        track=contenido * 0.045,
        barra=contenido * 0.72,
        alto=max(2, contenido * 0.075),
        gap=contenido * 0.10,
        glow=contenido * 0.12,
    )
    pagina.set_viewport_size({"width": lado, "height": lado})
    pagina.set_content(html)
    pagina.wait_for_timeout(700)          # que termine de cargar la tipografia
    pagina.screenshot(path=str(RAIZ / salida), omit_background=False)
    print(f"  {salida}  {lado}x{lado}")


def main():
    with sync_playwright() as p:
        navegador = p.chromium.launch()
        pagina = navegador.new_page(device_scale_factor=1)
        print("Generando iconos:")
        # iOS ya aplica su propia mascara redondeada; el PNG va cuadrado.
        render(pagina, 180, "icon-180.png")
        render(pagina, 192, "icon-192.png")
        render(pagina, 512, "icon-512.png")
        # Android recorta a circulo: contenido dentro del 60% central.
        render(pagina, 512, "icon-maskable-512.png", safe=0.46)
        render(pagina, 32, "favicon-32.png")
        navegador.close()


if __name__ == "__main__":
    main()
