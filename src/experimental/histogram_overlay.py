import pylab
import numpy
import numpy.random as random

if __name__ == '__main__':
    pylab.ion()
    ax = pylab.subplot(1,1,1)
    r1 = random.normal(0, 1, 1000)
    r2 = random.normal(2, 1, 1000)
    n1, bins1, patches1 = ax.hist(r1, 50, fc='b')
    n2, bins2, patches2 = ax.hist(r2, 50, fc='r')    

    # keep all patches in a list
    patches = []
    patches.extend(patches1)
    patches.extend(patches2)

    splits = numpy.cumsum([0, len(patches1), len(patches2)])
    
    # draw first histogram
    ax.patches = patches[splits[0]:splits[1]]
    ax.set_title('Add histogram 1')
    pylab.draw()

    raw_input("Hit Enter to continue ...")

    # add second histogram
    ax.patches = patches[splits[0]:splits[2]]
    ax.set_title('Add histogram 2')
    pylab.draw()

    raw_input("Hit Enter to continue ...")
    
    # subtract first histogram
    ax.patches = patches[splits[1]:splits[2]]
    ax.set_title('Remove histogram 1')
    pylab.draw()

    raw_input("Hit Enter to continue ...")

    # add back first histogram
    ax.patches = patches[splits[0]:splits[2]]
    ax.set_title('Add back histogram 1')
    pylab.draw()
    
    raw_input("Hit Enter to finish ...")

