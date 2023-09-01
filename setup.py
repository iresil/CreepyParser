from setuptools import setup, find_packages

setup(
    name='creepyParser',
    version='1.0',
    author='Irene Spanou',
    description='Extracts information from CreepyPasta stories',
    long_description='Attempts to retrieve useful information from CreepyPasta stories',
    url='https://github.com/iresil',
    keywords='creepypasta, parser',
    python_requires='>=3.10, <4',
    packages=find_packages(),
    install_requires=[
        'spacy~=3.6.1',
        'mysql~=0.0.3',
        'mysql-connector-python~=8.0.32',
        'gensim~=4.3.1',
        'spacytextblob~=4.0.0',
        'pyenchant~=3.2.2',
        'matplotlib~=3.7.2'
    ],
    package_data={
    },
    entry_points={
        'runners': [
            'creepyParser=creepyParser:main',
        ]
    }
)
