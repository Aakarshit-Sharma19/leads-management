from pathlib import Path
import os

workers = int(os.getenv("GUNICORN_WORKERS", 3))
timeout = int(os.getenv("GUNICORN_TIMEOUT", 300))
if os.getenv('ENABLE_HTTPS'):
    keyfile = str(Path(__file__).parent / "certificates" / "key.pem")
    certfile = str(Path(__file__).parent / "certificates" / "certificate.pem")
    os.environ['POST'] = '443'

bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"

accesslog = '-'