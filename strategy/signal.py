from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .baseline import FixedEffects
from .panel import EASYJET, RYANAIR, Airline, load_panel

BASE = [["airline", "route"], ["airline", "lead_days"], ["airline", "dow"]]
WITH_DATE = BASE + [["depart_date"]]


@dataclass
class PairSignal:
    long: Airline
    short: Airline
    baseline: FixedEffects
    clip: float = 1.0

    def score(self, history, new):
        pred = self.baseline.fit(history).predict(new)
        out = new.assign(pred=pred).dropna(subset=["pred"]).copy()
        out["s"] = (out["ln_p"] - out["pred"]).clip(-self.clip, self.clip)
        out["w"] = out["seats"] * np.exp(out["pred"])
        out["ws"] = out["w"] * out["s"]
        return out

    def spread(self, scored):
        g = scored.groupby(["snapshot_date", "city_pair", "airline"])
        s = (g["ws"].sum() / g["w"].sum()).unstack("airline").dropna()
        diff = (s[self.long.name] - s[self.short.name]).groupby("snapshot_date")
        return pd.DataFrame({"z": diff.mean(), "pairs": diff.size()})

    def series(self, df, expanding=False):
        if not expanding:
            return self.spread(self.score(df, df))
        days = sorted(df["snapshot_date"].unique())
        scored = [self.score(df[df["snapshot_date"] < day], df[df["snapshot_date"] == day]) for day in days[1:]]
        return self.spread(pd.concat(scored))

    def plot(self, df, title=""):
        in_sample = self.series(df)
        expanding = self.series(df, expanding=True)
        fig, (top, bottom) = plt.subplots(2, 1, sharex=True, height_ratios=[3, 1])
        top.axhline(0, color="gray", linewidth=1)
        top.plot(in_sample.index, in_sample["z"], color="gray", linestyle="--", label="in sample")
        top.plot(expanding.index, expanding["z"], color="tab:blue", marker="o", label="expanding")
        top.set_ylabel(f"{self.long.name} - {self.short.name}")
        top.set_title(title)
        top.legend()
        bottom.bar(expanding.index, expanding["pairs"], color="tab:blue")
        bottom.set_ylabel("city pairs")
        fig.autofmt_xdate()
        return fig


if __name__ == "__main__":
    panel = load_panel()
    for name, groups in [("base", BASE), ("base + departure date", WITH_DATE)]:
        PairSignal(RYANAIR, EASYJET, FixedEffects(groups)).plot(panel, name)
    plt.show()
