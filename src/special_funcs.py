from numpy import log

def productlog(x, prec=1e-12):
    """Productlog or LambertW function computes principal solution for w in f(w) = w*exp(w).""" 
    #  fast estimate with closed-form approximation
    if (x <= 500):
        lxl = log(x + 1.0)
        return 0.665 * (1+0.0195*lxl) * lxl + 0.04
    else:
        return log(x - 4.0) - (1.0 - 1.0/log(x)) * log(log(x))

