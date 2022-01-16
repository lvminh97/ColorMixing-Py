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

	def plot(self, xData, yData, yData2):
		self.figure.clear()
		axes = self.figure.add_subplot(1, 1, 1, yticks = [0, 0.2, 0.4, 0.6, 0.8, 1.0])
		axes.plot(xData, yData, 'b')
		axes.plot(xData, yData2, 'r')
		axes.plot([400, 400], [0, 1], 'w')
		self.draw()

	def clear(self):
		self.figure.clear()
		axes = self.figure.add_subplot(1, 1, 1, yticks = [0, 0.2, 0.4, 0.6, 0.8, 1.0])
		axes.plot(list(range(400, 701, 10)), [1] + [0] * 30, 'w')