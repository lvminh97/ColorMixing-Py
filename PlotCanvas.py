from PyQt5.QtWidgets import QSizePolicy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class PlotCanvas(FigureCanvas):
	def __init__(self, parent = None, width = 5, height = 4, dpi = 100):
		fig = Figure(figsize = (width, height), dpi = dpi)

		FigureCanvas.__init__(self, fig)
		self.setParent(parent)

		FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

	def plot(self, xData, yData, color = 'b'):
		axes = self.figure.add_subplot(111)
		axes.plot(xData, yData, color)
		self.draw()

	def clear(self):
		self.figure.clear()
		self.plot(list(range(400, 701, 10)), [1] + [0] * 30, 'w')