import tensorflow as tf
from tensorflow.contrib import layers

features = {
	'1' : tf.constant([[1,2,3], [2,3,4]], dtype=tf.int64),
	'2' : tf.constant([[1,2,3], [2,3,7]], dtype=tf.int64)
}

x1 = layers.sparse_column_with_integerized_feature('1', 10)
fc1 = layers.embedding_column(x1, 4)
x2 = layers.sparse_column_with_integerized_feature('2', 10)
fc2 = layers.embedding_column(x2, 4)
x3 = layers.sparse_column_with_integerized_feature('3', 10)
fc3 = layers.embedding_column(x3, 4)

fc = layers.shared_embedding_columns([x1, x2], 4)



#tensor1 = layers.input_from_feature_columns(features, [fc[1]])
#tensor2 = layers.sequence_input_from_feature_columns(features, [fc[1]])

#tensor11 = layers.input_from_feature_columns(features, [fc[0]])
#tensor22 = layers.sequence_input_from_feature_columns(features, [fc[0]])

t1 = layers.input_from_feature_columns(features, [fc1, fc3])
t2 = layers.input_from_feature_columns(features, [fc1])

with tf.train.MonitoredTrainingSession() as sess:
	r = sess.run([t1, t2])
	print(r[0])
	print()
	print(r[1])
	print()
