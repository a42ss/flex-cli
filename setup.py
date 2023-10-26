import codecs

from setuptools import find_packages, setup

from src.lcli import __version__, EXECUTABLE_NAME

setup(
    # Basic info
    name=EXECUTABLE_NAME,
    version=__version__,
    author='George Babarus',
    author_email='george.babarus@gmail.com',
    description='Local environment CLI tool',
    long_description=codecs.open('README.md', 'rb', 'utf8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/a42ss/flex-cli/',
    license='MIT',

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src', exclude=['tests*']),
    setup_requires=[
        'wheel',
    ],
    install_requires=[
        'fire>=0.4.0',
        'pinject>=0.14.1',
        'prompt_toolkit>=3.0',
        'PyYAML',
        'jsonschema',
        'pyfiglet',
        'blessings',
        'invoke'
    ],
    dependency_links=[
    ],
    extras_require={
        'test': [
            'coverage',
            'pytest',
            'pytest-cov'
        ],
        'dev': [
            'coverage',
            'pytest',
            'pytest-cov'
        ]
    },

    # Scripts
    entry_points={
        'console_scripts': [
            EXECUTABLE_NAME + ' = ' + EXECUTABLE_NAME + '.__main__:main'
        ],
    },
    scripts=[
        # EXECUTABLE_NAME
    ],

    include_package_data=True,
    package_data={
        '': [
            'config/*.yml',
            'config/*.yaml',
            'config/*/*.yml',
            'config/*/*.yaml'
        ],
        # And include any *.msg files found in the 'hello' package, too:
        EXECUTABLE_NAME: ['config/*.yml'],
    },

    # Other configurations
    zip_safe=True,
    platforms='any',
)
