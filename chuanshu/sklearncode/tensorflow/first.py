from mimetypes import inited
from turtle import shape
import tensorflow as tf
tf.executing_eagerly()

X = tf.constant([[1.,2.], [3.,4.]])
print(X)
y = tf.constant([[1.], [2.]])
print(y)
w = tf.compat.v1.get_variable('w', shape=[2,1], initializer=tf.constant_initializer([[1.],[2.]]))
print(w)
b = tf.compat.v1.get_variable('b', shape=[1], initializer=tf.constant_initializer([1.]))
print(b)
with tf.GradientTape() as tape:
    L = 0.5*tf.reduce_sum(tf.square(tf.matmul(X,w)+b-y))
w_grad, b_grad = tape.gradient(L,[w,b])
print([L.numpy(), w_grad.numpy(), b_grad.numpy()])