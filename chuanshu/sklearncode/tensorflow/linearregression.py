# import numpy as np
# x_raw = np.array([2013,2014,2015,2016,2017],dtype=np.float32)
# y_raw = np.array([12000, 14000, 15000, 16500, 17500],dtype=np.float32)
# x = (x_raw-x_raw.min())/(x_raw.max()-x_raw.min())
# y = (y_raw-y_raw.min())/(y_raw.max()-y_raw.min())
# a,b = 0,0
# num_epoch = 10000
# learning_rate = 1e-3
# for e in range(num_epoch):
#     y_pred = a*x+b
#     grad_a, grad_b = (y_pred-y).dot(x), (y_pred-y).sum()
#     a,b = a - learning_rate*grad_a, b - learning_rate*b
# print(a,b)
from types import GeneratorType
from matplotlib.pyplot import cla
import numpy as np
import tensorflow as tf
x_raw = np.array([2013,2014,2015,2016,2017],dtype=np.float32)
y_raw = np.array([12000, 14000, 15000, 16500, 17500],dtype=np.float32)
x = (x_raw-x_raw.min())/(x_raw.max()-x_raw.min())
y = (y_raw-y_raw.min())/(y_raw.max()-y_raw.min())
x = tf.constant(x)
y = tf.constant(y)
a = tf.compat.v1.get_variable('a', dtype=tf.float32, shape=[], initializer=tf.zeros_initializer)
b = tf.compat.v1.get_variable('b', dtype=tf.float32, shape=[], initializer=tf.zeros_initializer)
variables = [a,b]
num_epoch = 10000
optimizer = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=1e-3)
for e in range(num_epoch):
    with tf.GradientTape() as tape:
        y_pred = a*x+b
        loss = 0.5*tf.reduce_sum(tf.square(y_pred-y))
    grads = tape.gradient(loss, variables)
    optimizer.apply_gradients(grads_and_vars=zip(grads, variables))

