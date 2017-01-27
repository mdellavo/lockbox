from setuptools import setup

setup(
    name='lockbox',
    version='0.1',
    description='Library and cli-tool to manage storage of encrypted secrets',
    url='https://github.com/mdellavo/lockbox',
    author='Marc DellaVolpe',
    author_email='marc.dellavolpe@gmail.com',
    license='MIT',
    packages=['lockbox'],
    install_requires=[
        "pycrypto"
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': ['lockbox=lockbox.__main__:main'],
    },
)
