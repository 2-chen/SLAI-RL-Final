import json
import os
from collections import defaultdict


class Logger:
    def __init__(self, log_dir: str, run_name: str):
        self.log_dir = log_dir
        self.run_name = run_name
        self.metrics: dict[str, list] = defaultdict(list)
        self._step = 0
        os.makedirs(log_dir, exist_ok=True)

    def log(self, metrics: dict, step: int | None = None):
        if step is not None:
            self._step = step
        for k, v in metrics.items():
            self.metrics[k].append({"step": self._step, "value": v})
        if step is None:
            self._step += 1

    def save(self):
        path = os.path.join(self.log_dir, f"{self.run_name}.json")
        with open(path, "w") as f:
            json.dump(dict(self.metrics), f, indent=2)

    def load(self):
        path = os.path.join(self.log_dir, f"{self.run_name}.json")
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        return None
