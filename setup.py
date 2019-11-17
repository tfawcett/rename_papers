from setuptools import setup

setup(name='rename_papers',
      version='0.1.0',
      packages=['rename_papers'],
      entry_points={'console_scripts': ['rename_papers = rename_papers.__main__:main']})
