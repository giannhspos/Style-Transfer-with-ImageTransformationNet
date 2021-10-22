# -*- coding: utf-8 -*-
"""transformnet.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UKIyugSq6HkPPm7SfUPu4-AEf0M2r6r5
"""

#pip install -q -U tensorflow-addons

import tensorflow as tf
from tensorflow.keras.layers import BatchNormalization, Conv2D, Add, Layer, Conv2DTranspose, Activation

import tensorflow_addons as tfa



class ConvLayer(Layer):
  def __init__(self, filters, 
               kernel=(3,3), padding='same', 
               strides=(1,1), activate=True, name="", 
               weight_initializer="glorot_uniform"
               ):
    super(ConvLayer, self).__init__()
    self.activate = activate
    self.conv = Conv2D(filters, kernel_size=kernel, 
                       padding=padding, strides=strides, 
                       name=name, trainable=True,
                       use_bias=False, 
                       kernel_initializer=weight_initializer)
    self.inst_norm = tfa.layers.InstanceNormalization(axis=3, 
                                          center=True, 
                                          scale=True, 
                                          beta_initializer="zeros", 
                                          gamma_initializer="ones",
                                          trainable=True)
    if self.activate:
      self.relu_layer = Activation('relu', trainable=False)

  def call(self, x):
    x = self.conv(x)
    x = self.inst_norm(x)
    if self.activate:
      x = self.relu_layer(x)
    return x


class ResBlock(Layer):
  def __init__(self, filters, kernel=(3,3), padding='same', weight_initializer="glorot_uniform", prefix=""):
    super(ResBlock, self).__init__()
    self.prefix_name = prefix + "_"
    self.conv1 = ConvLayer(filters=filters, 
                           kernel=kernel, 
                           padding=padding, 
                           weight_initializer=weight_initializer,
                           name=self.prefix_name + "conv_1")
    self.conv2 = ConvLayer(filters=filters, 
                           kernel=kernel, 
                           padding=padding, 
                           activate=False, 
                           weight_initializer=weight_initializer,
                           name=self.prefix_name + "conv_2")
    self.add = Add(name=self.prefix_name + "add")

  def call(self, x):
    tmp = self.conv1(x)
    c = self.conv2(tmp)
    return self.add([x, c])


class ConvTLayer(Layer):
  def __init__(self, filters, kernel=(3,3), padding='same', strides=(1,1), activate=True, name="",
               weight_initializer="glorot_uniform" 
               ):
    super(ConvTLayer, self).__init__()
    self.activate = activate
    self.conv_t = Conv2DTranspose(filters, kernel_size=kernel, padding=padding, 
                                  strides=strides, name=name, 
                                  use_bias=False,
                                  kernel_initializer=weight_initializer)
    self.inst_norm = tfa.layers.InstanceNormalization(axis=3, 
                                          center=True, 
                                          scale=True, 
                                          beta_initializer="zeros", 
                                          gamma_initializer="ones",
                                          trainable=True)
    if self.activate:
      self.relu_layer = Activation('relu')

  def call(self, x):
    x = self.conv_t(x)
    x = self.inst_norm(x)
    if self.activate:
      x = self.relu_layer(x)
    return x



class TransformNet:
  def __init__(self):
    self.conv1 = ConvLayer(32, (9,9), strides=(1,1), padding='same', name="conv_1")
    self.conv2 = ConvLayer(64, (3,3), strides=(2,2), padding='same', name="conv_2")
    self.conv3 = ConvLayer(128, (3,3), strides=(2,2), padding='same', name="conv_3")
    self.res1 = ResBlock(128, prefix="res_1")
    self.res2 = ResBlock(128, prefix="res_2")
    self.res3 = ResBlock(128, prefix="res_3")
    self.res4 = ResBlock(128, prefix="res_4")
    self.res5 = ResBlock(128, prefix="res_5")
    self.convt1 = ConvTLayer(64, (3,3), strides=(2,2), padding='same', name="conv_t_1")
    self.convt2 = ConvTLayer(32, (3,3), strides=(2,2), padding='same', name="conv_t_2")
    self.conv4 = ConvLayer(3, (9,9), strides=(1,1), padding='same', activate=False, name="conv_4")
    self.tanh = Activation('tanh')
    self.model = self.Transformodel()

  def Transformodel(self):
    inputs = tf.keras.Input(shape=(None,None,3))
    x = self.conv1(inputs)
    x = self.conv2(x)
    x = self.conv3(x)
    x = self.res1(x)
    x = self.res2(x)
    x = self.res3(x)
    x = self.res4(x)
    x = self.res5(x)
    x = self.convt1(x)
    x = self.convt2(x)
    x = self.conv4(x)
    x = self.tanh(x)
    x = (x + 1) * (255. / 2)
    return tf.keras.Model(inputs, x, name="transformnet")
