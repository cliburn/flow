import numpy
import pylab

delta = 0.025
x = numpy.arange(-3.0, 3.0, delta)
y = numpy.arange(-2.0, 2.0, delta)
X, Y = pylab.meshgrid(x, y)
Z1 = pylab.bivariate_normal(X, Y, 0.2, 0.2, 0.0, 0.0)
Z2 = pylab.bivariate_normal(X, Y, 0.35, 0.5, 1, 1)
Z3 = pylab.bivariate_normal(X, Y, 0.135, 0.35, 1.5, 1)
Z4 = pylab.bivariate_normal(X, Y, 0.5, 0.5, 2.1, -1)
Z5 = pylab.bivariate_normal(X, Y, 0.35, 0.55, -1, -1)
# difference of Gaussians
Z = 10.0 * (Z2 + Z1 + Z3 + Z4 + Z5)

# interpolate values 
fig=pylab.figure()
ax = pylab.subplot(111)
xpts = numpy.random.uniform(-3, 3, 10000)
ypts = numpy.random.uniform(-2, 2, 10000)
xint = map(int, (xpts + 3)/delta)
yint = map(int, (ypts + 2)/delta)
zvals = [Z[_y, _x] for _x, _y in zip(xint, yint)]

ax.scatter(xpts, ypts, s=1, c=zvals, edgecolors='none')
ax.set_xlabel('X')
ax.set_ylabel('Y')
pylab.show()
