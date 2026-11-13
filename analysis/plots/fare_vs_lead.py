from collections import defaultdict
from statistics import mean

import matplotlib.pyplot as plt

from ..load import load_fares

prices = defaultdict(lambda: defaultdict(list))
for fare in load_fares():
    prices[fare["airline"]][fare["lead_days"]].append(fare["price"])

for airline, lead_prices in sorted(prices.items()):
    leads = sorted(lead_prices)
    plt.plot(leads, [mean(lead_prices[d]) for d in leads], marker="o", label=airline)

plt.xlabel("days before departure")
plt.ylabel("mean price (GBP)")
plt.legend()
plt.show()
