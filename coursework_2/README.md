# Machine-Learning-Practical
My solution for coursework 2 of the [Machine Learning Practical](http://www.drps.ed.ac.uk/18-19/dpt/cxinfr11132.htm) course at University of Edinburgh [School of Informatics](http://www.inf.ed.ac.uk).

The base code for the assignment can be found at https://github.com/CSTR-Edinburgh/mlpractical/tree/mlp2018-9/coursework_2 .

# Classification of Handwritten Digits using Neural Networks 
* Implemented the gradients, forward and back propagation methods of a convolutional network.
* Implemented the max pooling layer.
* Explored the context in convolutional networks achieved with Pooling layers, Striding and Dilation.

* The implementation of the convolutional layer is in [mlp/layers.py](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_2/mlp/layers.py)
 in ConvolutionalLayer class. To test the correctness of the fprop, bprop and grads_wrt_params methods [notebooks/ConvolutionalLayer_tests.ipynb](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_2/notebooks/ConvolutionalLayer_tests.ipynb) was provided.
 
 * The implementation of max pooling layer is in [mlp/layers.py](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_2/mlp/layers.py) 
 in MaxPooling2DLayer class. The tests are in [notebooks/MaxPoolingLayer_tests.ipynb](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_2/notebooks/MaxPoolingLayer_tests.ipynb).
 
 * ~~The findings of this coursework are outlined in the [report](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_2/report/coursework2.pdf).~~

The repository is shared after granted permission from the course organizers.
