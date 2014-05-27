"""Optimal classification in the sense of minimizing mis-classification is to just assign to class with highest posterior probability. If we want to increase specificity, can assign a threshold for the higest posterior probability - anything below the threshold is then 'unclassified'"""

import numpy
import tables

if __name__ == '__main__':
    probx = numpy.transpose([map(float, line.strip().split()) for line in open('save_probx_8_probx_out').readlines()])

    threshold = 0.9
    z = numpy.zeros(len(probx), 'i')
    nk = probx.shape[1]
    
    print ">>>", probx.shape, nk

    for i, k in enumerate(numpy.argmax(probx, axis=1)):
        if probx[i, k] < threshold:
            z[i] = nk
        else:
            z[i] = k

    fi = tables.openFile('/Users/cliburn/hg/flow2/data/3FITC-4PE.004.h5')
    data = fi.root.data[:]
    fields = fi.root.data.getAttr('fields')
    fi.close()

    fo = tables.openFile('/Users/cliburn/hg/flow2/data/classifier.h5', 'w')
    fo.createArray('/', 'data', data, 'data')
    fo.root.data.setAttr('fields', fields)
    fo.createArray('/', 'z', z, 'z')

    fo.close()

#     fi.close()
#     fo.close()
