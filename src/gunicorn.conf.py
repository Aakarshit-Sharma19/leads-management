from pathlib import Path
import os

bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"

workers = int(os.getenv("GUNICORN_WORKERS", 3))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 300))
if os.getenv('ENABLE_HTTPS'):
    keyfile = str(Path(__file__).parent / "certificates" / "key.pem")
    certfile = str(Path(__file__).parent / "certificates" / "certificate.pem")
accesslog = '-'