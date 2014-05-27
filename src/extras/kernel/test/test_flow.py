import RandomArray
import numpy
from numpy.random import normal
import sys
import fcs
import pylab
sys.path.append('../')
import flow

if __name__ == '__main__':
    data = numpy.concatenate((RandomArray.normal(5, 1, (2000, 2)),
                              RandomArray.normal(7, 1, (2000, 2)),
                              RandomArray.normal(9, 1, (3000, 2)),
                              RandomArray.normal(11, 1, (2000, 2)),
                              RandomArray.normal(13, 1, (1000, 2))), axis=0)

    #     f = fcs.FCSReader("../data/3FITC-4PE.004.fcs")
    #     print f.data.keys()
    #     m = 10000
    #     x1 = numpy.array((f.data['FSC-H'])[:m], 'd')
    #     x2 = numpy.array((f.data['SSC-H'])[:m], 'd')
    #     x3 = numpy.array((f.data['FL1-H'])[:m], 'd')
    #     x4 = numpy.array((f.data['FL2-H'])[:m], 'd')
    
    #     print min(x1), max(x1)
    #     print min(x2), max(x2)
    #     print min(x3), max(x3)
    #     print min(x4), max(x4)

    #     data_unscaled = numpy.transpose([x1, x2, x3, x4])
    #     #data = numpy.transpose([(x1-min(x1))/max(x1), (x2-min(x2))/max(x2), (x3-min(x3))/max(x3), (x4-min(x4))/max(x4)])
    #     data = data_unscaled
    # data = [map(float, line.strip().split(',')) for line in open('c_data.txt').readlines()]
    n, dim = numpy.shape(data)

    #print n
    #print dim
    
    k = n
    h = 0.25
    alpha = 0.0
    #print "Creating uniform analyzer using factory method"
    ap = flow.create_analyzer("Uniform", data, dim, n, k, h, alpha)

    #print "Test h functions"
    #print ap.get_h()

    #print "Test find seeds"
    # min_sep = ap.calc_h()
    # print min_sep
    min_sep = 0.1
    # seeds = ap.find_seeds(min_sep, 10, 100)
    seeds = ap.find_seeds_simple(500)
    #print "num seeds:", len(seeds)

    #print "Test find modes"
    modes = ap.find_modes(seeds, 1e-4)
    #print "num modes:", len(modes)
    # for mode in modes:
        # print mode, modes[mode]

    #print "Test merge modes"
    min_merge_sep = 0.01
    mmodes = ap.merge_modes(modes, min_merge_sep)
    #print "num merge modes:", len(mmodes)
    # for mmode in mmodes:
        # print mmode, mmodes[mmode]
    

    #print "Test support"
    min_pop = 2
    mmodes = ap.pop_check_modes(mmodes, min_pop)
    #print "num supported modes:", len(mmodes)
    # for mmode in mmodes:
        # print mmode, mmodes[mmode]

    #print "Test dip"
    dip_ratio = 0.85
    mmodes = ap.check_modes(mmodes, dip_ratio)
    #print "num dip modes:", len(mmodes)
    #print mmodes
    # for mmode in mmodes:
        # print mmode, mmodes[mmode]
        #         print ">>>", data_unscaled[mmodes[mmode][0]]

    #print "Test label seeds"
    # seed_labels = flow.label_seeds(mmodes)
    # for seed_label in seed_labels:
        # print seed_label, seed_labels[seed_label]

    #print "Test label points"
    # nbrs = 1+int(numpy.floor(len(mmodes)/5.0))
    nbrs = 1
    clusters = flow.label_points("Epanechnikov", data, mmodes, nbrs)
    counts = {}
    for k in clusters.values():
        counts[k] = counts.get(k, 0) + 1
    #print counts
    

    #     mm = [m[:2] for m in mmodes]
    #     x, y = zip(*mm)
    #     pylab.figure(figsize=[8,8])
    #     pylab.scatter(x, y, 30, 'r')
    #     dx, dy = zip(*data)[:2]
    #     pylab.scatter(dx, dy, .05, [0.9, 0.9, 0.9])
    #     pylab.xlabel('Dimension 1')
    #     pylab.ylabel('Dimension 2')
    #     pylab.axis('equal')
    #     pylab.show()

#     print [clusters[i] for i in range(100)]
#     pylab.figure(figsize=[8,8])
#     dc = map(float, [clusters[i] for i in range(len(data))])
#     dx, dy = zip(*data)[:2]
#     pylab.scatter(dx, dy, 5, dc, cmap=pylab.cm.jet, edgecolors='none')
#     pylab.xlabel('Dimension 1')
#     pylab.ylabel('Dimension 2')
#     pylab.axis('equal')
#     pylab.show()


#     f = open('labeled_pts.txt', 'w')
#     for pt in clusters.keys():
#         f.write(' '.join(map(str, list(data_unscaled[pt]))) + ' ' + str(clusters[pt]) + '\n')
#     f.close()
#     keys = clusters.keys()
#     values = clusters.values()
#     adict = {}
#     for key in keys:
#         adict[clusters[key]] = adict.get(clusters[key], 0) + 1
#     for item in adict.items():
#         print item

