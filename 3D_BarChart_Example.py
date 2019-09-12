from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection = "3d")

ax.set_xlabel("x")
ax.set_ylabel("y") 
ax.set_zlabel("z")
ax.set_xlim3d(0,10)
ax.set_ylim3d(0,10) 
ax.set_zlim3d(0,2)

xpos = [2,5,8,2,5,8,2,5,8]
ypos = [1,1,1,5,5,5,9,9,9]
zpos = np.zeros(9)

dx = np.ones(9)
dy = np.ones(9)
dz = [0.3,0.3,0.3,0.5,0.5,0.5,0.7,0.7,0.7]

ax.bar3d(xpos, ypos, zpos, dx, dy, dz)
plt.gca().invert_xaxis()
plt.show()