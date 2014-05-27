"""Class to interpret FCS 3.0 data. Requires >= python2.4"""
import struct
import cStringIO
import bitbuffer
import operator
import os
from utils import log2, fmt_integer, mask_integer
#try:
#	import psyco
#	psyco.full()
#except ImportError:
#	pass

class FCSReader(object):
	"""A class to read FCS3.0 data files."""
	def __init__(self, filename):
		self.name = '_'.join(os.path.basename(filename).split('.')[0:-1])
		self._file = cStringIO.StringIO(open(filename, 'rb').read())
		self.header = self.parse_header()
		self.text = self.parse_pairs(self.header['text_first'], 
					     self.header['text_last'])
		self.analysis = self.parse_pairs(self.header['analysis_first'], 
						 self.header['analysis_last'])
		# !! does not handle case where bit width is specified as '*'
		self.bitwidths = [int(getattr(self, 'P%dB' % i)) for i in range(1, int(self.PAR)+1)]
		self.ranges = [int(getattr(self, 'P%dR' % i)) for i in range(1, int(self.PAR)+1)]
		self.names = []
		self.altnames = []
		self.display = []
		self.max_value = []
		for i in range(1, int(self.PAR)+1):
			name = getattr(self, 'P%dS' % i)
			short_name = getattr(self, 'P%dN' % i)
			self.display.append(getattr(self, 'P%dDISPLAY' % i))
			self.max_value.append(getattr(self, 'P%dR' % i))
			if name:
				self.names.append(name)
			elif short_name:
				self.names.append(short_name)
			else:
				self.names.append('V%d' % (i+1))

			if short_name:
				self.altnames.append(short_name)
			elif name:
				self.altnames.append(name)
			else:
				self.altnames.append('V%d' % (i+1))

				
		#print zip(self.names, self.altnames)
		#print self.name
		#print ">>>", self.display
		#print ">>>", self.max_value

		#DEBUG-CLIBURN
		#self.names = self.altnames
		

# 		print self._file
# 		print self.header
# 		for item in sorted(self.text):
# 			#if item.lower().count('data'):
# 			print item, self.text[item]
# 		print self.analysis
# 		print self.bitwidths
# 		print self.ranges
# 		print self.names
		self.data = self.parse_data()
		
	def __str__(self):
		return self.name
		
	def read_bytes(self, start, stop):
		"""Read in bytes from start to stop inclusive."""
		self._file.seek(start)
		return self._file.read(stop-start+1)
	
	def read_bits(self, start, stop):
		"""Basic idea is get read the appropriate number of bytes, 
		then use a bitmask to extract the desired bits, and finally
		convert the bits to integer.
		Pseudocode:
		b = length of item in bits
		name = number of items
		c <- read in 4 byte chunks and interpret as integer (assume length of item < 32 bits)
		bitmask <- make a 4 byte bitmask with 32-b 0's and b 1's
		sb = 0
		while sb < 16:
			extract integer using (bitmask & c)
			right shift by b bits
		jump 2 bytes and read another 4 bytes (so overlap with previous)
		c <- shift as appropriate to align
		repeat
		"""
		pass
	
	def check_crc(self):
		"""CRC16 check - probably use Boost:CRC version if necessary."""
		pass
		
	def parse_header(self):
		"""Get offsets from FCS header."""
		header = {}
		header['version'] = self.read_bytes(0, 5)
		header['text_first'] = int(self.read_bytes(10, 17))
		header['text_last'] = int(self.read_bytes(18, 25))
		header['data_first'] = int(self.read_bytes(26, 33))
		header['data_last'] = int(self.read_bytes(34, 41))
		header['analysis_first'] = int(self.read_bytes(42, 49))
		header['analysis_last'] = int(self.read_bytes(50, 57))
		return header


	def parse_pairs(self, first, last):
		"""Get data pairs from TEXT or ANALYSIS sections."""
		if first == last:
			return {}
		else:
			delim = self.read_bytes(first, first)
			text = [s.strip() for s in self.read_bytes(first+1, last).replace('$', '').split(delim)]
			return dict(zip(text[::2], text[1::2]))
	
	def parse_data(self):
		"""Extract binary or other values from DATA section."""
		mode = self.MODE
		first = self.header['data_first']
		last = self.header['data_last']
		if first == 0 and last == 0:
			first = int(self.text['BEGINDATA'])
			last = int(self.text['ENDDATA'])

		if mode == 'L':
			data = self.parse_list_data(first, last)
		elif mode == 'C':
			data = self.parse_correlated_data(first, last)
		elif mode == 'U':
			data = self.parse_uncorrelated_data(first, last)
		return data

	def get_byte_order(self):
		if self.BYTEORD == '1,2,3,4':
			byte_order = '<'
			#DEBUG -FCS FILES ON WINDOWS READ WRONGLY
			#byte_order = '>@'
		elif self.BYTEORD == '4,3,2,1':
			byte_order = '>'
		else:
			# some strange byte order specified, use native byte order
			print "Unknown byte order: %s" % self.BYTEORD
			byte_order = '@'
		return byte_order
			
	def parse_list_data(self, first, last):
		"""Extract list data."""
		data_type = self.DATATYPE
		byte_order = self.get_byte_order()
	
		if data_type == 'I':
			data = self.read_integer_data(byte_order, first, last)
		elif data_type in ('F', 'D'):
			data = self.read_float_data(byte_order, first, last)
		elif data_type == 'A':
			data = self.read_ascii_data(byte_order, first, last)
		else:
			print "Unknown data type: %s" % data_type
		return data

	def read_integer_data(self, byte_order, first, last):
		"""Extract integer list data."""
		data = {}
		bitwidths, names, ranges = self.bitwidths, self.names, self.ranges
		unused_bitwidths = map(int, map(log2, ranges))
		# check that bitwidths can be handled by struct.unpack

		# DEBUG
		if reduce(operator.and_, [item in [8, 16, 32] for item in bitwidths]):
			print ">>> Regular"
			if len(set(bitwidths)) == 1: # uniform size for all parameters
				num_items = (last-first+1)/struct.calcsize(fmt_integer(bitwidths[0]))
				tmp = struct.unpack('%s%d%s' % (byte_order, num_items, fmt_integer(bitwidths[0])), 
														self.read_bytes(first, last))
# 				if bitwidths[0]-unused_bitwidths[0] != 0: # not all bits used - need to mask
# 					bitmask = mask_integer(bitwidths[0], unused_bitwidths[0]) # assume same number of used bits
# 					tmp = [bitmask & item for item in tmp]
				for i, name in enumerate(names):
					data[name] = tmp[i::len(names)]
				return data
			else: # parameter sizes are different e.g. 8, 8, 16,8, 32 ... do one at a time
				cur = first
				while cur < last:
					for i, bitwidth in enumerate(bitwidths):
						bitmask = mask_integer(bitwidth, unused_bitwidths[i])
						nbytes = bitwidth/8
						bin_string = self.read_bytes(cur, cur+nbytes-1)
						cur += nbytes
						val = bitmask & struct.unpack('%s%s' % (byte_order, fmt_integer(bitwidth)), bin_string)[0]
						data.setdefault(names[i], []).append(val)
		else: # bitwidths are non-standard
			print "<<< Irregular"
			bits = bitbuffer.BitBuffer(open('../data/' + self.name + '.fcs', 'rb').read())
			print ">>>", self.PAR, self.TOT
			bits.seek(first*8)
			for event in range(int(self.PAR)*int(self.TOT)):
				i = event % int(self.PAR)
				val = bits.readbits(bitwidths[i])
				data.setdefault(names[i], []).append(val)
		return data
		
	def read_float_data(self, byte_order, first, last):
		"""Faster version - reads in single chunk of float data."""
		data = {}
		names = self.names
		datatype = self.DATATYPE.lower()
		num_items = (last-first+1)/struct.calcsize(datatype) 
		tmp = struct.unpack('%s%d%s' % (byte_order, num_items, datatype), self.read_bytes(first, last))
		for i, name in enumerate(names):
			data[name] = tmp[i::len(names)]
		return data
	
	def read_ascii_data(self, byte_order, first, last):
		"""Extract ASCII list data."""
		data = {}
		names, bitwidths = self.names, self.bitwidths
		cur = first
		while cur < last:
			for i, bitwidth in enumerate(bitwidths):
				bin_string = self.read_bytes(cur, cur+bitwidth-1)
				cur += bitwidth
				data.setdefault(names[i], []).append(int(struct.unpack('%s%dB' % (byte_order, bitwidth), bin_string)[0]))
		return data
	
	def parse_correlated_data(self, first, last):
		"""Extract correlated histogram data."""
		return {}
	
	def parse_uncorrelated_data(self, first, last):
		"""Extract uncorrelated histogram data."""
		return {}
	
	def to_csv(self, outfile, delim=',', header=True):
		"""Export data to csv file."""
		fileout = open(outfile, 'w')
		if header:
			keys = self.data.keys()
			fileout.write(delim.join(keys) + '\n')
		for item in zip(*[self.data[k] for k in keys]):
			fileout.write(delim.join(map(str, item)) + '\n')
		fileout.close()
	
	def get_version(self):
		"""Return version from Header."""
		return self.header.get('version', None)
	
	def __getattr__(self, name):
		"""For convenience, allow attribute notation for 'text' and 'analysis' dictionary access."""
		try:
			return self.text[name]
		except KeyError:
			try:
				return self.analysis[name]
			except KeyError:
				return None
	
	# properties for encapsulation
	version = property(get_version)

if __name__ == '__main__':
	pass
	
