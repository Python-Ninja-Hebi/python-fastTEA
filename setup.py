from setuptools import setup, find_packages

# read requirements.txt
def parse_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='fasttea-web',
    version='0.3.0',
    description='fastTEA - Python-Web-Framework with fastAPI and htmx',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Hebi',
    author_email='hebi@python-ninja.com',
    url='https://github.com/dein-repo/fasttea',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)