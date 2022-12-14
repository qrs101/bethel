import tensorflow as tf

a = """  feature {
    key: "10129"
    value {
      int64_list {
        value: 5
      }
    }
  }"""
b = """
key: "11416"
"""
# path = u'hdfs://hq9-data-ns/apps/nothive/warehouse/xrec/prerank/pt=2020-11-20/data/v2.7/index_hot/tfrecord/xrec_cvr/part-r
# -00999.gz'
path = u'part-r-00999.gz'
record_iterator = tf.python_io.tf_record_iterator(path=path, options='GZIP')

example = tf.train.Example()

# with tf.gfile.GFile(other_path, 'w') as file:
with open('tfrecord', 'w') as file:
	i = 0
	for string_record in record_iterator:
		example.ParseFromString(string_record)
		res = str(example)
		file.write(res)
		file.write('\n' * 2)
		# print(res)
		i = i + 1
		if i > 5:
			break

