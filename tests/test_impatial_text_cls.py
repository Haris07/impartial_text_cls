import copy
import gc
import os
import pickle
import re
import sys
import tempfile
import unittest

import numpy as np
from sklearn.exceptions import NotFittedError
from sklearn.metrics import f1_score
from bert.tokenization import FullTokenizer

try:
    from impatial_text_cls.impatial_text_cls import ImpatialTextClassifier
except:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from impatial_text_cls.impatial_text_cls import ImpatialTextClassifier


class TestClassifier(unittest.TestCase):
    def tearDown(self):
        if hasattr(self, 'cls'):
            del self.cls
        if hasattr(self, 'another_cls'):
            del self.another_cls
        if hasattr(self, 'temp_file_name'):
            if os.path.isfile(self.temp_file_name):
                os.remove(self.temp_file_name)

    def test_creation(self):
        self.cls = ImpatialTextClassifier()
        self.assertIsInstance(self.cls, ImpatialTextClassifier)
        self.assertTrue(hasattr(self.cls, 'hidden_layer_sizes'))
        self.assertTrue(hasattr(self.cls, 'batch_size'))
        self.assertTrue(hasattr(self.cls, 'bert_hub_module_handle'))
        self.assertTrue(hasattr(self.cls, 'max_epochs'))
        self.assertTrue(hasattr(self.cls, 'patience'))
        self.assertTrue(hasattr(self.cls, 'random_seed'))
        self.assertTrue(hasattr(self.cls, 'gpu_memory_frac'))
        self.assertTrue(hasattr(self.cls, 'validation_fraction'))
        self.assertTrue(hasattr(self.cls, 'verbose'))
        self.assertTrue(hasattr(self.cls, 'num_monte_carlo'))
        self.assertIsInstance(self.cls.hidden_layer_sizes, tuple)
        self.assertIsInstance(self.cls.batch_size, int)
        self.assertIsInstance(self.cls.bert_hub_module_handle, str)
        self.assertIsInstance(self.cls.max_epochs, int)
        self.assertIsInstance(self.cls.patience, int)
        self.assertIsNone(self.cls.random_seed)
        self.assertIsInstance(self.cls.gpu_memory_frac, float)
        self.assertIsInstance(self.cls.validation_fraction, float)
        self.assertIsInstance(self.cls.verbose, bool)
        self.assertIsInstance(self.cls.num_monte_carlo, int)

    def test_check_params_positive(self):
        ImpatialTextClassifier.check_params(
            bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
            hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0, max_epochs=10,
            patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
        )
        self.assertTrue(True)

    def test_check_params_negative001(self):
        true_err_msg = re.escape('`bert_hub_module_handle` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative002(self):
        true_err_msg = re.escape('`bert_hub_module_handle` is wrong! Expected `{0}`, got `{1}`.'.format(
            type('abc'), type(123)))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle=1,
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative003(self):
        true_err_msg = re.escape('`batch_size` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative004(self):
        true_err_msg = re.escape('`batch_size` is wrong! Expected `{0}`, got `{1}`.'.format(
            type(3), type('3')))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size='32', validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative005(self):
        true_err_msg = re.escape('`batch_size` is wrong! Expected a positive integer value, but -3 is not positive.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=-3, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative006(self):
        true_err_msg = re.escape('`max_epochs` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative007(self):
        true_err_msg = re.escape('`max_epochs` is wrong! Expected `{0}`, got `{1}`.'.format(
            type(3), type('3')))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs='10', patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative008(self):
        true_err_msg = re.escape('`max_epochs` is wrong! Expected a positive integer value, but -3 is not positive.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=-3, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative009(self):
        true_err_msg = re.escape('`patience` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative010(self):
        true_err_msg = re.escape('`patience` is wrong! Expected `{0}`, got `{1}`.'.format(
            type(3), type('3')))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience='3', gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative011(self):
        true_err_msg = re.escape('`patience` is wrong! Expected a positive integer value, but -3 is not positive.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=-3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative012(self):
        true_err_msg = re.escape('`num_monte_carlo` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative013(self):
        true_err_msg = re.escape('`num_monte_carlo` is wrong! Expected `{0}`, got `{1}`.'.format(
            type(3), type('3')))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo='100', batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative014(self):
        true_err_msg = re.escape('`num_monte_carlo` is wrong! Expected a positive integer value, but 0 is not '
                                 'positive.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=0, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative015(self):
        true_err_msg = re.escape('`validation_fraction` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative016(self):
        true_err_msg = re.escape('`validation_fraction` is wrong! Expected `{0}`, got `{1}`.'.format(
            type(3.5), type('3')))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction='0.1',
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative017(self):
        true_err_msg = '`validation_fraction` is wrong! Expected a positive floating-point value greater than or ' \
                       'equal to 0.0, but {0} is not positive.'.format(-0.1)
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=-0.1,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative018(self):
        true_err_msg = '`validation_fraction` is wrong! Expected a positive floating-point value less than 1.0, but ' \
                       '{0} is not less than 1.0.'.format(1.1)
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=1.1,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative019(self):
        true_err_msg = re.escape('`gpu_memory_frac` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, verbose=False, random_seed=42
            )

    def test_check_params_negative020(self):
        true_err_msg = re.escape('`gpu_memory_frac` is wrong! Expected `{0}`, got `{1}`.'.format(
            type(3.5), type('3')))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac='1.0', verbose=False, random_seed=42
            )

    def test_check_params_negative021(self):
        true_err_msg = re.escape('`gpu_memory_frac` is wrong! Expected a floating-point value in the (0.0, 1.0], '
                                 'but {0} is not proper.'.format(-1.0))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=-1.0, verbose=False, random_seed=42
            )

    def test_check_params_negative022(self):
        true_err_msg = re.escape('`gpu_memory_frac` is wrong! Expected a floating-point value in the (0.0, 1.0], '
                                 'but {0} is not proper.'.format(1.3))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.3, verbose=False, random_seed=42
            )

    def test_check_params_negative023(self):
        true_err_msg = re.escape('`verbose` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, 50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, gpu_memory_frac=1.0, random_seed=42
            )

    def test_check_params_negative024(self):
        true_err_msg = re.escape('`hidden_layer_sizes` is not specified!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, verbose=False, random_seed=42, gpu_memory_frac=1.0
            )

    def test_check_params_negative025(self):
        true_err_msg = re.escape('`hidden_layer_sizes` is wrong! Expected `{0}`, got `{1}`.'.format(
            type((3, 5)), type('3')))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes='(100, 50)', num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, verbose=False, random_seed=42, gpu_memory_frac=1.0
            )

    def test_check_params_negative026(self):
        true_err_msg = re.escape('`hidden_layer_sizes` is wrong! Expected 1d array, but got 2d one.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=np.array([[100, 50], [200, 130]], dtype=np.int32), num_monte_carlo=100,
                batch_size=32, validation_fraction=0.0, max_epochs=10, patience=3, verbose=False, random_seed=42,
                gpu_memory_frac=1.0
            )

    def test_check_params_negative027(self):
        true_err_msg = re.escape('`hidden_layer_sizes` is wrong! It is empty.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=[], num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, verbose=False, random_seed=42, gpu_memory_frac=1.0
            )

    def test_check_params_negative028(self):
        true_err_msg = re.escape('Item 1 of `hidden_layer_sizes` is wrong! Expected `{0}`, got `{1}`.'.format(
            type(1), type('1')))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, '50'), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, verbose=False, random_seed=42, gpu_memory_frac=1.0
            )

    def test_check_params_negative029(self):
        true_err_msg = re.escape('Item 1 of `hidden_layer_sizes` is wrong! Expected a positive value, got -50.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_params(
                bert_hub_module_handle='https://tfhub.dev/google/bert_multi_cased_L-12_H-768_A-12/1',
                hidden_layer_sizes=(100, -50), num_monte_carlo=100, batch_size=32, validation_fraction=0.0,
                max_epochs=10, patience=3, verbose=False, random_seed=42, gpu_memory_frac=1.0
            )

    def test_check_X_positive(self):
        X = ['abc', 'defgh', '4wdffg']
        ImpatialTextClassifier.check_X(X, 'X_train')
        self.assertTrue(True)

    def test_check_X_negative01(self):
        X = {'abc', 'defgh', '4wdffg'}
        true_err_msg = re.escape('`X_train` is wrong, because it is not a list-like object!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_X(X, 'X_train')

    def test_check_X_negative02(self):
        X = np.random.uniform(-1.0, 1.0, (10, 2))
        true_err_msg = re.escape('`X_train` is wrong, because it is not 1-D list!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_X(X, 'X_train')

    def test_check_X_negative03(self):
        X = ['abc', 23, '4wdffg']
        true_err_msg = re.escape('Item 1 of `X_train` is wrong, because it is not string-like object!')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_X(X, 'X_train')

    def test_check_Xy_positive(self):
        X = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        y = [0, 0, 1, 1, 2, 2, 3, -1, -1, -1]
        true_classes = [0, 1, 2, 3]
        self.assertEqual(true_classes, ImpatialTextClassifier.check_Xy(X, 'X_train', y, 'y_train'))

    def test_check_Xy_negative_01(self):
        true_err_msg = re.escape('`X_train` is wrong, because it is not a list-like object!')
        X = {
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        }
        y = [0, 0, 1, 1, 2, 2, 3, -1, -1, -1]
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_Xy(X, 'X_train', y, 'y_train')

    def test_check_Xy_negative_02(self):
        true_err_msg = re.escape('`y_train` is wrong, because it is not a list-like object!')
        X = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        y = {0, 0, 1, 1, 2, 2, 3, -1, -1, -1}
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_Xy(X, 'X_train', y, 'y_train')

    def test_check_Xy_negative_03(self):
        true_err_msg = re.escape('`y_train` is wrong, because it is not 1-D list!')
        X = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        y = np.array([[0, 0, 1, 1, 2, 2, 3, -1, -1, -1], [0, 0, 1, 1, 2, 2, 3, -1, -1, -1]], dtype=np.int32)
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_Xy(X, 'X_train', y, 'y_train')

    def test_check_Xy_negative_04(self):
        true_err_msg = re.escape('Length of `X_train` does not correspond to length of `y_train`! 10 != 11')
        X = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        y = [0, 0, 1, 1, 2, 2, 3, -1, -1, -1, -1]
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_Xy(X, 'X_train', y, 'y_train')

    def test_check_Xy_negative_05(self):
        true_err_msg = re.escape('Item 8 of `y_train` is wrong, because it is `None`.')
        X = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        y = [0, 0, 1, 1, 2, 2, 3, -1, None, -1]
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_Xy(X, 'X_train', y, 'y_train')

    def test_check_Xy_negative_06(self):
        true_err_msg = re.escape('Item 3 of `y_train` is wrong, because `{0}` is inadmissible type for class '
                                 'label.'.format(type(1.5)))
        X = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        y = [0, 0, 1, 1.5, 2, 2, 3, -1, -1, -1]
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_Xy(X, 'X_train', y, 'y_train')

    def test_check_Xy_negative_07(self):
        true_err_msg = re.escape('`y_train` is wrong! There are too few classes in the `y_train`.')
        X = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        y = [0, 0, 0, 0, 0, 0, 0, -1, -1, -1]
        with self.assertRaisesRegex(ValueError, true_err_msg):
            ImpatialTextClassifier.check_Xy(X, 'X_train', y, 'y_train')

    def test_serialize_positive01(self):
        self.cls = ImpatialTextClassifier(random_seed=31)
        old_hidden_layer_sizes = self.cls.hidden_layer_sizes
        old_num_monte_carlo = self.cls.num_monte_carlo
        old_batch_size = self.cls.batch_size
        old_bert_hub_module_handle = self.cls.bert_hub_module_handle
        old_max_epochs = self.cls.max_epochs
        old_patience = self.cls.patience
        old_random_seed = self.cls.random_seed
        old_gpu_memory_frac = self.cls.gpu_memory_frac
        old_validation_fraction = self.cls.validation_fraction
        old_verbose = self.cls.verbose
        self.temp_file_name = tempfile.NamedTemporaryFile().name
        with open(self.temp_file_name, mode='wb') as fp:
            pickle.dump(self.cls, fp)
        del self.cls
        gc.collect()
        with open(self.temp_file_name, mode='rb') as fp:
            self.cls = pickle.load(fp)
        self.assertIsInstance(self.cls, ImpatialTextClassifier)
        self.assertTrue(hasattr(self.cls, 'batch_size'))
        self.assertTrue(hasattr(self.cls, 'bert_hub_module_handle'))
        self.assertTrue(hasattr(self.cls, 'max_epochs'))
        self.assertTrue(hasattr(self.cls, 'patience'))
        self.assertTrue(hasattr(self.cls, 'random_seed'))
        self.assertTrue(hasattr(self.cls, 'gpu_memory_frac'))
        self.assertTrue(hasattr(self.cls, 'validation_fraction'))
        self.assertTrue(hasattr(self.cls, 'verbose'))
        self.assertTrue(hasattr(self.cls, 'hidden_layer_sizes'))
        self.assertTrue(hasattr(self.cls, 'num_monte_carlo'))
        self.assertEqual(self.cls.batch_size, old_batch_size)
        self.assertEqual(self.cls.num_monte_carlo, old_num_monte_carlo)
        self.assertAlmostEqual(self.cls.hidden_layer_sizes, old_hidden_layer_sizes)
        self.assertEqual(self.cls.bert_hub_module_handle, old_bert_hub_module_handle)
        self.assertEqual(self.cls.max_epochs, old_max_epochs)
        self.assertEqual(self.cls.patience, old_patience)
        self.assertAlmostEqual(self.cls.gpu_memory_frac, old_gpu_memory_frac)
        self.assertAlmostEqual(self.cls.validation_fraction, old_validation_fraction)
        self.assertEqual(self.cls.verbose, old_verbose)
        self.assertEqual(self.cls.random_seed, old_random_seed)

    def test_serialize_positive02(self):
        train_texts = [
            'add Stani, stani Ibar vodo songs in my playlist música libre',
            'add this album to my Blues playlist',
            'Add the tune to the Rage Radio playlist.',
            'Add WC Handy to my Sax and the City playlist',
            'Add BSlade to women of k-pop playlist',
            'Book a reservation for seven people at a bakery in Osage City',
            'Book spot for three at Maid-Rite Sandwich Shop in Antigua and Barbuda',
            'I need a table for breakfast in MI at the pizzeria',
            'Book a restaurant reservation for me and my child for 2 Pm in Faysville',
            'I want to book a highly rated churrascaria ten months from now.',
            'How\'s the weather in Munchique National Natural Park',
            'Tell me the weather forecast for France',
            'Will there be wind in Hornitos DC?',
            'Is it warm here now?',
            'what is the forecast for Roulo for foggy conditions on February the eighteenth, 2018',
            'I\'d like to hear music that\'s popular from Trick-trick on the Slacker service',
            'Play Making Out by Alexander Rosenbaum off Google Music.',
            'I want to hear Pamela Jintana Racine from 1986 on Lastfm',
            'is there something new you can play by Lola Monroe',
            'I want to hear something from Post-punk Revival',
            'Rate All That Remains a five Give this album 4 points',
            'Give The Best Mysteries of Isaac Asimov four stars out of 6.',
            'Rate this current novel 1 out of 6 points.',
            'Give this textbook 5 points',
            'Give this series 0 out of 6 stars',
            'Please help me find the Bloom: Remix Album song.',
            'Find me the soundtrack called Enter the Chicken',
            'Can you please search Ellington at Newport?',
            'Please find me the Youth Against Fascism television show.',
            'Find me the book called Suffer',
            'Find movie times for Landmark Theatres.',
            'What are the movie times for Amco Entertainment',
            'what films are showing at Bow Tie Cinemas',
            'Show me the movies close by',
            'I want to see The Da Vinci Code',
            'Paleo-Indians migrated from Siberia to the North American mainland at least 12,000 years ago.',
            'Hello, world!',
            'Originating in U.S. defense networks, the Internet spread to international academic networks',
            'The WHO is a member of the United Nations Development Group.',
            'In 443, Geneva was taken by Burgundy.',
            'How are you?',
            'Don\'t mention it!',
            'I communicate a lot with advertising and media agencies.',
            'Hey, good morning, peasant!',
            'Neural networks can actually escalate or amplify the intensity of the initial signal.',
            'I was an artist.',
            'He\'s a con artist…among other things.',
            'Application area: growth factors study, cell biology.',
            'Have you taken physical chemistry?',
            'London is the capital of Great Britain'
        ]
        train_labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6,
                        6, 6, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        valid_texts = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        valid_labels = [0, 0, 1, 1, 2, 2, 4, -1, -1, -1]
        self.cls = ImpatialTextClassifier(random_seed=31, batch_size=4)
        old_hidden_layer_sizes = self.cls.hidden_layer_sizes
        old_num_monte_carlo = self.cls.num_monte_carlo
        old_batch_size = self.cls.batch_size
        old_bert_hub_module_handle = self.cls.bert_hub_module_handle
        old_max_epochs = self.cls.max_epochs
        old_patience = self.cls.patience
        old_random_seed = self.cls.random_seed
        old_gpu_memory_frac = self.cls.gpu_memory_frac
        old_validation_fraction = self.cls.validation_fraction
        old_verbose = self.cls.verbose
        self.cls.fit(train_texts, train_labels, validation_data=(valid_texts, valid_labels))
        old_certainty_threshold = self.cls.certainty_threshold_
        old_y = self.cls.predict(valid_texts)
        self.assertIsInstance(old_y, np.ndarray)
        self.assertEqual(len(old_y.shape), 1)
        self.assertEqual(old_y.shape[0], len(valid_labels))
        self.temp_file_name = tempfile.NamedTemporaryFile().name
        with open(self.temp_file_name, mode='wb') as fp:
            pickle.dump(self.cls, fp)
        del self.cls
        gc.collect()
        with open(self.temp_file_name, mode='rb') as fp:
            self.cls = pickle.load(fp)
        self.assertIsInstance(self.cls, ImpatialTextClassifier)
        self.assertTrue(hasattr(self.cls, 'batch_size'))
        self.assertTrue(hasattr(self.cls, 'bert_hub_module_handle'))
        self.assertTrue(hasattr(self.cls, 'max_epochs'))
        self.assertTrue(hasattr(self.cls, 'patience'))
        self.assertTrue(hasattr(self.cls, 'random_seed'))
        self.assertTrue(hasattr(self.cls, 'gpu_memory_frac'))
        self.assertTrue(hasattr(self.cls, 'validation_fraction'))
        self.assertTrue(hasattr(self.cls, 'verbose'))
        self.assertTrue(hasattr(self.cls, 'hidden_layer_sizes'))
        self.assertTrue(hasattr(self.cls, 'num_monte_carlo'))
        self.assertEqual(self.cls.batch_size, old_batch_size)
        self.assertEqual(self.cls.num_monte_carlo, old_num_monte_carlo)
        self.assertAlmostEqual(self.cls.hidden_layer_sizes, old_hidden_layer_sizes)
        self.assertEqual(self.cls.bert_hub_module_handle, old_bert_hub_module_handle)
        self.assertEqual(self.cls.max_epochs, old_max_epochs)
        self.assertEqual(self.cls.patience, old_patience)
        self.assertAlmostEqual(self.cls.gpu_memory_frac, old_gpu_memory_frac)
        self.assertAlmostEqual(self.cls.validation_fraction, old_validation_fraction)
        self.assertEqual(self.cls.verbose, old_verbose)
        self.assertEqual(self.cls.random_seed, old_random_seed)
        self.assertTrue(hasattr(self.cls, 'tokenizer_'))
        self.assertTrue(hasattr(self.cls, 'n_classes_'))
        self.assertTrue(hasattr(self.cls, 'sess_'))
        self.assertTrue(hasattr(self.cls, 'certainty_threshold_'))
        self.assertTrue(hasattr(self.cls, 'logits_'))
        self.assertTrue(hasattr(self.cls, 'labels_distribution_'))
        self.assertTrue(hasattr(self.cls, 'input_ids_'))
        self.assertTrue(hasattr(self.cls, 'input_mask_'))
        self.assertTrue(hasattr(self.cls, 'segment_ids_'))
        self.assertTrue(hasattr(self.cls, 'y_ph_'))
        self.assertIsInstance(self.cls.tokenizer_, FullTokenizer)
        self.assertIsInstance(self.cls.n_classes_, int)
        self.assertIsInstance(self.cls.certainty_threshold_, float)
        self.assertGreaterEqual(self.cls.certainty_threshold_, 0.0)
        self.assertLessEqual(self.cls.certainty_threshold_, 1.0)
        self.assertAlmostEqual(self.cls.certainty_threshold_, old_certainty_threshold, places=6)
        self.assertEqual(self.cls.n_classes_, 7)
        new_y = self.cls.predict(valid_texts)
        self.assertIsInstance(new_y, np.ndarray)
        self.assertEqual(len(new_y.shape), 1)
        self.assertEqual(new_y.shape[0], old_y.shape[0])
        self.assertEqual(old_y.tolist(), new_y.tolist())

    def test_copy_positive01(self):
        self.cls = ImpatialTextClassifier(random_seed=0)
        self.another_cls = copy.copy(self.cls)
        self.assertIsInstance(self.another_cls, ImpatialTextClassifier)
        self.assertIsNot(self.cls, self.another_cls)
        self.assertTrue(hasattr(self.another_cls, 'batch_size'))
        self.assertTrue(hasattr(self.another_cls, 'hidden_layer_sizes'))
        self.assertTrue(hasattr(self.another_cls, 'num_monte_carlo'))
        self.assertTrue(hasattr(self.another_cls, 'bert_hub_module_handle'))
        self.assertTrue(hasattr(self.another_cls, 'max_epochs'))
        self.assertTrue(hasattr(self.another_cls, 'patience'))
        self.assertTrue(hasattr(self.another_cls, 'random_seed'))
        self.assertTrue(hasattr(self.another_cls, 'gpu_memory_frac'))
        self.assertTrue(hasattr(self.another_cls, 'validation_fraction'))
        self.assertTrue(hasattr(self.another_cls, 'verbose'))
        self.assertEqual(self.cls.batch_size, self.another_cls.batch_size)
        self.assertEqual(self.cls.num_monte_carlo, self.another_cls.num_monte_carlo)
        self.assertAlmostEqual(self.cls.hidden_layer_sizes, self.another_cls.hidden_layer_sizes)
        self.assertEqual(self.cls.bert_hub_module_handle, self.another_cls.bert_hub_module_handle)
        self.assertEqual(self.cls.max_epochs, self.another_cls.max_epochs)
        self.assertEqual(self.cls.patience, self.another_cls.patience)
        self.assertEqual(self.cls.random_seed, self.another_cls.random_seed)
        self.assertAlmostEqual(self.cls.gpu_memory_frac, self.another_cls.gpu_memory_frac)
        self.assertAlmostEqual(self.cls.validation_fraction, self.another_cls.validation_fraction)
        self.assertEqual(self.cls.verbose, self.another_cls.verbose)

    def test_copy_positive02(self):
        train_texts = [
            'add Stani, stani Ibar vodo songs in my playlist música libre',
            'add this album to my Blues playlist',
            'Add the tune to the Rage Radio playlist.',
            'Add WC Handy to my Sax and the City playlist',
            'Add BSlade to women of k-pop playlist',
            'Book a reservation for seven people at a bakery in Osage City',
            'Book spot for three at Maid-Rite Sandwich Shop in Antigua and Barbuda',
            'I need a table for breakfast in MI at the pizzeria',
            'Book a restaurant reservation for me and my child for 2 Pm in Faysville',
            'I want to book a highly rated churrascaria ten months from now.',
            'How\'s the weather in Munchique National Natural Park',
            'Tell me the weather forecast for France',
            'Will there be wind in Hornitos DC?',
            'Is it warm here now?',
            'what is the forecast for Roulo for foggy conditions on February the eighteenth, 2018',
            'I\'d like to hear music that\'s popular from Trick-trick on the Slacker service',
            'Play Making Out by Alexander Rosenbaum off Google Music.',
            'I want to hear Pamela Jintana Racine from 1986 on Lastfm',
            'is there something new you can play by Lola Monroe',
            'I want to hear something from Post-punk Revival',
            'Rate All That Remains a five Give this album 4 points',
            'Give The Best Mysteries of Isaac Asimov four stars out of 6.',
            'Rate this current novel 1 out of 6 points.',
            'Give this textbook 5 points',
            'Give this series 0 out of 6 stars',
            'Please help me find the Bloom: Remix Album song.',
            'Find me the soundtrack called Enter the Chicken',
            'Can you please search Ellington at Newport?',
            'Please find me the Youth Against Fascism television show.',
            'Find me the book called Suffer',
            'Find movie times for Landmark Theatres.',
            'What are the movie times for Amco Entertainment',
            'what films are showing at Bow Tie Cinemas',
            'Show me the movies close by',
            'I want to see The Da Vinci Code',
            'Paleo-Indians migrated from Siberia to the North American mainland at least 12,000 years ago.',
            'Hello, world!',
            'Originating in U.S. defense networks, the Internet spread to international academic networks',
            'The WHO is a member of the United Nations Development Group.',
            'In 443, Geneva was taken by Burgundy.',
            'How are you?',
            'Don\'t mention it!',
            'I communicate a lot with advertising and media agencies.',
            'Hey, good morning, peasant!',
            'Neural networks can actually escalate or amplify the intensity of the initial signal.',
            'I was an artist.',
            'He\'s a con artist…among other things.',
            'Application area: growth factors study, cell biology.',
            'Have you taken physical chemistry?',
            'London is the capital of Great Britain'
        ]
        train_labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6,
                        6, 6, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        valid_texts = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        valid_labels = [0, 0, 1, 1, 2, 2, 4, -1, -1, -1]
        self.cls = ImpatialTextClassifier(random_seed=0, batch_size=4)
        self.cls.fit(train_texts, train_labels, validation_data=(valid_texts, valid_labels))
        self.another_cls = copy.copy(self.cls)
        self.assertIsInstance(self.another_cls, ImpatialTextClassifier)
        self.assertIsNot(self.cls, self.another_cls)
        self.assertTrue(hasattr(self.another_cls, 'batch_size'))
        self.assertTrue(hasattr(self.another_cls, 'hidden_layer_sizes'))
        self.assertTrue(hasattr(self.another_cls, 'num_monte_carlo'))
        self.assertTrue(hasattr(self.another_cls, 'bert_hub_module_handle'))
        self.assertTrue(hasattr(self.another_cls, 'max_epochs'))
        self.assertTrue(hasattr(self.another_cls, 'patience'))
        self.assertTrue(hasattr(self.another_cls, 'random_seed'))
        self.assertTrue(hasattr(self.another_cls, 'gpu_memory_frac'))
        self.assertTrue(hasattr(self.another_cls, 'validation_fraction'))
        self.assertTrue(hasattr(self.another_cls, 'verbose'))
        self.assertTrue(hasattr(self.another_cls, 'tokenizer_'))
        self.assertTrue(hasattr(self.another_cls, 'n_classes_'))
        self.assertTrue(hasattr(self.another_cls, 'sess_'))
        self.assertTrue(hasattr(self.another_cls, 'certainty_threshold_'))
        self.assertTrue(hasattr(self.another_cls, 'logits_'))
        self.assertTrue(hasattr(self.another_cls, 'labels_distribution_'))
        self.assertTrue(hasattr(self.another_cls, 'input_ids_'))
        self.assertTrue(hasattr(self.another_cls, 'input_mask_'))
        self.assertTrue(hasattr(self.another_cls, 'segment_ids_'))
        self.assertTrue(hasattr(self.another_cls, 'y_ph_'))
        self.assertEqual(self.cls.batch_size, self.another_cls.batch_size)
        self.assertEqual(self.cls.num_monte_carlo, self.another_cls.num_monte_carlo)
        self.assertAlmostEqual(self.cls.hidden_layer_sizes, self.another_cls.hidden_layer_sizes)
        self.assertEqual(self.cls.bert_hub_module_handle, self.another_cls.bert_hub_module_handle)
        self.assertEqual(self.cls.max_epochs, self.another_cls.max_epochs)
        self.assertEqual(self.cls.patience, self.another_cls.patience)
        self.assertEqual(self.cls.random_seed, self.another_cls.random_seed)
        self.assertAlmostEqual(self.cls.gpu_memory_frac, self.another_cls.gpu_memory_frac)
        self.assertAlmostEqual(self.cls.validation_fraction, self.another_cls.validation_fraction)
        self.assertEqual(self.cls.verbose, self.another_cls.verbose)
        self.assertAlmostEqual(self.cls.certainty_threshold_, self.another_cls.certainty_threshold_, places=9)
        self.assertEqual(self.cls.n_classes_, self.another_cls.n_classes_)
        self.assertEqual(self.cls.predict(valid_texts).tolist(), self.another_cls.predict(valid_texts).tolist())

    def test_fit_predict_positive01(self):
        train_texts = [
            'add Stani, stani Ibar vodo songs in my playlist música libre',
            'add this album to my Blues playlist',
            'Add the tune to the Rage Radio playlist.',
            'Add WC Handy to my Sax and the City playlist',
            'Add BSlade to women of k-pop playlist',
            'Book a reservation for seven people at a bakery in Osage City',
            'Book spot for three at Maid-Rite Sandwich Shop in Antigua and Barbuda',
            'I need a table for breakfast in MI at the pizzeria',
            'Book a restaurant reservation for me and my child for 2 Pm in Faysville',
            'I want to book a highly rated churrascaria ten months from now.',
            'How\'s the weather in Munchique National Natural Park',
            'Tell me the weather forecast for France',
            'Will there be wind in Hornitos DC?',
            'Is it warm here now?',
            'what is the forecast for Roulo for foggy conditions on February the eighteenth, 2018',
            'I\'d like to hear music that\'s popular from Trick-trick on the Slacker service',
            'Play Making Out by Alexander Rosenbaum off Google Music.',
            'I want to hear Pamela Jintana Racine from 1986 on Lastfm',
            'is there something new you can play by Lola Monroe',
            'I want to hear something from Post-punk Revival',
            'Rate All That Remains a five Give this album 4 points',
            'Give The Best Mysteries of Isaac Asimov four stars out of 6.',
            'Rate this current novel 1 out of 6 points.',
            'Give this textbook 5 points',
            'Give this series 0 out of 6 stars',
            'Please help me find the Bloom: Remix Album song.',
            'Find me the soundtrack called Enter the Chicken',
            'Can you please search Ellington at Newport?',
            'Please find me the Youth Against Fascism television show.',
            'Find me the book called Suffer',
            'Find movie times for Landmark Theatres.',
            'What are the movie times for Amco Entertainment',
            'what films are showing at Bow Tie Cinemas',
            'Show me the movies close by',
            'I want to see The Da Vinci Code',
            'Paleo-Indians migrated from Siberia to the North American mainland at least 12,000 years ago.',
            'Hello, world!',
            'Originating in U.S. defense networks, the Internet spread to international academic networks',
            'The WHO is a member of the United Nations Development Group.',
            'In 443, Geneva was taken by Burgundy.',
            'How are you?',
            'Don\'t mention it!',
            'I communicate a lot with advertising and media agencies.',
            'Hey, good morning, peasant!',
            'Neural networks can actually escalate or amplify the intensity of the initial signal.',
            'I was an artist.',
            'He\'s a con artist…among other things.',
            'Application area: growth factors study, cell biology.',
            'Have you taken physical chemistry?',
            'London is the capital of Great Britain'
        ]
        train_labels = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6,
                        6, 6, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        valid_texts = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        valid_labels = [0, 0, 1, 1, 2, 2, 4, -1, -1, -1]
        self.cls = ImpatialTextClassifier(batch_size=4)
        res = self.cls.fit(train_texts, train_labels, validation_data=(valid_texts, valid_labels))
        self.assertIsInstance(res, ImpatialTextClassifier)
        self.assertTrue(hasattr(res, 'hidden_layer_sizes'))
        self.assertTrue(hasattr(res, 'batch_size'))
        self.assertTrue(hasattr(res, 'bert_hub_module_handle'))
        self.assertTrue(hasattr(res, 'max_epochs'))
        self.assertTrue(hasattr(res, 'patience'))
        self.assertTrue(hasattr(res, 'random_seed'))
        self.assertTrue(hasattr(res, 'gpu_memory_frac'))
        self.assertTrue(hasattr(res, 'validation_fraction'))
        self.assertTrue(hasattr(res, 'verbose'))
        self.assertTrue(hasattr(res, 'num_monte_carlo'))
        self.assertIsInstance(res.hidden_layer_sizes, tuple)
        self.assertIsInstance(res.batch_size, int)
        self.assertIsInstance(res.bert_hub_module_handle, str)
        self.assertIsInstance(res.max_epochs, int)
        self.assertIsInstance(res.patience, int)
        self.assertIsNone(res.random_seed)
        self.assertIsInstance(res.gpu_memory_frac, float)
        self.assertIsInstance(res.validation_fraction, float)
        self.assertIsInstance(res.verbose, bool)
        self.assertIsInstance(res.num_monte_carlo, int)
        self.assertTrue(hasattr(res, 'tokenizer_'))
        self.assertTrue(hasattr(res, 'n_classes_'))
        self.assertTrue(hasattr(res, 'sess_'))
        self.assertTrue(hasattr(res, 'certainty_threshold_'))
        self.assertTrue(hasattr(res, 'logits_'))
        self.assertTrue(hasattr(res, 'labels_distribution_'))
        self.assertTrue(hasattr(res, 'input_ids_'))
        self.assertTrue(hasattr(res, 'input_mask_'))
        self.assertTrue(hasattr(res, 'segment_ids_'))
        self.assertTrue(hasattr(res, 'y_ph_'))
        self.assertIsInstance(res.tokenizer_, FullTokenizer)
        self.assertIsInstance(res.n_classes_, int)
        self.assertIsInstance(res.certainty_threshold_, float)
        self.assertGreaterEqual(res.certainty_threshold_, 0.0)
        self.assertLessEqual(res.certainty_threshold_, 1.0)
        self.assertEqual(res.n_classes_, 7)
        y_pred = res.predict(valid_texts)
        self.assertIsInstance(y_pred, np.ndarray)
        self.assertEqual(len(y_pred.shape), 1)
        self.assertEqual(y_pred.shape[0], len(valid_labels))
        f1 = f1_score(y_true=valid_labels, y_pred=y_pred, average='macro')
        self.assertGreater(f1, 0.0)
        self.assertAlmostEqual(f1, res.score(valid_texts, valid_labels), places=5)
        probabilities = res.predict_proba(valid_texts)
        self.assertIsInstance(probabilities, np.ndarray)
        self.assertEqual(len(probabilities.shape), 2)
        self.assertEqual(probabilities.shape[0], len(valid_labels))
        self.assertEqual(probabilities.shape[1], res.n_classes_)
        for sample_idx in range(len(valid_labels)):
            if y_pred[sample_idx] >= 0:
                self.assertEqual(y_pred[sample_idx], probabilities[sample_idx].argmax(),
                                 msg='Sample {0}'.format(sample_idx))
            prob_sum = 0.0
            for class_idx in range(res.n_classes_):
                self.assertGreater(probabilities[sample_idx][class_idx], 0.0,
                                   msg='Sample {0}, class {1}'.format(sample_idx, class_idx))
                self.assertLess(probabilities[sample_idx][class_idx], 1.0,
                                msg='Sample {0}, class {1}'.format(sample_idx, class_idx))
                prob_sum += probabilities[sample_idx][class_idx]
            self.assertAlmostEqual(prob_sum, 1.0, places=3, msg='Sample {0}'.format(sample_idx))
        log_probabilities = res.predict_log_proba(valid_texts)
        self.assertIsInstance(log_probabilities, np.ndarray)
        self.assertEqual(len(log_probabilities.shape), 2)
        self.assertEqual(log_probabilities.shape[0], len(valid_labels))
        self.assertEqual(log_probabilities.shape[1], res.n_classes_)
        for sample_idx in range(len(valid_labels)):
            for class_idx in range(res.n_classes_):
                self.assertAlmostEqual(probabilities[sample_idx][class_idx],
                                       np.exp(log_probabilities[sample_idx][class_idx]),
                                       places=3, msg='Sample {0}, class {1}'.format(sample_idx, class_idx))

    def test_fit_predict_positive02(self):
        train_texts = np.array(
            [
                'add Stani, stani Ibar vodo songs in my playlist música libre',
                'add this album to my Blues playlist',
                'Add the tune to the Rage Radio playlist.',
                'Add WC Handy to my Sax and the City playlist',
                'Add BSlade to women of k-pop playlist',
                'Book a reservation for seven people at a bakery in Osage City',
                'Book spot for three at Maid-Rite Sandwich Shop in Antigua and Barbuda',
                'I need a table for breakfast in MI at the pizzeria',
                'Book a restaurant reservation for me and my child for 2 Pm in Faysville',
                'I want to book a highly rated churrascaria ten months from now.',
                'How\'s the weather in Munchique National Natural Park',
                'Tell me the weather forecast for France',
                'Will there be wind in Hornitos DC?',
                'Is it warm here now?',
                'what is the forecast for Roulo for foggy conditions on February the eighteenth, 2018',
                'I\'d like to hear music that\'s popular from Trick-trick on the Slacker service',
                'Play Making Out by Alexander Rosenbaum off Google Music.',
                'I want to hear Pamela Jintana Racine from 1986 on Lastfm',
                'is there something new you can play by Lola Monroe',
                'I want to hear something from Post-punk Revival',
                'Rate All That Remains a five Give this album 4 points',
                'Give The Best Mysteries of Isaac Asimov four stars out of 6.',
                'Rate this current novel 1 out of 6 points.',
                'Give this textbook 5 points',
                'Give this series 0 out of 6 stars',
                'Please help me find the Bloom: Remix Album song.',
                'Find me the soundtrack called Enter the Chicken',
                'Can you please search Ellington at Newport?',
                'Please find me the Youth Against Fascism television show.',
                'Find me the book called Suffer',
                'Find movie times for Landmark Theatres.',
                'What are the movie times for Amco Entertainment',
                'what films are showing at Bow Tie Cinemas',
                'Show me the movies close by',
                'I want to see The Da Vinci Code',
                'Paleo-Indians migrated from Siberia to the North American mainland at least 12,000 years ago.',
                'Hello, world!',
                'Originating in U.S. defense networks, the Internet spread to international academic networks',
                'The WHO is a member of the United Nations Development Group.',
                'In 443, Geneva was taken by Burgundy.',
                'How are you?',
                'Don\'t mention it!',
                'I communicate a lot with advertising and media agencies.',
                'Hey, good morning, peasant!',
                'Neural networks can actually escalate or amplify the intensity of the initial signal.',
                'I was an artist.',
                'He\'s a con artist…among other things.',
                'Application area: growth factors study, cell biology.',
                'Have you taken physical chemistry?',
                'London is the capital of Great Britain'
            ],
            dtype=np.str
        )
        train_labels = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5,
                                 5, 6, 6, 6, 6, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                dtype=np.int32)
        valid_texts = np.array(
            [
                "I'd like to have this track onto my Classical Relaxations playlist.",
                'Add the album to my Flow Español playlist.',
                'Book a reservation for my babies and I',
                'need a table somewhere in Quarryville 14 hours from now',
                'what is the weather here',
                'What kind of weather is forecast in MS now?',
                'Please play something catchy on Youtube',
                'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
                'The Soviet Union played a decisive role in the Allied victory in World War II.',
                'Most of Northern European Russia and Siberia has a subarctic climate'
            ],
            dtype=np.str
        )
        valid_labels = np.array([0, 0, 1, 1, 2, 2, 4, -1, -1, -1], dtype=np.int32)
        self.cls = ImpatialTextClassifier(validation_fraction=0.2, batch_size=4)
        res = self.cls.fit(train_texts, train_labels)
        self.assertIsInstance(res, ImpatialTextClassifier)
        self.assertTrue(hasattr(res, 'hidden_layer_sizes'))
        self.assertTrue(hasattr(res, 'batch_size'))
        self.assertTrue(hasattr(res, 'bert_hub_module_handle'))
        self.assertTrue(hasattr(res, 'max_epochs'))
        self.assertTrue(hasattr(res, 'patience'))
        self.assertTrue(hasattr(res, 'random_seed'))
        self.assertTrue(hasattr(res, 'gpu_memory_frac'))
        self.assertTrue(hasattr(res, 'validation_fraction'))
        self.assertTrue(hasattr(res, 'verbose'))
        self.assertTrue(hasattr(res, 'num_monte_carlo'))
        self.assertIsInstance(res.hidden_layer_sizes, tuple)
        self.assertIsInstance(res.batch_size, int)
        self.assertIsInstance(res.bert_hub_module_handle, str)
        self.assertIsInstance(res.max_epochs, int)
        self.assertIsInstance(res.patience, int)
        self.assertIsNone(res.random_seed)
        self.assertIsInstance(res.gpu_memory_frac, float)
        self.assertIsInstance(res.validation_fraction, float)
        self.assertIsInstance(res.verbose, bool)
        self.assertIsInstance(res.num_monte_carlo, int)
        self.assertTrue(hasattr(res, 'tokenizer_'))
        self.assertTrue(hasattr(res, 'n_classes_'))
        self.assertTrue(hasattr(res, 'sess_'))
        self.assertTrue(hasattr(res, 'certainty_threshold_'))
        self.assertTrue(hasattr(res, 'logits_'))
        self.assertTrue(hasattr(res, 'labels_distribution_'))
        self.assertTrue(hasattr(res, 'input_ids_'))
        self.assertTrue(hasattr(res, 'input_mask_'))
        self.assertTrue(hasattr(res, 'segment_ids_'))
        self.assertTrue(hasattr(res, 'y_ph_'))
        self.assertIsInstance(res.tokenizer_, FullTokenizer)
        self.assertIsInstance(res.n_classes_, int)
        self.assertIsInstance(res.certainty_threshold_, float)
        self.assertGreaterEqual(res.certainty_threshold_, 0.0)
        self.assertLessEqual(res.certainty_threshold_, 1.0)
        self.assertEqual(res.n_classes_, 7)
        y_pred = res.predict(valid_texts)
        self.assertIsInstance(y_pred, np.ndarray)
        self.assertEqual(len(y_pred.shape), 1)
        self.assertEqual(y_pred.shape[0], len(valid_labels))
        f1 = f1_score(y_true=valid_labels, y_pred=y_pred, average='macro')
        self.assertGreater(f1, 0.0)
        self.assertAlmostEqual(f1, res.score(valid_texts, valid_labels), places=5)
        probabilities = res.predict_proba(valid_texts)
        self.assertIsInstance(probabilities, np.ndarray)
        self.assertEqual(len(probabilities.shape), 2)
        self.assertEqual(probabilities.shape[0], len(valid_labels))
        self.assertEqual(probabilities.shape[1], res.n_classes_)
        for sample_idx in range(len(valid_labels)):
            if y_pred[sample_idx] >= 0:
                self.assertEqual(y_pred[sample_idx], probabilities[sample_idx].argmax(),
                                 msg='Sample {0}'.format(sample_idx))
            prob_sum = 0.0
            for class_idx in range(res.n_classes_):
                self.assertGreater(probabilities[sample_idx][class_idx], 0.0,
                                   msg='Sample {0}, class {1}'.format(sample_idx, class_idx))
                self.assertLess(probabilities[sample_idx][class_idx], 1.0,
                                msg='Sample {0}, class {1}'.format(sample_idx, class_idx))
                prob_sum += probabilities[sample_idx][class_idx]
            self.assertAlmostEqual(prob_sum, 1.0, places=3, msg='Sample {0}'.format(sample_idx))
        log_probabilities = res.predict_log_proba(valid_texts)
        self.assertIsInstance(log_probabilities, np.ndarray)
        self.assertEqual(len(log_probabilities.shape), 2)
        self.assertEqual(log_probabilities.shape[0], len(valid_labels))
        self.assertEqual(log_probabilities.shape[1], res.n_classes_)
        for sample_idx in range(len(valid_labels)):
            for class_idx in range(res.n_classes_):
                self.assertAlmostEqual(probabilities[sample_idx][class_idx],
                                       np.exp(log_probabilities[sample_idx][class_idx]),
                                       places=3, msg='Sample {0}, class {1}'.format(sample_idx, class_idx))

    def test_fit_negative_01(self):
        n_classes = 4
        classes_list = [0, 1, 2, 4]
        true_err_msg = re.escape('`y` is wrong! Labels of classes are not ordered. Expected a `{0}`, but got a '
                                 '`{1}`.'.format(list(range(n_classes)), classes_list))
        X = [
            "I'd like to have this track onto my Classical Relaxations playlist.",
            'Add the album to my Flow Español playlist.',
            'Book a reservation for my babies and I',
            'need a table somewhere in Quarryville 14 hours from now',
            'what is the weather here',
            'What kind of weather is forecast in MS now?',
            'Please play something catchy on Youtube',
            'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
            'The Soviet Union played a decisive role in the Allied victory in World War II.',
            'Most of Northern European Russia and Siberia has a subarctic climate'
        ]
        y = [0, 0, 1, 1, 2, 2, 4, -1, -1, -1]
        self.cls = ImpatialTextClassifier(batch_size=4)
        with self.assertRaisesRegex(ValueError, true_err_msg):
            self.cls.fit(X, y)

    def test_fit_negative02(self):
        train_texts = np.array(
            [
                'add Stani, stani Ibar vodo songs in my playlist música libre',
                'add this album to my Blues playlist',
                'Add the tune to the Rage Radio playlist.',
                'Add WC Handy to my Sax and the City playlist',
                'Add BSlade to women of k-pop playlist',
                'Book a reservation for seven people at a bakery in Osage City',
                'Book spot for three at Maid-Rite Sandwich Shop in Antigua and Barbuda',
                'I need a table for breakfast in MI at the pizzeria',
                'Book a restaurant reservation for me and my child for 2 Pm in Faysville',
                'I want to book a highly rated churrascaria ten months from now.',
                'How\'s the weather in Munchique National Natural Park',
                'Tell me the weather forecast for France',
                'Will there be wind in Hornitos DC?',
                'Is it warm here now?',
                'what is the forecast for Roulo for foggy conditions on February the eighteenth, 2018',
                'I\'d like to hear music that\'s popular from Trick-trick on the Slacker service',
                'Play Making Out by Alexander Rosenbaum off Google Music.',
                'I want to hear Pamela Jintana Racine from 1986 on Lastfm',
                'is there something new you can play by Lola Monroe',
                'I want to hear something from Post-punk Revival',
                'Rate All That Remains a five Give this album 4 points',
                'Give The Best Mysteries of Isaac Asimov four stars out of 6.',
                'Rate this current novel 1 out of 6 points.',
                'Give this textbook 5 points',
                'Give this series 0 out of 6 stars',
                'Please help me find the Bloom: Remix Album song.',
                'Find me the soundtrack called Enter the Chicken',
                'Can you please search Ellington at Newport?',
                'Please find me the Youth Against Fascism television show.',
                'Find me the book called Suffer',
                'Find movie times for Landmark Theatres.',
                'What are the movie times for Amco Entertainment',
                'what films are showing at Bow Tie Cinemas',
                'Show me the movies close by',
                'I want to see The Da Vinci Code',
                'Paleo-Indians migrated from Siberia to the North American mainland at least 12,000 years ago.',
                'Hello, world!',
                'Originating in U.S. defense networks, the Internet spread to international academic networks',
                'The WHO is a member of the United Nations Development Group.',
                'In 443, Geneva was taken by Burgundy.',
                'How are you?',
                'Don\'t mention it!',
                'I communicate a lot with advertising and media agencies.',
                'Hey, good morning, peasant!',
                'Neural networks can actually escalate or amplify the intensity of the initial signal.',
                'I was an artist.',
                'He\'s a con artist…among other things.',
                'Application area: growth factors study, cell biology.',
                'Have you taken physical chemistry?',
                'London is the capital of Great Britain'
            ],
            dtype=np.str
        )
        train_labels = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5,
                                 5, 6, 6, 6, 6, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                dtype=np.int32)
        valid_texts = np.array(
            [
                "I'd like to have this track onto my Classical Relaxations playlist.",
                'Add the album to my Flow Español playlist.',
                'Book a reservation for my babies and I',
                'need a table somewhere in Quarryville 14 hours from now',
                'what is the weather here',
                'What kind of weather is forecast in MS now?',
                'Please play something catchy on Youtube',
                'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
                'The Soviet Union played a decisive role in the Allied victory in World War II.',
                'Most of Northern European Russia and Siberia has a subarctic climate'
            ],
            dtype=np.str
        )
        valid_labels = np.array([0, 0, 1, 1, 2, 2, 4, 7, 7, 7], dtype=np.int32)
        self.cls = ImpatialTextClassifier(validation_fraction=0.2, batch_size=4)
        true_err_msg = re.escape('`y_val` is wrong. Class 7 is unknown.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            self.cls.fit(train_texts, train_labels, validation_data=(valid_texts, valid_labels))

    def test_fit_negative03(self):
        train_texts = np.array(
            [
                'add Stani, stani Ibar vodo songs in my playlist música libre',
                'add this album to my Blues playlist',
                'Add the tune to the Rage Radio playlist.',
                'Add WC Handy to my Sax and the City playlist',
                'Add BSlade to women of k-pop playlist',
                'Book a reservation for seven people at a bakery in Osage City',
                'Book spot for three at Maid-Rite Sandwich Shop in Antigua and Barbuda',
                'I need a table for breakfast in MI at the pizzeria',
                'Book a restaurant reservation for me and my child for 2 Pm in Faysville',
                'I want to book a highly rated churrascaria ten months from now.',
                'How\'s the weather in Munchique National Natural Park',
                'Tell me the weather forecast for France',
                'Will there be wind in Hornitos DC?',
                'Is it warm here now?',
                'what is the forecast for Roulo for foggy conditions on February the eighteenth, 2018',
                'I\'d like to hear music that\'s popular from Trick-trick on the Slacker service',
                'Play Making Out by Alexander Rosenbaum off Google Music.',
                'I want to hear Pamela Jintana Racine from 1986 on Lastfm',
                'is there something new you can play by Lola Monroe',
                'I want to hear something from Post-punk Revival',
                'Rate All That Remains a five Give this album 4 points',
                'Give The Best Mysteries of Isaac Asimov four stars out of 6.',
                'Rate this current novel 1 out of 6 points.',
                'Give this textbook 5 points',
                'Give this series 0 out of 6 stars',
                'Please help me find the Bloom: Remix Album song.',
                'Find me the soundtrack called Enter the Chicken',
                'Can you please search Ellington at Newport?',
                'Please find me the Youth Against Fascism television show.',
                'Find me the book called Suffer',
                'Find movie times for Landmark Theatres.',
                'What are the movie times for Amco Entertainment',
                'what films are showing at Bow Tie Cinemas',
                'Show me the movies close by',
                'I want to see The Da Vinci Code',
                'Paleo-Indians migrated from Siberia to the North American mainland at least 12,000 years ago.',
                'Hello, world!',
                'Originating in U.S. defense networks, the Internet spread to international academic networks',
                'The WHO is a member of the United Nations Development Group.',
                'In 443, Geneva was taken by Burgundy.',
                'How are you?',
                'Don\'t mention it!',
                'I communicate a lot with advertising and media agencies.',
                'Hey, good morning, peasant!',
                'Neural networks can actually escalate or amplify the intensity of the initial signal.',
                'I was an artist.',
                'He\'s a con artist…among other things.',
                'Application area: growth factors study, cell biology.',
                'Have you taken physical chemistry?',
                'London is the capital of Great Britain'
            ],
            dtype=np.str
        )
        train_labels = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5,
                                 5, 6, 6, 6, 6, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                dtype=np.int32)
        valid_texts = np.array(
            [
                "I'd like to have this track onto my Classical Relaxations playlist.",
                'Add the album to my Flow Español playlist.',
                'Book a reservation for my babies and I',
                'need a table somewhere in Quarryville 14 hours from now',
                'what is the weather here',
                'What kind of weather is forecast in MS now?',
                'Please play something catchy on Youtube',
                'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
                'The Soviet Union played a decisive role in the Allied victory in World War II.',
                'Most of Northern European Russia and Siberia has a subarctic climate'
            ],
            dtype=np.str
        )
        valid_labels = np.array([0, 0, 1, 1, 2, 2, 8, 7, 7, 7], dtype=np.int32)
        self.cls = ImpatialTextClassifier(validation_fraction=0.2, batch_size=4)
        true_err_msg = re.escape('`y_val` is wrong. Classes {0} are unknown.'.format([7, 8]))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            self.cls.fit(train_texts, train_labels, validation_data=(valid_texts, valid_labels))

    def test_score_negative01(self):
        train_texts = np.array(
            [
                'add Stani, stani Ibar vodo songs in my playlist música libre',
                'add this album to my Blues playlist',
                'Add the tune to the Rage Radio playlist.',
                'Add WC Handy to my Sax and the City playlist',
                'Add BSlade to women of k-pop playlist',
                'Book a reservation for seven people at a bakery in Osage City',
                'Book spot for three at Maid-Rite Sandwich Shop in Antigua and Barbuda',
                'I need a table for breakfast in MI at the pizzeria',
                'Book a restaurant reservation for me and my child for 2 Pm in Faysville',
                'I want to book a highly rated churrascaria ten months from now.',
                'How\'s the weather in Munchique National Natural Park',
                'Tell me the weather forecast for France',
                'Will there be wind in Hornitos DC?',
                'Is it warm here now?',
                'what is the forecast for Roulo for foggy conditions on February the eighteenth, 2018',
                'I\'d like to hear music that\'s popular from Trick-trick on the Slacker service',
                'Play Making Out by Alexander Rosenbaum off Google Music.',
                'I want to hear Pamela Jintana Racine from 1986 on Lastfm',
                'is there something new you can play by Lola Monroe',
                'I want to hear something from Post-punk Revival',
                'Rate All That Remains a five Give this album 4 points',
                'Give The Best Mysteries of Isaac Asimov four stars out of 6.',
                'Rate this current novel 1 out of 6 points.',
                'Give this textbook 5 points',
                'Give this series 0 out of 6 stars',
                'Please help me find the Bloom: Remix Album song.',
                'Find me the soundtrack called Enter the Chicken',
                'Can you please search Ellington at Newport?',
                'Please find me the Youth Against Fascism television show.',
                'Find me the book called Suffer',
                'Find movie times for Landmark Theatres.',
                'What are the movie times for Amco Entertainment',
                'what films are showing at Bow Tie Cinemas',
                'Show me the movies close by',
                'I want to see The Da Vinci Code',
                'Paleo-Indians migrated from Siberia to the North American mainland at least 12,000 years ago.',
                'Hello, world!',
                'Originating in U.S. defense networks, the Internet spread to international academic networks',
                'The WHO is a member of the United Nations Development Group.',
                'In 443, Geneva was taken by Burgundy.',
                'How are you?',
                'Don\'t mention it!',
                'I communicate a lot with advertising and media agencies.',
                'Hey, good morning, peasant!',
                'Neural networks can actually escalate or amplify the intensity of the initial signal.',
                'I was an artist.',
                'He\'s a con artist…among other things.',
                'Application area: growth factors study, cell biology.',
                'Have you taken physical chemistry?',
                'London is the capital of Great Britain'
            ],
            dtype=np.str
        )
        train_labels = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5,
                                 5, 6, 6, 6, 6, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                dtype=np.int32)
        valid_texts = np.array(
            [
                "I'd like to have this track onto my Classical Relaxations playlist.",
                'Add the album to my Flow Español playlist.',
                'Book a reservation for my babies and I',
                'need a table somewhere in Quarryville 14 hours from now',
                'what is the weather here',
                'What kind of weather is forecast in MS now?',
                'Please play something catchy on Youtube',
                'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
                'The Soviet Union played a decisive role in the Allied victory in World War II.',
                'Most of Northern European Russia and Siberia has a subarctic climate'
            ],
            dtype=np.str
        )
        valid_labels = np.array([0, 0, 1, 1, 2, 2, 4, 7, 7, 7], dtype=np.int32)
        self.cls = ImpatialTextClassifier(validation_fraction=0.2, batch_size=4)
        res = self.cls.fit(train_texts, train_labels)
        true_err_msg = re.escape('`y` is wrong. Class 7 is unknown.')
        with self.assertRaisesRegex(ValueError, true_err_msg):
            _ = res.score(valid_texts, valid_labels)

    def test_score_negative02(self):
        train_texts = np.array(
            [
                'add Stani, stani Ibar vodo songs in my playlist música libre',
                'add this album to my Blues playlist',
                'Add the tune to the Rage Radio playlist.',
                'Add WC Handy to my Sax and the City playlist',
                'Add BSlade to women of k-pop playlist',
                'Book a reservation for seven people at a bakery in Osage City',
                'Book spot for three at Maid-Rite Sandwich Shop in Antigua and Barbuda',
                'I need a table for breakfast in MI at the pizzeria',
                'Book a restaurant reservation for me and my child for 2 Pm in Faysville',
                'I want to book a highly rated churrascaria ten months from now.',
                'How\'s the weather in Munchique National Natural Park',
                'Tell me the weather forecast for France',
                'Will there be wind in Hornitos DC?',
                'Is it warm here now?',
                'what is the forecast for Roulo for foggy conditions on February the eighteenth, 2018',
                'I\'d like to hear music that\'s popular from Trick-trick on the Slacker service',
                'Play Making Out by Alexander Rosenbaum off Google Music.',
                'I want to hear Pamela Jintana Racine from 1986 on Lastfm',
                'is there something new you can play by Lola Monroe',
                'I want to hear something from Post-punk Revival',
                'Rate All That Remains a five Give this album 4 points',
                'Give The Best Mysteries of Isaac Asimov four stars out of 6.',
                'Rate this current novel 1 out of 6 points.',
                'Give this textbook 5 points',
                'Give this series 0 out of 6 stars',
                'Please help me find the Bloom: Remix Album song.',
                'Find me the soundtrack called Enter the Chicken',
                'Can you please search Ellington at Newport?',
                'Please find me the Youth Against Fascism television show.',
                'Find me the book called Suffer',
                'Find movie times for Landmark Theatres.',
                'What are the movie times for Amco Entertainment',
                'what films are showing at Bow Tie Cinemas',
                'Show me the movies close by',
                'I want to see The Da Vinci Code',
                'Paleo-Indians migrated from Siberia to the North American mainland at least 12,000 years ago.',
                'Hello, world!',
                'Originating in U.S. defense networks, the Internet spread to international academic networks',
                'The WHO is a member of the United Nations Development Group.',
                'In 443, Geneva was taken by Burgundy.',
                'How are you?',
                'Don\'t mention it!',
                'I communicate a lot with advertising and media agencies.',
                'Hey, good morning, peasant!',
                'Neural networks can actually escalate or amplify the intensity of the initial signal.',
                'I was an artist.',
                'He\'s a con artist…among other things.',
                'Application area: growth factors study, cell biology.',
                'Have you taken physical chemistry?',
                'London is the capital of Great Britain'
            ],
            dtype=np.str
        )
        train_labels = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 5, 5, 5, 5,
                                 5, 6, 6, 6, 6, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
                                dtype=np.int32)
        valid_texts = np.array(
            [
                "I'd like to have this track onto my Classical Relaxations playlist.",
                'Add the album to my Flow Español playlist.',
                'Book a reservation for my babies and I',
                'need a table somewhere in Quarryville 14 hours from now',
                'what is the weather here',
                'What kind of weather is forecast in MS now?',
                'Please play something catchy on Youtube',
                'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
                'The Soviet Union played a decisive role in the Allied victory in World War II.',
                'Most of Northern European Russia and Siberia has a subarctic climate'
            ],
            dtype=np.str
        )
        valid_labels = np.array([0, 0, 1, 1, 2, 2, 8, 7, 7, 7], dtype=np.int32)
        self.cls = ImpatialTextClassifier(validation_fraction=0.2, batch_size=4)
        res = self.cls.fit(train_texts, train_labels)
        true_err_msg = re.escape('`y` is wrong. Classes {0} are unknown.'.format([7, 8]))
        with self.assertRaisesRegex(ValueError, true_err_msg):
            _ = res.score(valid_texts, valid_labels)

    def test_score_negative03(self):
        valid_texts = np.array(
            [
                "I'd like to have this track onto my Classical Relaxations playlist.",
                'Add the album to my Flow Español playlist.',
                'Book a reservation for my babies and I',
                'need a table somewhere in Quarryville 14 hours from now',
                'what is the weather here',
                'What kind of weather is forecast in MS now?',
                'Please play something catchy on Youtube',
                'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
                'The Soviet Union played a decisive role in the Allied victory in World War II.',
                'Most of Northern European Russia and Siberia has a subarctic climate'
            ],
            dtype=np.str
        )
        valid_labels = np.array([0, 0, 1, 1, 2, 2, 4, -1, -1, -1], dtype=np.int32)
        self.cls = ImpatialTextClassifier(validation_fraction=0.2, batch_size=4)
        with self.assertRaises(NotFittedError):
            _ = self.cls.score(valid_texts, valid_labels)

    def test_predict_negative01(self):
        valid_texts = np.array(
            [
                "I'd like to have this track onto my Classical Relaxations playlist.",
                'Add the album to my Flow Español playlist.',
                'Book a reservation for my babies and I',
                'need a table somewhere in Quarryville 14 hours from now',
                'what is the weather here',
                'What kind of weather is forecast in MS now?',
                'Please play something catchy on Youtube',
                'The East Slavs emerged as a recognizable group in Europe between the 3rd and 8th centuries AD.',
                'The Soviet Union played a decisive role in the Allied victory in World War II.',
                'Most of Northern European Russia and Siberia has a subarctic climate'
            ],
            dtype=np.str
        )
        self.cls = ImpatialTextClassifier(validation_fraction=0.2, batch_size=4)
        with self.assertRaises(NotFittedError):
            _ = self.cls.predict(valid_texts)


if __name__ == '__main__':
    unittest.main(verbosity=2)
