import numpy
import pylab

xn1 = numpy.random.normal(0, 0.63, 10000)
yn1 = numpy.random.normal(0, 0.63, 10000)

xn2 = numpy.random.normal(0.5, 0.23, 15000)
yn2 = numpy.random.normal(0.5, 0.23, 15000)

xu = numpy.random.uniform(-5, 5, 1000)
yu = numpy.random.uniform(-5, 5, 1000)

x = numpy.concatenate([xn1, xn2, xu])
y = numpy.concatenate([yn1, yn2, yu])

bins = 100
z, xedge, yedge = numpy.histogram2d(y, x, bins=[bins, bins], 
                                    range=[(numpy.min(y), numpy.max(y)),
                                           (numpy.min(x), numpy.max(x))])

# interpolate to get rid of blocky effect
# from http://en.wikipedia.org/wiki/Bilinear_interpolation
xfrac, xint = numpy.modf((x - numpy.min(x))/
                         (numpy.max(x)-numpy.min(x))*(bins-1))
yfrac, yint = numpy.modf((y - numpy.min(y))/
                         (numpy.max(y)-numpy.min(y))*(bins-1))

zvals = numpy.zeros(len(xint), 'd')
for i, (_x, _y, _xf, _yf) in enumerate(zip(xint, yint, xfrac, yfrac)):
    q11 = z[_y, _x]
    if _xf:
        q12 = z[_y, _x+1]
    else:
        q12 = 0
    if _yf:
        q21 = z[_y+1, _x]
    else:
        q21 = 0
    if _xf and _yf:
        q22 = z[_y+1, _x+1]
    else:
        q22 = 0

    zvals[i] = q11*(1-_xf)*(1-_yf) + q21*(1-_xf)*(_yf) + \
        q12*(_xf)*(1-_yf) + q22*(_xf)*(_yf)

ax = pylab.subplot(111)
ax.scatter(x, y, s=1, c=zvals, edgecolors='none')

# ax.contour(numpy.linspace(-3, 3, num=150), numpy.linspace(-3, 3, num=150), z)
ax.set_xlabel('X')
ax.set_ylabel('Y')
pylab.show()
