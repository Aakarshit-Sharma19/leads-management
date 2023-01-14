from pathlib import Path
import os

bind = f"0.0.0.0:{os.getenv('PORT', 8000)}"

workers = 4
# keyfile = str(Path(__file__).parent / "certificates" / "key.pem")
# certfile = str(Path(__file__).parent / "certificates" / "certificate.pem")
accesslog = '-'
loglevel = 'debug'