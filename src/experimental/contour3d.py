from numpy import *
import pylab as p
import matplotlib.axes3d as p3

delta = 0.025
x = arange(-3.0, 3.0, delta)
y = arange(-2.0, 2.0, delta)
X, Y = p.meshgrid(x, y)
Z1 = p.bivariate_normal(X, Y, 0.2, 0.2, 0.0, 0.0)
Z2 = p.bivariate_normal(X, Y, 0.35, 0.5, 1, 1)
Z3 = p.bivariate_normal(X, Y, 0.135, 0.35, 1.5, 1)
Z4 = p.bivariate_normal(X, Y, 0.5, 0.5, 2.1, -1)
Z5 = p.bivariate_normal(X, Y, 0.35, 0.55, -1, -1)
# difference of Gaussians
Z = 10.0 * (Z2 + Z1 + Z3 + Z4 + Z5)
fig=p.figure()
ax = p3.Axes3D(fig)
ax.contour3D(X,Y,Z,250)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
p.show()
