#! /usr/bin/env python
import sys

class Histogram:
	def __init__(self):
		self.bins = []
		self.counts = {}

	def add(self, bin, delta=1):
		if self.counts.has_key(bin):
			self.counts[bin] += delta
		else:
			self.bins.append(bin)
			self.counts[bin] = delta

	def stdout(self):
		COLUMNS = 80
		maxlen = max(map(lambda s: len(s), self.counts.keys()))
		COLUMNCHAR = "#"
		maxvalue = max(self.counts.values())
		for bin in self.bins:
			formatstring = "%" + str(maxlen) + "s: %s (%d)"
			print formatstring % (bin, COLUMNCHAR * (COLUMNS * self.counts[bin] / maxvalue), self.counts[bin])


def main(argv = sys.argv):
	# detects whether have pipe line parsing in
	if not sys.stdin.isatty():
		h = Histogram()
		for s in sys.stdin:
			s = s.strip("\n\r")
			h.add(s)
		h.stdout()


if __name__=="__main__":
	main()

