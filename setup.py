# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='joke_bot',  # Required
    version='0.0.1',  # Required
    description='Joke bot',  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    python_requires='>=3.5, <4',  # Required
    install_requires=['python-telegram-bot', 'pymongo', 'bson', 'numpy'],  # Optional
    entry_points={  # Optional
        'console_scripts': [
            'app=app:main',
        ],
    }
)
