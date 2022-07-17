#!/usr/bin/env/python
#  -*- coding: utf-8 -*-
__author__ = 'dushuai'

"""
shift():
    input:
        shift(X=[1,2,3,4,5,6,7,8,9],shift_win=3)   
    output:
        [1,1,1,1,2,3,4,5,6]

    input:
        shift(X=[1,2,3,4,5,6,7,8,9],shift_win=20)
    output:
        [1,1,1,1,1,1,1,1,1]

simple_feature():
    input:
        [1,2,3,0] >= 2 ? [1,2,3,4] + 10 : -1
    output:
        [-1,12,13,-1]
"""

import numpy as np
import time

def shift(X:list, shift_win):
    if len(X):
        out = []
        for i in range(len(X)):
            if i < (shift_win):
                out.append(X[0])
            else:
                out.append(X[i-3])
    else:
        print("X is None")
    return out

def minus(x1:list,x2:list):
    return list(map(lambda x,y:x-y,x1,x2))

def simple_feature(X:list):
    res = list(map(lambda x,y:x-y,minus(shift(X,30),shift(X,15)),minus(shift(X,30), X)))
    a = minus(shift(X,1),X)
    output = []
    for i in range(len(res)):
        if res[i] < -1e-13:
            output.append(1)
        else:
            output.append(a[i])
    # print(output)
    return output
    
if __name__ == "__main__":
    np.random.seed(1)
    tic = time.time()    
    A = np.random.random(200000).astype(np.float64) * 300 - 160
    toc = time.time()
    print("Data generation time: {} ms.".format((toc -tic)*1e3))
    tic = time.time()
    B = simple_feature(A)
    toc = time.time()
    print("Computing time: {} ms.".format((toc - tic)*1e3))




