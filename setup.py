from setuptools import setup

# libraries needed at runtime in a production environment
install_requires = [
    'confluent_kafka >= 1.6.0',
    'psycopg2_binary >= 2.8.6',
    'requests >= 2.25.1',
]

# additional dependencies for dev/test/build environment
dev_requires = [
    'flake8 >= 3.8',
    'mypy >= 0.800',
    'pytest >= 6.2',
    'VCRpy >= 4.1',
]

setup(
    name='checksite',
    version='0.0',
    author='Greg Ward',
    author_email='greg@gerg.ca',
    description='web site checker',
    packages=['checksite'],
    install_requires=install_requires,
    extras_require={'dev': dev_requires},
)
