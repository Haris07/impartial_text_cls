from setuptools import setup, find_packages

import impatial_text_cls

long_description = '''
Impartial Text Classifier
=========================
Text classifier, based on the BERT and a Bayesian neural network, which
can train on small labeled texts and doubt its decision.

The goal of this project is developing of simple and power text classifier
based on transfer learning and bayesian neural networks.

A transfer learning (particulary, well-known BERT model) helps to generate
special contextual embeddings for text tokens, which provide a better
discrimination ability in feature space, than classical word embeddings.
Therefore we can use smaller labeled data for training of final classifier.

Bayesian neural network in final classifier models uncertainty in data,
owing to this fact probabilities of recognized classes returned by this
network are more fair, and bayesian neural network is more robust to
overfitting.
'''

setup(
    name='impartial-text-cls',
    version=impatial_text_cls.__version__,
    packages=find_packages(exclude=['tests', 'demo']),
    include_package_data=True,
    description='Text classifier, based on the BERT and a Bayesian neural network, which can train on small labeled '
                'texts and doubt its decision',
    long_description=long_description,
    url='https://github.com/bond005/impartial_text_cls',
    author='Ivan Bondarenko',
    author_email='bond005@yandex.ru',
    license='Apache License Version 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords=['bert', 'bayesian', 'intent', 'text', 'nlp', 'tensorflow', 'scikit-learn'],
    install_requires=['bert-tensorflow==1.0.1', 'nltk==3.4.4', 'numpy==1.16.4', 'scikit-learn==0.21.2',
                      'scikit-optimize==0.5.2', 'tensorflow-gpu==1.14.0', 'tensorflow-hub==0.5.0',
                      'tensorflow-probability==0.7.0'],
    test_suite='tests'
)
