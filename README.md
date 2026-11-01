# Hackeo TV

Pantalla de inicio moderna para una Panasonic TX-55FX600E (My Home Screen 3, navegador Firefox 34), sin ningún aparato externo: la página vive en el navegador de la tele como página de inicio, va a pantalla completa con OK y lanza YouTube y Netflix por DIAL contra la propia tele. Si el PC de casa está encendido (`auto.py`), además abre Prime Video, Disney+ y el resto de apps.

- `docs/` — la página (publicada con GitHub Pages).
- `tv.py`, `servir.py`, `vigilante.py`, `auto.py` — parte opcional que corre en el PC.
- `emparejar.py` — emparejamiento con PIN (una sola vez); guarda `tv.json`, que no se sube.
