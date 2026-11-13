from dataclasses import dataclass, field, replace

import pandas as pd

TOLERANCE = 1e-9
MAX_ITERATIONS = 500


@dataclass
class FixedEffects:
    groups: list
    intercept: float = 0.0
    effects: list = field(default_factory=list)

    def fit(self, df):
        intercept = df["ln_p"].mean()
        resid = df["ln_p"] - intercept
        effects = [0 * resid.groupby([df[c] for c in cols]).mean() for cols in self.groups]
        for _ in range(MAX_ITERATIONS):
            biggest = 0.0
            for i, cols in enumerate(self.groups):
                grouped = resid.groupby([df[c] for c in cols])
                resid = resid - grouped.transform("mean")
                step = grouped.mean()
                effects[i] = effects[i] + step
                biggest = max(biggest, step.abs().max())
            if biggest < TOLERANCE:
                break
        return replace(self, intercept=intercept, effects=effects)

    def predict(self, df):
        total = pd.Series(self.intercept, index=df.index)
        for cols, effect in zip(self.groups, self.effects):
            total = total + effect.reindex(df.set_index(cols).index).to_numpy()
        return total
