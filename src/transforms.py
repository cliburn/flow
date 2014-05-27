"""Test for logical, biexponential, hyperlog transforms."""

from numpy import arange, exp, vectorize, max, sign, log, log10, zeros, array, where, greater, min, log10, log, clip, take, argsort, arcsinh, concatenate, mean, std
from numpy.random import normal, lognormal
from scipy.optimize import fsolve, bisect as bisection
from scipy import interpolate
from special_funcs import productlog
from logicle import hyperlog, logicle, quantile, S

def ScaleOp(data, indices, inputs):
    for i in indices:
        top = max(data[:, i])
        bot = min(data[:, i])
        data[:, i] = inputs['lower'] + (inputs['upper']-inputs['lower'])*(data[:, i] - bot)/(top-bot)

def NormalScaleOp(data, indices, inputs):
    for i in indices:
        data[:, i] = (data[:, i] - mean(data[:, i]))/std(data[:, i])

def ClipOp(data, indices, inputs):
    for i in indices:
        data[:, i] = clip(data[:, i], inputs['lower'], inputs['upper'])

def LinearOp(data, indices, inputs):
    for i in indices:
        data[:, i] = (inputs['a'] + inputs['b']*data[:, i])

def QuadraticOp(data, indices, inputs):
    for i in indices:
        data[:, i] = (inputs['a']*data[:, i]**2 + inputs['b']*data[:, i] + inputs['c'])

def LogOp(data, indices, inputs):
    for i in indices:
        data[:, i] = inputs['r']/inputs['d'] * \
            log10(where(greater(data[:, i], inputs['l']), data[:, i], 1))

def LognOp(data, indices, inputs):
    for i in indices:
        data[:, i] = inputs['r']/inputs['d'] * \
            log(where(greater(data[:, i], inputs['l']), data[:, i], 1))

def BiexponentialOp(data, indices, inputs):
    for i in indices:
        data[:, i] = biex(data[:, i], inputs['a'], inputs['b'],
                                     inputs['c'], inputs['d'], inputs['f'])

def LogicleOp(data, indices, inputs):
    m = inputs['M'] * log(10) # convert from log10 to log
    for i in indices:
        d = data[:, i]
        r = quantile(d[d<0], inputs['r'])
        data[:, i] = logicle(data[:, i], inputs['T'], m, r)

def HyperlogOp(data, indices, inputs):
    for i in indices:
        data[:, i] = hyperlog(data[:, i], inputs['b'], inputs['d'], inputs['r'])

def ArcsinhOp(data, indices, inputs):
    for i in indices:
        data[:, i] = arcsinh(inputs['a']+inputs['b']*data[:, i]) + inputs['c']

def B(y, x, a, b, c, d, f):
    return a*exp(b*y) - c*exp(-d*y) + f - x

def biex0(x, a, b, c, d, f):
    return bisection(B, -100, 100, (x, a, b, c, d, f))
biex0 = vectorize(biex0)

def biex(x, a, b, c, d, f, order=2, intervals=1000.0):
    """Spline3 interpolation."""
    ub = log(max(x)+1-min(x))
    xx = exp(arange(0, ub, ub/intervals))-1+min(x)
    yy = biex0(xx, a, b, c, d, f)
    t = interpolate.splrep(xx, yy, k=order)
    return interpolate.splev(x, t)

if __name__ == '__main__':
    import pylab

    d1 = normal(0, 50, (50000))
    d2 = lognormal(8, 1, (50000))
    d3 = concatenate([d1, d2])

    T = 262144
    d = 4
    m = d*log(10)
    r = quantile(d3[d3<0], 0.05)
    w = (m-log(T/abs(r)))/2

    pylab.clf()
    pylab.figtext(0.5, 0.94, 'Logicle transform with r=%.2f, d=%d and T=%d\nData is normal(0, 50, 50000) + lognormal(8, 1, 50000)' % (r, d, T),
                  va='center', ha='center', fontsize=12)

    pylab.subplot(3,1,1)
    x = arange(0, m, 0.1)
    pylab.plot(x, S(x, 0, T, m, w))
    locs, labs = pylab.xticks()
    pylab.xticks([])
    pylab.yticks([])
    pylab.ylabel('Inverse logicle')

    pylab.subplot(3,1,2)
    pylab.hist(d3, 1250)
    locs, labs = pylab.xticks()
    pylab.xticks([])
    pylab.yticks([])
    pylab.ylabel('Raw data')

    pylab.subplot(3,1,3)
    pylab.hist(logicle(d3, T, m, r), 1250)
    locs, labs = pylab.xticks()
    pylab.xticks([])
    pylab.yticks([])
    pylab.ylabel('Data after transform')

    # pylab.savefig('logicle.png')
    pylab.show()
