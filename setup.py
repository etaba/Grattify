from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
  name = 'grattify',
  packages = ['grattify'], # this must be the same as the name above
  version = '0.2post',
  description = 'Script to download music',
  author = 'Eric Taba',
  author_email = 'eptaba@gmail.com',
  url = 'https://github.com/etaba/grattify', # use the URL to the github repo
  download_url = 'https://github.com/etaba/grattify/tarball/0.1', # I'll explain this in a second
  keywords = ['music', 'spotify', 'pandora', 'download', 'song'], # arbitrary keywords
  classifiers = [],
  install_requires=[
        'bs4',
        'requests',
        'youtube_dl',
        'spotipy',
        'urllib'
  ],
  scripts=['bin/grattify.py'],
  include_package_data=True
)

