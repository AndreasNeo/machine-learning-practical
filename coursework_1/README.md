# Exploration of RMSProp and Adam Learning Algorithms 
My assignment solution for coursework 1 of the [Machine Learning Practical](http://www.drps.ed.ac.uk/18-19/dpt/cxinfr11132.htm) course at University of Edinburgh [School of Informatics](http://www.inf.ed.ac.uk).

The base code for the assignment can be found at https://github.com/CSTR-Edinburgh/mlpractical/tree/mlp2018-9/coursework_1.

Implemented and explored:
* RMSProp and Adam.
* Learning rate scheduler for stochastic gradient descent (SGD) and Adam.
* Adam with regularization and weight decay.

In the file [mlp/learning_rules.py](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_1/mlp/learning_rules.py) the following classes were implemented:
* RMSPropLearningRule
* AdamLearningRule
* AdamLearningRuleWithWeightDecay. The test file is [notebooks/WeightDecay_tests.ipynb](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_1/notebooks/WeightDecay_tests.ipynb).


Cosine annealing scheduler was implemented in [mlp/schedulers.py](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_1/mlp/schedulers.py) in CosineAnnealingWithWarmRestarts class. The test file for this class is [notebooks/CosineAnnealingScheduler_tests.ipynb](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_1/notebooks/CosineAnnealingScheduler_tests.ipynb).

The experiments were carried out in the file [notebooks/Coursework_1.ipynb](https://github.com/AndreasNeokleous/Machine-Learning-Practical/blob/master/coursework_1/notebooks/Coursework_1.ipynb).

The repository is shared after granted permission from the course organizers.
