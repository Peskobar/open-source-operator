import csv
import time
import psutil
import torch


def monitor(output="resources.csv"):
    with open(output, "a", newline="") as f:
        writer = csv.writer(f)
        while True:
            gpu_mem = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
            ram = psutil.virtual_memory().used
            writer.writerow([time.time(), gpu_mem, ram])
            f.flush()
            time.sleep(60)


if __name__ == "__main__":
    monitor()
