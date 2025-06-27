import csv
import time
from datetime import datetime

import psutil

try:
    import torch
except Exception:  # pragma: no cover - torch optional
    torch = None


def monitor(output="resources.csv"):
    with open(output, "a", newline="") as f:
        writer = csv.writer(f)
        while True:
            gpu_mem = 0
            if torch and torch.cuda.is_available():
                gpu_mem = torch.cuda.memory_allocated() / (1024 ** 2)
            ram = psutil.virtual_memory().used / (1024 ** 2)
            writer.writerow([datetime.utcnow().isoformat(), gpu_mem, ram])
            f.flush()
            time.sleep(60)


if __name__ == "__main__":
    monitor()
