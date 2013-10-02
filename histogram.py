#! /usr/bin/env python
import sys


class Histogram:
	"""A histogram representation.

	You could possible use collections.Counter(...) for this instead.
	"""
	def __init__(self):
		"""Constructor."""
		self.bins = []
		self.counts = {}

	def add(self, bin, delta=1):
		"""Count the occurence of bin.

		The count is incremented by delta.
		"""
		if self.counts.has_key(bin):
			self.counts[bin] += delta
		else:
			self.bins.append(bin)
			self.counts[bin] = delta

	def write(self):
		"""Write the histogram to stdout."""
		# The width of the terminal
		COLUMNS = 80
		
		maxlen = max(map(lambda s: len(s), self.counts.keys()))
		COLUMNCHAR = "#"
		maxvalue = max(self.counts.values())
		for bin in self.bins:
			formatstring = "%" + str(maxlen) + "s: %s (%d)"
			print formatstring % (bin, COLUMNCHAR * (COLUMNS * self.counts[bin] / maxvalue), self.counts[bin])


def main(argv = sys.argv):
	"""The main(...) function responsible for initial execution."""
	h = Histogram()
	for s in sys.stdin:
		s = s.strip("\n\r")
		h.add(s)
	h.write()


if __name__=="__main__":
	main()

