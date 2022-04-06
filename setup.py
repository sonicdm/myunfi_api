from setuptools import setup, find_packages

setup(
    name='myunfi',
    version='0.01a',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='',
    license='MIT',
    author='Allan Barcellos',
    author_email='sonicdm@gmail.com',
    description='Python client for myunfi.com'
)
