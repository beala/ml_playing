import tensorflow as tf
import sys

from ProgressBar import ProgressBar

IMAGE_HEIGHT_PIXELS = 300
IMAGE_WIDTH_PIXELS = 200
TOTAL_PIXELS = 300 * 200 * 3
TOTAL_CLASSES = 18


def deserialize_example(example_bytes):
    parsed = tf.parse_single_example(
        example_bytes,
        features={
            'image': tf.FixedLenFeature([], dtype=tf.string),
            'one_hot': tf.FixedLenFeature([], dtype=tf.string),
            'label': tf.FixedLenFeature([], dtype=tf.string),
            'image_path': tf.FixedLenFeature([], dtype=tf.string),
        },
        name='parse_example'
    )

    parsed_img_tensor = tf.parse_tensor(parsed['image'], tf.float32, name='parse_image')
    parsed_one_hot_tensor = tf.parse_tensor(parsed['one_hot'], tf.float32, name='parse_one_hot')
    parsed_label = parsed['label']
    parsed_path = parsed['image_path']

    return tf.reshape(parsed_img_tensor, (TOTAL_PIXELS,)), tf.reshape(parsed_one_hot_tensor, (TOTAL_CLASSES,)), parsed_label, parsed_path 
from shutil import import copyfile

def put_in_predicted_location(location, from_file):
    copyfile(f,     

if __name__ == "__main__":
    dataset = tf.data.TFRecordDataset(sys.argv[1])

    data_iter = dataset\
        .map(deserialize_example, num_parallel_calls=8)\
        .repeat()\
        .shuffle(1000)\
        .batch(10)\
        .make_one_shot_iterator()  # type: tf.data.Iterator

    inputs_op, true_values_op, label_op, path = data_iter.get_next()

    # Create the model
    x = tf.placeholder(tf.float32, [None, TOTAL_PIXELS])
    W = tf.Variable(tf.zeros([TOTAL_PIXELS, TOTAL_CLASSES]))
    b = tf.Variable(tf.zeros([TOTAL_CLASSES]))
    # y = ax+b, learn a and b
    y = tf.matmul(x, W) + b
    # Define loss and optimizer
    y_ = tf.placeholder(tf.float32, [None, TOTAL_CLASSES])

    # The raw formulation of cross-entropy,
    #
    #   tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(tf.nn.softmax(y)),
    #                                 reduction_indices=[1]))
    #
    # can be numerically unstable.
    #
    # So here we use tf.nn.softmax_cross_entropy_with_logits on the raw
    # outputs of 'y', and then average across the batch.
    cross_entropy = tf.reduce_mean(
        tf.nn.softmax_cross_entropy_with_logits(labels=y_, logits=y))
    train_step = tf.train.GradientDescentOptimizer(0.01).minimize(cross_entropy)

    sess = tf.InteractiveSession()
    tf.global_variables_initializer().run()

    steps = 1000
    bar = ProgressBar(steps)
    for _ in range(steps):
        inputs, true_values, label = sess.run([inputs_op, true_values_op])
        sess.run(train_step, feed_dict={x: inputs, y_: true_values})
        bar.incr()
        bar.display()

    dataset_test = tf.data.TFRecordDataset(sys.argv[2])

    data_iter_test = dataset_test\
        .map(deserialize_example, num_parallel_calls=8)\
        .make_one_shot_iterator()  # type: tf.data.Iterator

    inputs_op, true_values_op, label_op, path_op = data_iter_test.get_next()

    # Test trained model
    while True:
        try:
            softmax_op = tf.nn.softmax(y, 1)
            predicted_position = tf.argmax(y, 1)
            correct_prediction = tf.equal(predicted_position, tf.argmax(y_, 1))
            accuracy_op = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            inputs, true_values, label, path = sess.run([inputs_op, true_values_op, label_op, path_op])
            accuracy, our_prediction = sess.run([accuracy_op, softmax_op], feed_dict={x: inputs, y_: true_values})
            print("\nTest accuracy: %f" % accuracy)
            print(our_prediction)
        except tf.errors.OutOfRangeError:
            break
