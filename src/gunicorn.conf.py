from pathlib import Path
import os

workers = int(os.getenv("GUNICORN_WORKERS", 3))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 300))
ENABLE_HTTPS = os.getenv('ENABLE_HTTPS')
if ENABLE_HTTPS:
    keyfile = str(Path(__file__).parent / "certificates" / "key.pem")
    certfile = str(Path(__file__).parent / "certificates" / "certificate.pem")

bind = f"0.0.0.0:{os.getenv('PORT', 8000) if not ENABLE_HTTPS else 443}"

accesslog = '-'