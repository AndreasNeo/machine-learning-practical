# -*- coding: utf-8 -*-
"""Layer definitions.

This module defines classes which encapsulate a single layer.

These layers map input activations to output activation with the `fprop`
method and map gradients with repsect to outputs to gradients with respect to
their inputs with the `bprop` method.

Some layers will have learnable parameters and so will additionally define
methods for getting and setting parameter and calculating gradients with
respect to the layer parameters.
"""

import numpy as np
import mlp.initialisers as init
from mlp import DEFAULT_SEED
from mlp.im2col import im2col_indices, col2im_indices

class Layer(object):
    """Abstract class defining the interface for a layer."""

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        raise NotImplementedError()

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        raise NotImplementedError()


class LayerWithParameters(Layer):
    """Abstract class defining the interface for a layer with parameters."""

    def grads_wrt_params(self, inputs, grads_wrt_outputs):
        """Calculates gradients with respect to layer parameters.

        Args:
            inputs: Array of inputs to layer of shape (batch_size, input_dim).
            grads_wrt_to_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            List of arrays of gradients with respect to the layer parameters
            with parameter gradients appearing in same order in tuple as
            returned from `get_params` method.
        """
        raise NotImplementedError()

    def params_penalty(self):
        """Returns the parameter dependent penalty term for this layer.

        If no parameter-dependent penalty terms are set this returns zero.
        """
        raise NotImplementedError()

    @property
    def params(self):
        """Returns a list of parameters of layer.

        Returns:
            List of current parameter values. This list should be in the
            corresponding order to the `values` argument to `set_params`.
        """
        raise NotImplementedError()

    @params.setter
    def params(self, values):
        """Sets layer parameters from a list of values.

        Args:
            values: List of values to set parameters to. This list should be
                in the corresponding order to what is returned by `get_params`.
        """
        raise NotImplementedError()


class StochasticLayerWithParameters(Layer):
    """Specialised layer which uses a stochastic forward propagation."""

    def __init__(self, rng=None):
        """Constructs a new StochasticLayer object.

        Args:
            rng (RandomState): Seeded random number generator object.
        """
        if rng is None:
            rng = np.random.RandomState(DEFAULT_SEED)
        self.rng = rng

    def fprop(self, inputs, stochastic=True):
        """Forward propagates activations through the layer transformation.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            stochastic: Flag allowing different deterministic
                forward-propagation mode in addition to default stochastic
                forward-propagation e.g. for use at test time. If False
                a deterministic forward-propagation transformation
                corresponding to the expected output of the stochastic
                forward-propagation is applied.

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        raise NotImplementedError()

    def grads_wrt_params(self, inputs, grads_wrt_outputs):
        """Calculates gradients with respect to layer parameters.

        Args:
            inputs: Array of inputs to layer of shape (batch_size, input_dim).
            grads_wrt_to_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            List of arrays of gradients with respect to the layer parameters
            with parameter gradients appearing in same order in tuple as
            returned from `get_params` method.
        """
        raise NotImplementedError()

    def params_penalty(self):
        """Returns the parameter dependent penalty term for this layer.

        If no parameter-dependent penalty terms are set this returns zero.
        """
        raise NotImplementedError()

    @property
    def params(self):
        """Returns a list of parameters of layer.

        Returns:
            List of current parameter values. This list should be in the
            corresponding order to the `values` argument to `set_params`.
        """
        raise NotImplementedError()

    @params.setter
    def params(self, values):
        """Sets layer parameters from a list of values.

        Args:
            values: List of values to set parameters to. This list should be
                in the corresponding order to what is returned by `get_params`.
        """
        raise NotImplementedError()


class StochasticLayer(Layer):
    """Specialised layer which uses a stochastic forward propagation."""

    def __init__(self, rng=None):
        """Constructs a new StochasticLayer object.

        Args:
            rng (RandomState): Seeded random number generator object.
        """
        if rng is None:
            rng = np.random.RandomState(DEFAULT_SEED)
        self.rng = rng

    def fprop(self, inputs, stochastic=True):
        """Forward propagates activations through the layer transformation.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            stochastic: Flag allowing different deterministic
                forward-propagation mode in addition to default stochastic
                forward-propagation e.g. for use at test time. If False
                a deterministic forward-propagation transformation
                corresponding to the expected output of the stochastic
                forward-propagation is applied.

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        raise NotImplementedError()

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs. This should correspond to
        default stochastic forward-propagation.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        raise NotImplementedError()


class AffineLayer(LayerWithParameters):
    """Layer implementing an affine tranformation of its inputs.

    This layer is parameterised by a weight matrix and bias vector.
    """

    def __init__(self, input_dim, output_dim,
                 weights_initialiser=init.UniformInit(-0.1, 0.1),
                 biases_initialiser=init.ConstantInit(0.),
                 weights_penalty=None, biases_penalty=None):
        """Initialises a parameterised affine layer.

        Args:
            input_dim (int): Dimension of inputs to the layer.
            output_dim (int): Dimension of the layer outputs.
            weights_initialiser: Initialiser for the weight parameters.
            biases_initialiser: Initialiser for the bias parameters.
            weights_penalty: Weights-dependent penalty term (regulariser) or
                None if no regularisation is to be applied to the weights.
            biases_penalty: Biases-dependent penalty term (regulariser) or
                None if no regularisation is to be applied to the biases.
        """
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.weights = weights_initialiser((self.output_dim, self.input_dim))
        self.biases = biases_initialiser(self.output_dim)
        self.weights_penalty = weights_penalty
        self.biases_penalty = biases_penalty

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.

        For inputs `x`, outputs `y`, weights `W` and biases `b` the layer
        corresponds to `y = W.dot(x) + b`.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        return self.weights.dot(inputs.T).T + self.biases

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        return grads_wrt_outputs.dot(self.weights)

    def grads_wrt_params(self, inputs, grads_wrt_outputs):
        """Calculates gradients with respect to layer parameters.

        Args:
            inputs: array of inputs to layer of shape (batch_size, input_dim)
            grads_wrt_to_outputs: array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim)

        Returns:
            list of arrays of gradients with respect to the layer parameters
            `[grads_wrt_weights, grads_wrt_biases]`.
        """

        grads_wrt_weights = np.dot(grads_wrt_outputs.T, inputs)
        grads_wrt_biases = np.sum(grads_wrt_outputs, axis=0)

        if self.weights_penalty is not None:
            grads_wrt_weights += self.weights_penalty.grad(parameter=self.weights)

        if self.biases_penalty is not None:
            grads_wrt_biases += self.biases_penalty.grad(parameter=self.biases)

        return [grads_wrt_weights, grads_wrt_biases]

    def params_penalty(self):
        """Returns the parameter dependent penalty term for this layer.

        If no parameter-dependent penalty terms are set this returns zero.
        """
        params_penalty = 0
        if self.weights_penalty is not None:
            params_penalty += self.weights_penalty(self.weights)
        if self.biases_penalty is not None:
            params_penalty += self.biases_penalty(self.biases)
        return params_penalty

    @property
    def params(self):
        """A list of layer parameter values: `[weights, biases]`."""
        return [self.weights, self.biases]

    @params.setter
    def params(self, values):
        self.weights = values[0]
        self.biases = values[1]

    def __repr__(self):
        return 'AffineLayer(input_dim={0}, output_dim={1})'.format(
            self.input_dim, self.output_dim)


class SigmoidLayer(Layer):
    """Layer implementing an element-wise logistic sigmoid transformation."""

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.

        For inputs `x` and outputs `y` this corresponds to
        `y = 1 / (1 + exp(-x))`.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        return 1. / (1. + np.exp(-inputs))

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        return grads_wrt_outputs * outputs * (1. - outputs)

    def __repr__(self):
        return 'SigmoidLayer'

class ConvolutionalLayer(LayerWithParameters):
    """Layer implementing a 2D convolution-based transformation of its inputs.
    The layer is parameterised by a set of 2D convolutional kernels, a four
    dimensional array of shape
        (num_output_channels, num_input_channels, kernel_height, kernel_dim_2)
    and a bias vector, a one dimensional array of shape
        (num_output_channels,)
    i.e. one shared bias per output channel.
    Assuming no-padding is applied to the inputs so that outputs are only
    calculated for positions where the kernel filters fully overlap with the
    inputs, and that unit strides are used the outputs will have spatial extent
        output_height = input_height - kernel_height + 1
        output_width = input_width - kernel_width + 1
    """

    def __init__(self, num_input_channels, num_output_channels,
                 input_height, input_width,
                 kernel_height, kernel_width,
                 kernels_init=init.UniformInit(-0.01, 0.01),
                 biases_init=init.ConstantInit(0.),
                 kernels_penalty=None, biases_penalty=None):
        """Initialises a parameterised convolutional layer.
        Args:
            num_input_channels (int): Number of channels in inputs to
                layer (this may be number of colour channels in the input
                images if used as the first layer in a model, or the
                number of output channels, a.k.a. feature maps, from a
                a previous convolutional layer).
            num_output_channels (int): Number of channels in outputs
                from the layer, a.k.a. number of feature maps.
            input_height (int): Size of first input dimension of each 2D
                channel of inputs.
            input_width (int): Size of second input dimension of each 2D
                channel of inputs.
            kernel_height (int): Size of first dimension of each 2D channel of
                kernels.
            kernel_width (int): Size of second dimension of each 2D channel of
                kernels.
            kernels_intialiser: Initialiser for the kernel parameters.
            biases_initialiser: Initialiser for the bias parameters.
            kernels_penalty: Kernel-dependent penalty term (regulariser) or
                None if no regularisation is to be applied to the kernels.
            biases_penalty: Biases-dependent penalty term (regulariser) or
                None if no regularisation is to be applied to the biases.
        """
        self.num_input_channels = num_input_channels
        self.num_output_channels = num_output_channels
        self.input_height = input_height
        self.input_width = input_width
        self.kernel_height = kernel_height
        self.kernel_width = kernel_width
        self.kernels_init = kernels_init
        self.biases_init = biases_init
        self.kernels_shape = (
            num_output_channels, num_input_channels, kernel_height, kernel_width
        )
        self.inputs_shape = (
            None, num_input_channels, input_height, input_width
        )
        self.kernels = self.kernels_init(self.kernels_shape)
        self.biases = self.biases_init(num_output_channels)
        self.kernels_penalty = kernels_penalty
        self.biases_penalty = biases_penalty

        self.cache = None

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.
        For inputs `x`, outputs `y`, kernels `K` and biases `b` the layer
        corresponds to `y = conv2d(x, K) + b`.
        Args:
            inputs: Array of layer inputs of shape (batch_size, num_input_channels, image_height, image_width).
        Returns:
            outputs: Array of layer outputs of shape (batch_size, num_output_channels, output_height, output_width).
        """
        #self.num_output_channels #2
        #self.num_input_channels #3
        #inputs.shape #(2, 3, 4, 4)
        #self.input_height #4
        #self.input_width #4
        #self.kernel_height #2
        #self.kernel_width #2 
        #self.kernels_shape #(2, 3, 2, 2)
        #self.biases #[0 1]

  
        # im2col stretched out input regions into columns. input_col: (12, 18)
        input_col = im2col_indices(inputs,self.kernel_height,self.kernel_width,padding=0,stride=1)
        # The weights are streched into rows. reshape kernel from (2, 3, 2, 2) to (2,12)
        weights_col = self.kernels.reshape(self.num_output_channels,self.kernels_shape[1]*self.kernels_shape[2]*self.kernels_shape[3])
        # Transpose the dot product of weights_col and input_col to add bias. Output (18,2)
        out =  np.dot(weights_col,input_col).T + self.biases
        # Transpose output back to get  (2,18)
        out = out.T       
        # Calculate output height and width
        output_height = self.input_height - self.kernel_height + 1 #3
        output_width = self.input_width - self.kernel_width + 1 #3
        # Reshape to get (2, 3, 3, 2)
        out = out.reshape(self.num_output_channels,output_height,output_width,inputs.shape[0])
        # Transpose to get (2, 2, 3, 3) (batch_size, num_output_channels, output_height, output_width)
        out = out.transpose(3, 0, 1, 2)

        return out

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.
        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.
        Args:
            inputs: Array of layer inputs of shape
                (batch_size, num_input_channels, input_height, input_width).
            outputs: Array of layer outputs calculated in forward pass of
                shape
                (batch_size, num_output_channels, output_height, output_width).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape
                (batch_size, num_output_channels, output_height, output_width).
        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, num_input_channels, input_height, input_width).
        """
        #inputs.shape (2, 3, 4, 4)
        #outputs.shape (2, 2, 3, 3)
        #grads_wrt_outputs.shape (2, 2, 3, 3)

        # Reshape to (2,18)
        grads_wrt_outputs_r = grads_wrt_outputs.transpose(1, 2, 3, 0).reshape(self.num_output_channels,-1)
        # Reshape kernels to (2,12)
        kernel_r = self.kernels.reshape(self.num_output_channels,self.kernels_shape[1]*self.kernels_shape[2]*self.kernels_shape[3])
        # Gradients wrt inputs col
        grads_wrt_input_col = np.dot(kernel_r.T,grads_wrt_outputs_r) 
        # Undo strech to reshape to (2, 3, 4, 4)
        grads_wrt_input = col2im_indices(grads_wrt_input_col,inputs.shape,self.kernel_height,self.kernel_width,padding=0,stride=1) 
        return grads_wrt_input

    def grads_wrt_params(self, inputs, grads_wrt_outputs):
        """Calculates gradients with respect to layer parameters.
        Args:
            inputs: array of inputs to layer of shape (batch_size, input_dim)
            grads_wrt_to_outputs: array of gradients with respect to the layer
                outputs of shape
                (batch_size, num_output_channels, output_height, output_width).
        Returns:
            list of arrays of gradients with respect to the layer parameters
            `[grads_wrt_kernels, grads_wrt_biases]`.
        """
        #grads_wrt_outputs.shape (2, 2, 3, 3)

        # im2col stretched out input regions into columns. input_col: (12, 18)
        input_col = im2col_indices(inputs,self.kernel_height,self.kernel_width,padding=0,stride=1)
        
        # Calculate bias gradients
        bias_grads = np.sum(grads_wrt_outputs,axis=(0,2,3))

        # Reshape grads_wrt_outputs to (2,18)
        grads_wrt_outputs_r = grads_wrt_outputs.transpose(1, 2, 3, 0).reshape(self.num_output_channels,-1)
        # Gradients wrt inputs params
        kernel_grads = np.dot(grads_wrt_outputs_r,input_col.T)
        kernel_grads = kernel_grads.reshape(self.kernels_shape)

        return kernel_grads, bias_grads
    def params_penalty(self):
        """Returns the parameter dependent penalty term for this layer.
        If no parameter-dependent penalty terms are set this returns zero.
        """
        params_penalty = 0
        if self.kernels_penalty is not None:
            params_penalty += self.kernels_penalty(self.kernels)
        if self.biases_penalty is not None:
            params_penalty += self.biases_penalty(self.biases)
        return params_penalty

    @property
    def params(self):
        """A list of layer parameter values: `[kernels, biases]`."""
        return [self.kernels, self.biases]

    @params.setter
    def params(self, values):
        self.kernels = values[0]
        self.biases = values[1]

    def __repr__(self):
        return (
            'ConvolutionalLayer(\n'
            '    num_input_channels={0}, num_output_channels={1},\n'
            '    input_height={2}, input_width={3},\n'
            '    kernel_height={4}, kernel_width={5}\n'
            ')'
                .format(self.num_input_channels, self.num_output_channels,
                        self.input_height, self.input_width, self.kernel_height,
                        self.kernel_width)
        )

class MaxPooling2DLayer(Layer):
    """
    A class implementing a MaxPooling2D layer.
    """
    def __init__(self, input_height, input_width, size, stride):
        """
        Initializes a max pooling 2D layer
        :param input_height: The image height of the input images
        :param input_width: The image width of the input images
        :param size: The size of the max pooling kernel, indicated as an int
        :param stride: The stride of the max pooling layer, i.e. how many pixels we move the max pooling filter (in the
         relevant axis) at each step during the scanning process
        """
        self.input_height = input_height
        self.input_width = input_width
        self.size = size
        self.stride = stride
        self.cache = None

    def fprop(self, inputs):
        """
        Given an input of shape (b, c, input_height, input_width), apply the max pooling function without padding.
        :param inputs: Inputs of size (b, c, input_height, input_width)
        :return: The output of the max pooling operation. Assuming a stride=2 the output should have a shape of
        (b, c, (input_height - size)/stride + 1, (input_width - size)/stride + 1)
        """
        # size = 2
        # stride = 2
        # inputs.shape (2, 3, 8, 8)
        # output.shape (2, 3, 4, 4)

        inputs_r = inputs.reshape(inputs.shape[0]*inputs.shape[1],1,inputs.shape[2],inputs.shape[3])
        inputs_col = im2col_indices(inputs_r,self.size,self.size,padding=0,stride=self.stride)
        argmax_index =np.argmax(inputs_col,axis=0)
        max_pool = inputs_col[argmax_index,range(argmax_index.size)]
        output_height = int((self.input_height - self.size)/self.stride + 1) #
        output_width = int((self.input_width - self.size)/self.stride + 1) #
        max_pool = max_pool.reshape(output_height,output_width,int(inputs.shape[0]),int(inputs.shape[1]))
        max_pool = max_pool.transpose(2,3,0,1)
        return max_pool

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """
        Given the inputs, outputs and grads_wrt_outputs of the max pooling layer, compute the grads_wrt_inputs
        :param inputs:  Inputs of size (b, c, input_height, input_width)
        :param outputs: The output of the max pooling layer fprop function. Assuming a stride=2 the output should have a shape of
        (b, c, (input_height - size)/stride + 1, (input_width - size)/stride + 1)
        :param grads_wrt_outputs: The grads wrt to the outputs, of shape equal to that of the outputs.
        :return: grads_wrt_input, of shape equal to the inputs.
        """
        inputs_r = inputs.reshape(inputs.shape[0]*inputs.shape[1],1,inputs.shape[2],inputs.shape[3])
        inputs_col = im2col_indices(inputs_r,self.size,self.size,padding=0,stride=self.stride)
        argmax_index =np.argmax(inputs_col,axis=0)

        grads_wrt_outputs_r = grads_wrt_outputs.transpose(2,3,0,1).ravel()
        grads_wrt_input_col = np.zeros_like(inputs_col)
        grads_wrt_input_col[argmax_index,range(argmax_index.size)] = grads_wrt_outputs_r

        shape = (inputs.shape[0]*inputs.shape[1],1,inputs.shape[2],inputs.shape[3])
        grads_wrt_input = col2im_indices(grads_wrt_input_col,shape,self.size,self.size,padding=0,stride=self.stride)
        grads_wrt_input = grads_wrt_input.reshape(inputs.shape[0], inputs.shape[1],inputs.shape[2],inputs.shape[3] )
        return grads_wrt_input


class ReluLayer(Layer):
    """Layer implementing an element-wise rectified linear transformation."""

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.

        For inputs `x` and outputs `y` this corresponds to `y = max(0, x)`.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        return np.maximum(inputs, 0.)

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        return (outputs > 0) * grads_wrt_outputs

    def __repr__(self):
        return 'ReluLayer'


class TanhLayer(Layer):
    """Layer implementing an element-wise hyperbolic tangent transformation."""

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.

        For inputs `x` and outputs `y` this corresponds to `y = tanh(x)`.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        return np.tanh(inputs)

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        return (1. - outputs ** 2) * grads_wrt_outputs

    def __repr__(self):
        return 'TanhLayer'


class SoftmaxLayer(Layer):
    """Layer implementing a softmax transformation."""

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.

        For inputs `x` and outputs `y` this corresponds to

            `y = exp(x) / sum(exp(x))`.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        # subtract max inside exponential to improve numerical stability -
        # when we divide through by sum this term cancels
        exp_inputs = np.exp(inputs - inputs.max(-1)[:, None])
        return exp_inputs / exp_inputs.sum(-1)[:, None]

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        return (outputs * (grads_wrt_outputs -
                           (grads_wrt_outputs * outputs).sum(-1)[:, None]))

    def __repr__(self):
        return 'SoftmaxLayer'


class RadialBasisFunctionLayer(Layer):
    """Layer implementing projection to a grid of radial basis functions."""

    def __init__(self, grid_dim, intervals=[[0., 1.]]):
        """Creates a radial basis function layer object.

        Args:
            grid_dim: Integer specifying how many basis function to use in
                grid across input space per dimension (so total number of
                basis functions will be grid_dim**input_dim)
            intervals: List of intervals (two element lists or tuples)
                specifying extents of axis-aligned region in input-space to
                tile basis functions in grid across. For example for a 2D input
                space spanning [0, 1] x [0, 1] use intervals=[[0, 1], [0, 1]].
        """
        num_basis = grid_dim ** len(intervals)
        self.centres = np.array(np.meshgrid(*[
            np.linspace(low, high, grid_dim) for (low, high) in intervals])
                                ).reshape((len(intervals), -1))
        self.scales = np.array([
            [(high - low) * 1. / grid_dim] for (low, high) in intervals])

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        return np.exp(-(inputs[..., None] - self.centres[None, ...]) ** 2 /
                      self.scales ** 2).reshape((inputs.shape[0], -1))

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        num_basis = self.centres.shape[1]
        return -2 * (
                ((inputs[..., None] - self.centres[None, ...]) / self.scales ** 2) *
                grads_wrt_outputs.reshape((inputs.shape[0], -1, num_basis))
        ).sum(-1)

    def __repr__(self):
        return 'RadialBasisFunctionLayer(grid_dim={0})'.format(self.grid_dim)


class DropoutLayer(StochasticLayer):
    """Layer which stochastically drops input dimensions in its output."""

    def __init__(self, rng=None, incl_prob=0.5, share_across_batch=True):
        """Construct a new dropout layer.

        Args:
            rng (RandomState): Seeded random number generator.
            incl_prob: Scalar value in (0, 1] specifying the probability of
                each input dimension being included in the output.
            share_across_batch: Whether to use same dropout mask across
                all inputs in a batch or use per input masks.
        """
        super(DropoutLayer, self).__init__(rng)
        assert incl_prob > 0. and incl_prob <= 1.
        self.incl_prob = incl_prob
        self.share_across_batch = share_across_batch
        self.rng = rng

    def fprop(self, inputs, stochastic=True):
        """Forward propagates activations through the layer transformation.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            stochastic: Flag allowing different deterministic
                forward-propagation mode in addition to default stochastic
                forward-propagation e.g. for use at test time. If False
                a deterministic forward-propagation transformation
                corresponding to the expected output of the stochastic
                forward-propagation is applied.

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        if stochastic:
            mask_shape = (1,) + inputs.shape[1:] if self.share_across_batch else inputs.shape
            self._mask = (self.rng.uniform(size=mask_shape) < self.incl_prob)
            return inputs * self._mask
        else:
            return inputs * self.incl_prob

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs. This should correspond to
        default stochastic forward-propagation.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        return grads_wrt_outputs * self._mask

    def __repr__(self):
        return 'DropoutLayer(incl_prob={0:.1f})'.format(self.incl_prob)


class ReshapeLayer(Layer):
    """Layer which reshapes dimensions of inputs."""

    def __init__(self, output_shape=None):
        """Create a new reshape layer object.

        Args:
            output_shape: Tuple specifying shape each input in batch should
                be reshaped to in outputs. This **excludes** the batch size
                so the shape of the final output array will be
                    (batch_size, ) + output_shape
                Similarly to numpy.reshape, one shape dimension can be -1. In
                this case, the value is inferred from the size of the input
                array and remaining dimensions. The shape specified must be
                compatible with the input array shape - i.e. the total number
                of values in the array cannot be changed. If set to `None` the
                output shape will be set to
                    (batch_size, -1)
                which will flatten all the inputs to vectors.
        """
        self.output_shape = (-1,) if output_shape is None else output_shape

    def fprop(self, inputs):
        """Forward propagates activations through the layer transformation.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).

        Returns:
            outputs: Array of layer outputs of shape (batch_size, output_dim).
        """
        return inputs.reshape((inputs.shape[0],) + self.output_shape)

    def bprop(self, inputs, outputs, grads_wrt_outputs):
        """Back propagates gradients through a layer.

        Given gradients with respect to the outputs of the layer calculates the
        gradients with respect to the layer inputs.

        Args:
            inputs: Array of layer inputs of shape (batch_size, input_dim).
            outputs: Array of layer outputs calculated in forward pass of
                shape (batch_size, output_dim).
            grads_wrt_outputs: Array of gradients with respect to the layer
                outputs of shape (batch_size, output_dim).

        Returns:
            Array of gradients with respect to the layer inputs of shape
            (batch_size, input_dim).
        """
        return grads_wrt_outputs.reshape(inputs.shape)

    def __repr__(self):
        return 'ReshapeLayer(output_shape={0})'.format(self.output_shape)
