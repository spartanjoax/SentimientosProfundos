import numpy as np
import tensorflow as tf

class TextCNNRNN(object):
    def __init__(self, 
                 hidden_unit,
                 max_pool_size,
                 sequence_length,
                 num_classes,
                 vocab_size,
                 embedding_size,
                 filter_sizes,
                 num_filters,
                 l2_reg_lambda=0.0,
                 pre_trained=False):

        self.input_x = tf.placeholder(tf.int32, [None, sequence_length], name='input_x')
        self.input_y = tf.placeholder(tf.float32, [None, num_classes], name='input_y')
        self.dropout_keep_prob = tf.placeholder(tf.float32, name='dropout_keep_prob')
        self.batch_size = tf.placeholder(tf.int32, [])
        self.real_len = tf.placeholder(tf.int32, [None], name='real_len')

        l2_loss = tf.constant(0.0)

        # Embedding layer
        with tf.device('/cpu:0'), tf.name_scope("embedding"):
            if pre_trained:
                W_ = tf.Variable(
                        tf.constant(0.0, shape=[vocab_size, embedding_size]),
                        trainable=False,
                        name='W')
                self.embedding_placeholder = tf.placeholder(
                        tf.float32, [vocab_size, embedding_size],
                        name='pre_trained')
                W = tf.assign(W_, self.embedding_placeholder)
            else:
                W = tf.Variable(
                        tf.random_uniform([vocab_size, embedding_size], -1.0, 1.0),
                        name="W")

            self.embedded_chars = tf.nn.embedding_lookup(W, self.input_x)
            emb = tf.expand_dims(self.embedded_chars, -1)

        pooled_concat = []
        reduced = np.int32(np.ceil((sequence_length) * 1.0 / max_pool_size))

        # Create a convolution + maxpool layer for each filter size
        pooled_outputs = []
        for i, filter_size in enumerate(filter_sizes):
            with tf.name_scope("conv-maxpool-%s" % filter_size):
                # Convolution Layer
                filter_shape = [filter_size, embedding_size, 1, num_filters]
                W = tf.Variable(
                    tf.truncated_normal(filter_shape, stddev=0.1), name="W")
                b = tf.Variable(
                    tf.constant(0.1, shape=[num_filters]), name="b")
                conv = tf.nn.conv2d(
                    emb,
                    W,
                    strides=[1, 1, 1, 1],
                    padding="VALID",
                    name="conv")
                # Apply nonlinearity
                h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
                # Maxpooling over the outputs
                pooled = tf.nn.max_pool(
                    h,
                    ksize=[1, sequence_length - filter_size + 1, 1, 1],
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="pool")
                pooled_outputs.append(pooled)

        # Combine all the pooled features
        num_filters_total = num_filters * len(list(filter_sizes))
        self.h_pool = tf.concat(pooled_outputs, 3)
        self.h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])
        pooled_concat = tf.nn.dropout(self.h_pool_flat, self.dropout_keep_prob)

        # lstm_cell = tf.nn.rnn_cell.LSTMCell(num_units=hidden_unit)

        #lstm_cell = tf.nn.rnn_cell.GRUCell(num_units=hidden_unit)
        lstm_cell = tf.contrib.rnn.GRUCell(num_units=hidden_unit)

        #lstm_cell = tf.nn.rnn_cell.DropoutWrapper(lstm_cell, output_keep_prob=self.dropout_keep_prob)
        lstm_cell = tf.contrib.rnn.DropoutWrapper(lstm_cell, output_keep_prob=self.dropout_keep_prob)


        self._initial_state = lstm_cell.zero_state(self.batch_size, tf.float32)
        inputs = [tf.squeeze(input_, [1]) for input_ in tf.split(1, int(reduced), pooled_concat)]
        #inputs = [tf.squeeze(input_, [1]) for input_ in tf.split(pooled_concat,num_or_size_splits=int(reduced),axis=1)]
        #outputs, state = tf.nn.rnn(lstm_cell, inputs, initial_state=self._initial_state, sequence_length=self.real_len)
        outputs, state = tf.contrib.rnn.static_rnn(lstm_cell, inputs, initial_state=self._initial_state, sequence_length=self.real_len)

        # Collect the appropriate last words into variable output (dimension = batch x embedding_size)
        output = outputs[0]
        with tf.variable_scope('Output'):
            tf.get_variable_scope().reuse_variables()
            one = tf.ones([1, hidden_unit], tf.float32)
            for i in range(1,len(outputs)):
                ind = self.real_len < (i+1)
                ind = tf.to_float(ind)
                ind = tf.expand_dims(ind, -1)
                mat = tf.matmul(ind, one)
                output = tf.add(tf.multiply(output, mat),tf.multiply(outputs[i], 1.0 - mat))

        with tf.name_scope('output'):
            self.W = tf.Variable(tf.truncated_normal([hidden_unit, num_classes], stddev=0.1), name='W')
            b = tf.Variable(tf.constant(0.1, shape=[num_classes]), name='b')
            l2_loss += tf.nn.l2_loss(W)
            l2_loss += tf.nn.l2_loss(b)
            self.scores = tf.nn.xw_plus_b(output, self.W, b, name='scores')
            self.predictions = tf.argmax(self.scores, 1, name='predictions')

        with tf.name_scope('loss'):
            losses = tf.nn.softmax_cross_entropy_with_logits_v2(labels = self.input_y, logits = self.scores) #  only named arguments accepted            
            self.loss = tf.reduce_mean(losses) + l2_reg_lambda * l2_loss

        with tf.name_scope('accuracy'):
            correct_predictions = tf.equal(self.predictions, tf.argmax(self.input_y, 1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_predictions, "float"), name='accuracy')

        with tf.name_scope('num_correct'):
            correct = tf.equal(self.predictions, tf.argmax(self.input_y, 1))
            self.num_correct = tf.reduce_sum(tf.cast(correct, 'float'))