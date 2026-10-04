"""Labor: einziger Zugang zur Ground Truth. Jeder Aufruf wird geloggt (Tabelle `experiments`)."""
import time


class Lab:
    def __init__(self, y, run_id="", seed=-1, policy="", dataset="", sink=None):
        self._y = y; self.log = []
        self.ctx = dict(run_id=run_id, seed=seed, policy=policy, dataset=dataset)
        self.sink = sink if sink is not None else []

    def run(self, i: int) -> float:
        i = int(i); y = float(self._y[i]); self.log.append(i)
        self.sink.append({**self.ctx, "step": len(self.log), "x_index": i, "y": y, "mlflow_run_id": "",
                          "ts": time.strftime("%Y-%m-%dT%H:%M:%S")})
        return y
