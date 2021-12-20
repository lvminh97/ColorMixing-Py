from ColorParams import *
import numpy as np
import math

class Helper:
	BIT0 = 1
	BIT1 = 2
	BIT2 = 4
	BIT3 = 8
	BIT4 = 16
	BIT5 = 32
	BIT6 = 64
	BIT7 = 128

	def func(x):
		if x > 0.008856:
			return x ** (1 / 3)
		else:
			return (903.3 * x +16) / 116

	def sampleToXYZ(sample, type = 0): # 0 -> 2* ; 1 -> 10*
		if type == 0:
			K = sum([Illuminant.D65_ILL[i] * ObserverFunction.Y2[i] for i in range(31)])
			X = sum([Illuminant.D65_ILL[i] * ObserverFunction.X2[i] * sample[i] for i in range(31)])
			Y = sum([Illuminant.D65_ILL[i] * ObserverFunction.Y2[i] * sample[i] for i in range(31)])
			Z = sum([Illuminant.D65_ILL[i] * ObserverFunction.Z2[i] * sample[i] for i in range(31)])
		else:
			K = sum([Illuminant.D65_ILL[i] * ObserverFunction.Y10[i] for i in range(31)])
			X = sum([Illuminant.D65_ILL[i] * ObserverFunction.X10[i] * sample[i] for i in range(31)])
			Y = sum([Illuminant.D65_ILL[i] * ObserverFunction.Y10[i] * sample[i] for i in range(31)])
			Z = sum([Illuminant.D65_ILL[i] * ObserverFunction.Z10[i] * sample[i] for i in range(31)])
		return [X / K, Y / K, Z / K]

	def rgbAdj(x): ####
		res = 0
		if x <= -0.0031308:
			res = 0
		elif x <= 0.0031308:
			res = 12.92 * x
		else:
			res = 1.055 * (x ** 0.41666) - 0.055
		if 0 <= res <= 1:
			return res
		elif res < 0:
			return 0
		else:
			return 1

	def sampleToRGB(sample):
		X, Y, Z = Helper.sampleToXYZ(sample)
		r = Helper.rgbAdj(3.2404542 * X - 1.5371385 * Y - 0.4985314 * Z)
		g = Helper.rgbAdj(-0.969266 * X + 1.8760108 * Y + 0.0415560 * Z)
		b = Helper.rgbAdj(0.0556434 * X - 0.2040259 * Y + 1.0572252 * Z)
		return list(map(lambda x: round(x * 255), [r, g, b]))

	def sampleToCIELAB(sample, type = 0):
		X, Y, Z = Helper.sampleToXYZ(sample, type)
		L = 116 * Helper.func(Y / Illuminant.D65_REF['Y']) - 16
		a = 500 * (Helper.func(X / Illuminant.D65_REF['X']) - Helper.func(Y / Illuminant.D65_REF['Y']))
		b = 200 * (Helper.func(Y / Illuminant.D65_REF['Y']) - Helper.func(Z / Illuminant.D65_REF['Z']))
		return [L, a, b]

	def sampleToCIELCH(sample):
		L, a, b = Helper.sampleToCIELAB(sample)
		C = (a * a + b * b) ** 0.5
		if a != 0:
			H = math.atan(b / a) / 3.1415926 * 180
		else:
			H = 90 if b >= 0 else 270
		if a < 0:
			H += 180
		return [L, C, H]

	def deltaE(Lab1, Lab2):
		s = 0
		for i in range(3):
			s += (Lab1[i] - Lab2[i]) ** 2
		return s ** 0.5

	def deltaAB(Lab1, Lab2):
		s = 0
		for i in range(1, 3):
			s += (Lab1[i] - Lab2[i]) ** 2
		return s ** 0.5
	def deltaH(Lch1, Lch2):
		return abs(Lch1[2] - Lch2[2])
	def deltaC(Lch1, Lch2):
		return abs(Lch1[1] - Lch2[1])
	def deltaCH(Lch1, Lch2):
		s = 0
		for i in range(1, 3):
			s += (Lch1[i] - Lch2[i]) ** 2
		return s ** 0.5

class Process:
	def __init__(self):
		self.basicMat = []
		self.ratio = []
		self.minDiff = []
		self.minDiff2 = []
		self.ratioFinal = []
		self.sampleFinal = []
		self.LAB_Ref = []
		self.len = 0

	def backtrack(self, pos, bound, step, max):
		for a in range(bound[pos][0], bound[pos][1] + 1, step):
			if a < 0:
				continue
			elif sum(self.ratio[:pos]) + a <= max:
				self.ratio[pos] = a
				if pos < self.len - 2:
					self.backtrack(pos + 1, bound, step, max)
				elif sum(self.ratio[:self.len - 1]) < max:
					self.ratio[self.len - 1] = max - sum(self.ratio[:self.len - 1])
					ratioMat = np.matrix(list(map(lambda x: x / max, self.ratio))).T
					sampleRes = self.basicMat * ratioMat
					LAB_Act = Helper.sampleToCIELAB(sampleRes.T.tolist()[0])
					# LAB_Act = Helper.sampleToCIELCH(sampleRes.T.tolist()[0])
					# if Helper.deltaH(LAB_Act, self.LAB_Ref) < self.minDiff or (Helper.deltaH(LAB_Act, self.LAB_Ref) == self.minDiff and Helper.deltaC(LAB_Act, self.LAB_Ref) <= self.minDiff2):
					# if Helper.deltaCH(LAB_Act, self.LAB_Ref) < self.minDiff:

					if Helper.deltaAB(LAB_Act, self.LAB_Ref) < 5 and self.minDiff2 > abs(LAB_Act[0] - self.LAB_Ref[0]):
						self.minDiff2 = abs(LAB_Act[0] - self.LAB_Ref[0])
						self.ratioFinal = [i / max for i in self.ratio]
						self.sampleFinal = sampleRes.T.tolist()[0]
					elif Helper.deltaAB(LAB_Act, self.LAB_Ref) < self.minDiff:
						self.minDiff = Helper.deltaAB(LAB_Act, self.LAB_Ref)
						self.ratioFinal = [i / max for i in self.ratio]
						self.sampleFinal = sampleRes.T.tolist()[0]
			else:
				return

	def compute(self, basicColorChosen, sample, bound, step, max = 100):
		basic = []
		if basicColorChosen & Helper.BIT0:
			basic += [BasicColor.YELLOW]
		if basicColorChosen & Helper.BIT1:
			basic += [BasicColor.RED]
		if basicColorChosen & Helper.BIT2:
			basic += [BasicColor.RH_RED]
		if basicColorChosen & Helper.BIT3:
			basic += [BasicColor.PINK]
		if basicColorChosen & Helper.BIT4:
			basic += [BasicColor.BLUE]
		if basicColorChosen & Helper.BIT5:
			basic += [BasicColor.BLACK]
		self.len = len(basic)
		self.basicMat = np.matrix(basic).T
		self.LAB_Ref = Helper.sampleToCIELAB(sample)
		# self.LAB_Ref = Helper.sampleToCIELCH(sample)

		self.minDiff = 999999
		self.minDiff2 = 999999
		self.ratio = [0] * self.len
		self.ratioFinal = []
		self.sampleFinal = []

		self.backtrack(0, bound, step, max)
		return [self.ratioFinal, self.sampleFinal]

