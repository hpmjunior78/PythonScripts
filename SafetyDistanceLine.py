#!/usr/bin/python

## According to the traffic safety in Europe, a driver must have, at least,
## 2 seconds of reaction in order to be capable of avoiding an accident.
## This script computes a safety distance of reaction according to the 2 seconds time
## and the speed of two vehicles travelling towards one another.

import pylab
import numpy as np
import math

x = np.linspace(1,20)
y1 = 100 + x * 100
y2 = 100 * np.log10(x * 100)
y3 = 100 + x * np.log10(x * 100)
y4 = 100 * np.log10(x)
y5 = 100 + x * 50
# compose plot
pylab.plot(x,y1,'--') # 
#pylab.plot(x,y2,'-.') # 
#pylab.plot(x,y3,'.') # 
#pylab.plot(x,y4,'*') #
pylab.plot(x,y5,'x') #
pylab.show() # show the plot