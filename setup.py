from setuptools import setup


def get_version():
    with open('version.txt', 'r') as fh:
        return fh.read().strip()


setup(
    name='arn-info',
    version=get_version(),
    description="Get info based on an ARN",
    author='Ben Bridts',
    author_email='ben@cloudar.be',
    url='',  # todo
    packages=['src'],
    package_data={'src': ['data/*']},
    entry_points={
        'console_scripts': [
            'arn-info = src.cli:main',
        ]
    },
    install_requires=[
        'arn',
    ],
)
