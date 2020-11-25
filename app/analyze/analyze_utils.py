import numpy as np

def hour2min(series, minutes=15):
    retval = []
    for i in series:
        retval.append(int(np.floor((i.hour * 60 + i.minute) * 60 + i.second) / 60 / minutes))
    return retval

def hour2min15(data):
    retval = []
    for i in data:
        temp = i.split(':')
        to15 = int(np.floor(((int(temp[0])*3600 + int(temp[1])*60 + int(temp[0]))/900)))
        retval.append(to15)
    return retval

# params[i]: 
def gauss(x,mu,sigma,A):
    return A*np.exp(-(x-mu)**2/2/sigma**2)

def n_modal(x, *params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        mu = params[i]
        sigma = params[i + 1]
        A = params[i + 2]
        y += gauss(x, mu, sigma, A)
    return y

def gauss_mix(x,*params):
    y = np.zeros_like(x)
    for i in range(0, len(params), 3):
        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]
        y = y + amp * np.exp( -((x - ctr)/wid)**2)
    return y