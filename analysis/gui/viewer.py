import sys
from collections import defaultdict
from statistics import mean

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QVBoxLayout, QWidget

from ..load import load_fares

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 650


class Window(QWidget):
    def __init__(self, fares):
        super().__init__()
        self.fares = fares
        for fare in self.fares:
            fare["route"] = fare["origin"] + "-" + fare["dest"]

        self.route_box = self.make_box("route")
        self.date_box = self.make_box("depart_date")

        self.figure = Figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot()

        left = QVBoxLayout()
        left.addWidget(self.route_box)
        left.addWidget(self.date_box)
        left.addStretch()

        main = QHBoxLayout(self)
        main.addLayout(left)
        main.addWidget(self.canvas)
        self.plot()

    def make_box(self, key):
        box = QComboBox()
        box.addItem("All")
        box.addItems(sorted({fare[key] for fare in self.fares}))
        box.currentIndexChanged.connect(self.plot)
        return box

    def plot(self):
        route = self.route_box.currentText()
        date = self.date_box.currentText()

        prices = defaultdict(lambda: defaultdict(list))
        for fare in self.fares:
            if route in ("All", fare["route"]) and date in ("All", fare["depart_date"]):
                prices[fare["airline"]][fare["lead_days"]].append(fare["price"])

        self.axes.clear()
        for airline in sorted(prices):
            days = sorted(prices[airline])
            average = [mean(prices[airline][day]) for day in days]
            self.axes.plot(days, average, marker="o", label=airline)
        self.axes.invert_xaxis()
        self.axes.set_xlabel("days before departure")
        self.axes.set_ylabel("price (GBP)")
        self.axes.legend()
        self.canvas.draw_idle()


app = QApplication(sys.argv)
window = Window(load_fares())
window.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
window.show()
sys.exit(app.exec())
