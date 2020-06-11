from setuptools import setup, find_packages

setup(
    name='moleculer-client',
    version='0.1.1',
    description='Simple Client in python to communicate with MoleculerJs Microservices using NATS',
    author='Caio Filus Felisbino',
    author_email='caio.filus@gmail.com',
    url='https://github.com/CaioFilus',
    license='MIT',
    packages=['moleculer_client'],
    install_requires=[
        'nats-python==0.7.0',
    ],
    include_package_data=True,
    keywords=['python', 'microservices', 'NATs'],
)
