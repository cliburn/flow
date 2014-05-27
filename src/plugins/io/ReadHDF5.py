from flowio import Io

class ReadHDF5(Io):
    newMethods=('ReadHDF5','Load HDF5 data file')
    type = 'Read'
    supported = "HDF5 files (*.h5)|*.h5|All files (*.*)|*.*"
    def ReadHDF5(self, hdf5File):
        self.model.open(hdf5File)

