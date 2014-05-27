from flowio import Io
import numpy
import os

class ReadCSV(Io):
    """Expects an .out file containing tab-separated n*p data,
    and a .txt containing column headers one per line"""
    newMethods=('ReadCSV','Load CSV data file')
    type = 'Read'
    supported = "CSV files (*.out)|*.out|All files (*.*)|*.*"

    def ReadCSV(self, filename, sep=None):
        """reads a csv file and populates data structures"""
        # self.model.ready = False

        arr = numpy.loadtxt(filename, delimiter=sep)
        headers = numpy.loadtxt(filename.replace('out', 'txt'),
                                dtype='string')

#         text = open(filename).readlines()
#         headers = open(filename.replace('out', 'txt')).readlines()
#         # headers = text[0].strip('\n').strip('\r').split(sep)
#         arr = numpy.array([map(float, line.strip().split(sep)) for line in text[0:]])        

        # create a new group
        basename = os.path.basename(filename)
        base, ext = os.path.splitext(basename)
        self.model.NewGroup(base)
            
        # create an hdf5 file
        self.model.LoadData(headers, arr, 'Original data')
