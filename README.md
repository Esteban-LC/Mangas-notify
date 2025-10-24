# Mangas-noty

Bot que verifica capítulos y notifica en Discord (siempre manda resumen).

## Variables
- `DISCORD_WEBHOOK`: webhook de tu canal.

## Ejecutar local
```bash
pip install -r requirements.txt
python -m playwright install --with-deps chromium
python main.py
```

## Añadir series
Edita `series.yaml` y agrega tus obras.
