from cProfile import label
from operator import imod
import re
from turtle import color
import numpy as np 
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt

rng = np.random.RandomState(1)
x = np.sort(200*rng.rand(100,1)-100, axis=0)
y = np.array([np.pi*np.sin(x).ravel(), np.pi*np.cos(x).ravel()]).T
y[::5,:] += (0.5-rng.rand(20,2))

regr_1 = DecisionTreeRegressor(max_depth=2)
regr_2 = DecisionTreeRegressor(max_depth=5)
regr_1.fit(x,y)
regr_2.fit(x,y)

x_test = np.arange(-100.0,100.0,0.01)[:,np.newaxis]
y_1 = regr_1.predict(x_test)
y_2 = regr_2.predict(x_test)

plt.figure()
s=25
plt.scatter(y[:,0],y[:,1],c="navy",s=s,edgecolors="black", label="data")
plt.scatter(y_1[:,0],y_1[:,1],c="cornflowerblue",s=s,edgecolors="black",label="max_depth=2")
plt.scatter(y_2[:,0],y_2[:,1],c="red",s=s,edgecolors="black",label="max_depth=5")
plt.xlim([-6,6])
plt.xlim([-6,6])
plt.xlabel("target1")
plt.ylabel("target2")
plt.title("multi-output decision tree regression")
plt.legend()
plt.show()