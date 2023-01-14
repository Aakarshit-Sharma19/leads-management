import multiprocessing
from pathlib import Path

bind = "0.0.0.0:8000"

workers = multiprocessing.cpu_count() * 2 + 1
keyfile = str(Path(__file__).parent / "certificates" / "key.pem")
certfile = str(Path(__file__).parent / "certificates" / "certificate.pem")
accesslog = '-'
