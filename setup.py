from setuptools import setup


setup(name='redwood-cli',
      version='0.1.0',
      description='Redwood Tracker CLI',
      url='http://github.com/kespindler/redwood-cli',
      author='Kurt Spindler',
      author_email='kespindler@gmail.com',
      license='MIT',
      packages=['redwood_cli'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'redwood-cli=redwood_cli:main',
          ],
      },
)
