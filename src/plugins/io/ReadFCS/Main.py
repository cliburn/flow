from Model import FlowModel
from flowio import Io
import numpy
import fcs
import os

# def create_comp_matrix(s):
#     """Convert the string representation of compensation matrix to array."""
#     ss = s.split(',')
#     n = int(ss[0])
#     headers = ss[1:n+1]
#     mat = numpy.reshape(map(float, ss[n+1:]), (n, n))
#     return headers, mat

# def compensate(f, data):
#     """Compensate data using spillover matrix."""
#     dc = data[:]
#     headers, comp = create_comp_matrix(f.text['SPILL'])
#     names = [f.text['P%dN' % i] for i in range(1, len(f.names)+1)]
#     indices = [names.index(header) for header in headers]
#     d_comp = numpy.take(data, indices, 0)
#     d_comp = numpy.linalg.solve(comp, d_comp)

#     for j, i in enumerate(indices):
#         dc[i,:] = d_comp[j,:]
#     return dc

# def log_transform(f, data, decades=4.0):
#     """Log transform where indicated."""
#     # upper and lower bounds for channel number
#     dl = data[:]
#     upper = max(map(float, [f.text['P%dR' % i] for i in range(1, len(f.names)+1)]))
#     lower = upper/float(10.0**decades)

#     # clip data
#     dl = numpy.clip(dl, lower, upper)

#     # log transform
#     for i in range(len(f.names)):
#         if f.text.get('P%dDISPLAY' % (i+1), '') == 'LOG': 
#             dl[i] = 1024.0/decades * numpy.log10(dl[i]/lower)
#         else:
#             dl[i] = 1024.0/upper * dl[i]
#     return dl

class ReadFCS(Io):
    newMethods=('ReadFCS','Load FCS data file')
    type = 'Read'
    supported = "FCS files (*.fcs)|*.fcs|All files (*.*)|*.*"

    def ReadFCS(self, filename):
        """reads a fcs file and populates data structures"""
        self.model.ready = False

        f = fcs.FCSReader(filename)
        # headers = f.data.keys()
        headers = f.names
        markersS = [f.text.get('P%dS' % i, None) 
                    for i in range(1, len(headers)+1)]
        markersN = [f.text.get('P%dN' % i, None) 
                    for i in range(1, len(headers)+1)]
        StoN = dict(zip(markersS, markersN))
        NtoS = dict(zip(markersN, markersS))
        
        version = f.header['version']
        # do we need the creator?  It appears to be important for compensating for FACSDiva
        # which we're not doing any more....
        try: 
            creator = f.text['CREATOR']
        except KeyError:
            creator = 'UNKNOWN'
                
        d = numpy.array([f.data[k] for k in f.names], 'd')

        # customization for machine and fcs version
        # if version.count('3.0') and creator.count('FACSDiva'):
            # dc = compensate(f, d)
            # dl = log_transform(f, dc)

        # create a new group
        basename = os.path.basename(filename)
        base, ext = os.path.splitext(basename)
        self.model.NewGroup(base)

        d = numpy.transpose(d)
        data = self.model.hdf5.createArray(self.model.GetCurrentGroup(), 'data', d, 'Original data')
        data.attrs.fields = headers
        data.attrs.fcs_file = basename
        data.attrs.text = f.text
        data.attrs.markersS = markersS
        data.attrs.markersN = markersN
        data.attrs.StoN = StoN
        data.attrs.NtoS = NtoS
        spill = f.text.get('SPILL', None)
        if spill:
            self.model.setSpill(spill)
#             spill = spill.split(',')
#             n = int(spill[0])
#             headers = spill[1:(n+1)]
#             matrix = numpy.reshape(map(float, spill[n+1:]), (n, n))
#             spillover = self.model.hdf5.createArray(self.model.GetCurrentGroup(), 'spillover', matrix)
#             spillover.setAttr('markers', headers)

        try:
            dc = numpy.transpose(dc)
            self.model.NewGroup('Compensated data')
            data_comp = self.model.hdf5.createArray(self.model.GetCurrentGroup(), 'data', dc, 'Data after compensation')
            data_comp.setAttr('fields', headers)
        except NameError:
            pass

        #self.model.current_group = self.model.hdf5.getNode('/')
        self.model.current_array = data
        self.model.UpdateData()
        
