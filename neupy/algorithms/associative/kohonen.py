import theano
import theano.tensor as T

from .base import BaseAssociative


__all__ = ('Kohonen',)


class Kohonen(BaseAssociative):
    """Kohonen unsupervised associative Neural Network.
    This algorith similar to :network:`Instar`. Like the instar rule, the
    Kohonen rule allows the weights of a neuron to learn an input vector
    and is therefore suitable for recognition applications. One difference
    that this algorithm is not proportional to output. This Kohonen network
    interpretetion update only weights with non-zero output.

    Notes
    -----
    * Network architecture must contains two layers.

    Parameters
    ----------
    {full_params}

    Methods
    -------
    {unsupervised_train_epochs}
    {full_methods}

    Examples
    --------
    >>> import numpy as np
    >>> from neupy import algorithms, layers
    >>>
    >>> np.random.seed(0)
    >>>
    >>> input_data = np.array([
    ...     [0.1961,  0.9806],
    ...     [-0.1961,  0.9806],
    ...     [0.9806,  0.1961],
    ...     [0.9806, -0.1961],
    ...     [-0.5812, -0.8137],
    ...     [-0.8137, -0.5812],
    ... ])
    >>>
    >>> kohonet = algorithms.Kohonen(
    ...     layers.Linear(2) > layers.CompetitiveOutput(3),
    ...     step=0.5,
    ...     verbose=False
    ... )
    >>> kohonet.train(input_data, epochs=100)
    >>> kohonet.predict(input_data)
    array([[ 0.,  1.,  0.],
           [ 0.,  1.,  0.],
           [ 1.,  0.,  0.],
           [ 1.,  0.,  0.],
           [ 0.,  0.,  1.],
           [ 0.,  0.,  1.]])
    """
    #
    # def update_indexes(self, layer_output):
    #     _, index_y = nonzero(layer_output)
    #     return index_y
    #
    # def train_epoch(self, input_train, target_train):
    #     input_train = format_data(input_train)
    #
    #     weight = self.input_layer.weight
    #     predict = self.predict
    #     update_indexes = self.update_indexes
    #
    #     for input_row in input_train:
    #         input_row = reshape(input_row, (1, input_row.size))
    #         layer_output = predict(input_row)
    #
    #         index_y = update_indexes(layer_output)
    #         self.input_layer.weight[:, index_y] += self.step * (
    #             input_row.T - weight[:, index_y]
    #         )

    def init_methods(self):
        super(Kohonen, self).init_methods()
        prediction = self.variables.prediction_func

        self.methods.train_epoch = theano.function(
            inputs=[self.variables.network_input],
            outputs=prediction.sum(),
            updates=self.init_train_updates(),
        )

    def update_rule(self, layer_output):
        return layer_output.sum(axis=1).nonzero()

    def train_epoch(self, input_train, target_train):
        for input_row in input_train:
            self.methods.train_epoch(input_train)

    def init_layer_updates(self, layer):
        predicted = self.variables.prediction_func
        network_input = self.variables.network_input
        step = self.variables.step

        update_rule = self.update_rule(predicted)

        weight_delta = T.switch(
            self.update_rule(predicted),
            network_input - layer.weight[:, update_rule],
            0
        )

        return [
            (layer.weight, layer.weight + step * weight_delta),
        ]
