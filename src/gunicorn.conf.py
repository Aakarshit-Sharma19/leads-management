from pathlib import Path
import os

bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"

workers = 4
if not os.getenv('DISABLE_HTTPS'):
    keyfile = str(Path(__file__).parent / "certificates" / "key.pem")
    certfile = str(Path(__file__).parent / "certificates" / "certificate.pem")
accesslog = '-'