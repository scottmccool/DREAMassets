from setuptools import setup

setup(name='DREAM',
      version='0.0.3',
      python_requires='>=3.5',
      description='Dream bluetooth framework',
      url='https://github.com/DREAMassets-org/DREAMassets/',
      author='DREAM',
      author_email='no-reply@localhost',
      license='MIT',
      packages=['dreamhub','dreamhub.publisher','dreamhub.sniffer'],
      zip_safe=False)
