# Copyright 2019 Ivan Bondarenko
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from argparse import ArgumentParser
import os
import pickle
import random
import sys
import time
from typing import List, Union

import nltk
from nltk.corpus import brown, reuters
from nltk.tokenize.treebank import TreebankWordDetokenizer
from sklearn.metrics import classification_report


try:
    from impartial_text_cls.impartial_text_cls import ImpartialTextClassifier
    from impartial_text_cls.utils import read_snips2017_data, parse_hidden_layers_description
except:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from impartial_text_cls.impartial_text_cls import ImpartialTextClassifier
    from impartial_text_cls.utils import read_snips2017_data, parse_hidden_layers_description


def load_brown_corpus() -> List[str]:
    nltk.download('brown')
    sentences = list(filter(
        lambda sent: (len(sent) <= 30) and (len(sent) >= 3) and any(map(lambda word: word.isalpha(), sent)),
        brown.sents()
    ))
    mdetok = TreebankWordDetokenizer()
    return list(map(
        lambda sent: mdetok.detokenize(
            (' '.join(sent).replace('``', '"').replace("''", '"').replace('`', "'")).split()
        ),
        sentences
    ))


def load_reuters_corpus() -> List[str]:
    nltk.download('reuters')
    sentences = list(filter(
        lambda sent: (len(sent) <= 30) and (len(sent) >= 3) and any(map(lambda word: word.isalpha(), sent)) and
                     len(list(filter(lambda word2: word2.isupper(), sent))) < (len(sent) // 4),
        reuters.sents()
    ))
    mdetok = TreebankWordDetokenizer()
    return list(map(
        lambda sent: mdetok.detokenize(
            (' '.join(sent).replace('``', '"').replace("''", '"').replace('`', "'")).split()
        ),
        sentences
    ))


def generate_random_samples(texts: List[str], labels: List[str]):
    texts_by_classes = dict()
    for cur_text, cur_label in zip(texts, labels):
        if cur_label in texts_by_classes:
            texts_by_classes[cur_label].add(cur_text)
        else:
            texts_by_classes[cur_label] = {cur_text}
    for cur_label in texts_by_classes.keys():
        texts_by_classes[cur_label] = sorted(random.sample(list(texts_by_classes[cur_label]), k=2))
    print('Random examples from train set:')
    for cur_label in sorted(list(texts_by_classes.keys())):
        print('  Class `{0}`:'.format(cur_label))
        for cur_text in texts_by_classes[cur_label]:
            print('    {0}'.format(cur_text))


def is_string(value: Union[str, int]) -> bool:
    return hasattr(value, 'split') and hasattr(value, 'strip')


def main():
    random_seed = 42
    parser = ArgumentParser()
    parser.add_argument('-m', '--model', dest='model_name', type=str, required=True,
                        help='The binary file with the text classifier.')
    parser.add_argument('-d', '--data_dir', dest='data_dir', type=str, required=True,
                        help='Path to the directory with SNIPS-2017 data (see `2017-06-custom-intent-engines` subfolder'
                             ' of the repository https://github.com/snipsco/nlu-benchmark).')
    parser.add_argument('--conv1', dest='size_of_conv1', type=int, required=False, default=200,
                        help='Size of the Bayesian convolution layer with kernel size 1.')
    parser.add_argument('--conv2', dest='size_of_conv2', type=int, required=False, default=200,
                        help='Size of the Bayesian convolution layer with kernel size 2.')
    parser.add_argument('--conv3', dest='size_of_conv3', type=int, required=False, default=200,
                        help='Size of the Bayesian convolution layer with kernel size 3.')
    parser.add_argument('--conv4', dest='size_of_conv4', type=int, required=False, default=200,
                        help='Size of the Bayesian convolution layer with kernel size 4.')
    parser.add_argument('--conv5', dest='size_of_conv5', type=int, required=False, default=200,
                        help='Size of the Bayesian convolution layer with kernel size 5.')
    parser.add_argument('--hidden', dest='hidden_layer_size', type=str, required=False, default='500',
                        help='Size of each hidden layer and total number of hidden layers (separate them with colons).')
    parser.add_argument('--num_monte_carlo', dest='num_monte_carlo', type=int, required=False, default=100,
                        help='Number of generated Monte Carlo samples for each data sample.')
    parser.add_argument('--batch_size', dest='batch_size', type=int, required=False, default=64,
                        help='Size of mini-batch.')
    parser.add_argument('--gpu_frac', dest='gpu_memory_frac', type=float, required=False, default=0.9,
                        help='Allocable part of the GPU memory for the classifier.')
    parser.add_argument('--nn_type', dest='nn_type', type=str, choices=['bayesian', 'usual', 'additional_class'],
                        required=False, default='bayesian',
                        help='Neural network type: `bayesian`, `usual` or `additional_class` (it is same as `usual` '
                             'but unlabeled samples are modeled as additional class).')
    args = parser.parse_args()

    model_name = os.path.normpath(args.model_name)
    data_dir = os.path.normpath(args.data_dir)
    hidden_layer_size, n_hidden_layers = parse_hidden_layers_description(args.hidden_layer_size)

    train_data, val_data, test_data = read_snips2017_data(data_dir)
    print('Classes list: {0}'.format(sorted(list(set(train_data[1])))))
    print('Number of samples for training is {0}.'.format(len(train_data[0])))
    print('Number of samples for validation is {0}.'.format(len(val_data[0])))
    print('Number of samples for final testing is {0}.'.format(len(test_data[0])))
    generate_random_samples(train_data[0], train_data[1])
    print('')
    unlabeled_texts_for_training = load_reuters_corpus()
    unlabeled_texts_for_testing = load_brown_corpus()
    random.seed(random_seed)
    print('Number of unlabeled (unknown) samples for training is {0}. For example:'.format(
        len(unlabeled_texts_for_training)))
    for it in random.sample(unlabeled_texts_for_training, 5):
        print('  {0}'.format(it))
    print('Number of unlabeled (unknown) samples for final testing is {0}. For example:'.format(
        len(unlabeled_texts_for_testing)))
    for it in random.sample(unlabeled_texts_for_testing, 5):
        print('  {0}'.format(it))
    print('')

    if os.path.isfile(model_name):
        with open(model_name, 'rb') as fp:
            nn = pickle.load(fp)
    else:
        if args.nn_type == 'additional_class':
            random.shuffle(unlabeled_texts_for_training)
            n = int(round(0.15 * len(unlabeled_texts_for_training)))
            train_texts = train_data[0] + unlabeled_texts_for_training[n:]
            train_labels = train_data[1] + ['UNKNOWN' for _ in range(len(unlabeled_texts_for_training) - n)]
            val_texts = val_data[0] + unlabeled_texts_for_training[:n]
            val_labels = val_data[1] + ['UNKNOWN' for _ in range(n)]
        else:
            train_texts = train_data[0] + unlabeled_texts_for_training
            train_labels = train_data[1] + [-1 for _ in range(len(unlabeled_texts_for_training))]
            val_texts = val_data[0]
            val_labels = val_data[1]
        nn = ImpartialTextClassifier(filters_for_conv1=args.size_of_conv1, filters_for_conv2=args.size_of_conv2,
                                    filters_for_conv3=args.size_of_conv3, filters_for_conv4=args.size_of_conv4,
                                    filters_for_conv5=args.size_of_conv5, batch_size=args.batch_size,
                                    hidden_layer_size=hidden_layer_size, n_hidden_layers=n_hidden_layers,
                                    num_monte_carlo=args.num_monte_carlo, gpu_memory_frac=args.gpu_memory_frac,
                                    verbose=True, multioutput=False, random_seed=random_seed, validation_fraction=0.15,
                                    max_epochs=50, patience=5, bayesian=(args.nn_type == 'bayesian'),
                                    kl_weight_init=1.0, kl_weight_fin=0.001)
        nn.fit(train_texts, train_labels, validation_data=(val_texts, val_labels))
        print('')
        with open(model_name, 'wb') as fp:
            pickle.dump(nn, fp)
    test_texts = test_data[0] + unlabeled_texts_for_testing
    test_labels = test_data[1] + ['UNKNOWN' for _ in range(len(unlabeled_texts_for_testing))]
    start_time = time.time()
    if args.nn_type == 'additional_class':
        y_pred = [nn.classes_reverse_index_[class_idx] for class_idx in nn.predict_proba(test_texts).argmax(axis=1)]
    else:
        y_pred_ = nn.predict(test_texts)
        y_pred = []
        for sample_idx in range(len(y_pred_)):
            if is_string(y_pred_[sample_idx]):
                y_pred.append(y_pred_[sample_idx])
            else:
                if y_pred_[sample_idx] < 0:
                    y_pred.append('UNKNOWN')
                else:
                    y_pred.append(y_pred_[sample_idx])
    end_time = time.time()
    print('Duration of testing is {0:.3f} seconds.'.format(end_time - start_time))
    print('Mean duration of a single test sample recognition is {0:.3f} seconds.'.format(
        (end_time - start_time) / float(len(test_texts))))
    print('Results of {0}:'.format(
        'bayesian neural network' if args.nn_type == 'bayesian' else
        ('usual neural network' if args.nn_type == 'usual' else 'usual neural network with additional class')
    ))
    print(classification_report(test_labels, y_pred, digits=4))
    if args.nn_type != 'additional_class':
        print('')
        print('Results of {0} without UNKNOWN class:'.format(
            'bayesian neural network' if args.nn_type == 'bayesian' else 'usual neural network'
        ))
        y_pred = [nn.classes_reverse_index_[class_idx] for class_idx in nn.predict_proba(test_data[0]).argmax(axis=1)]
        print(classification_report(test_data[1], y_pred, digits=4))


if __name__ == '__main__':
    main()
