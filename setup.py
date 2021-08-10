import os

from setuptools import setup

requires = (
    'coloredlogs>=14.0',
    'dash>=1.19.0',
    'pandas>=1.0.3',
    'parse>=1.19.0',
    'plotly>=4.14.3',
    'pydash>=4.8.0',
    'pyee>=7.0.2',
    'python-i18n>=0.3.9',
    'pyyaml>=5.4',
    'typeguard>=2.12.1',
    'xdg==5.1.1',
)

this_directory = os.path.abspath(os.path.dirname(__file__))


# NOTE: solution from https://packaging.python.org/guides/single-sourcing-package-version/
def get_version(rel_path: str) -> str:
    init_path = os.path.join(this_directory, rel_path)
    with open(init_path, 'r') as f:
        for line in f.read().splitlines():
            if line.startswith('__version__'):
                delim = '"' if '"' in line else "'"

                return line.split(delim)[1]

        raise RuntimeError(f'Unable to find version string in [{init_path}]!')


def get_long_description() -> str:
    readme_path = os.path.join(this_directory, 'README.md')
    with open(readme_path, encoding='utf-8') as f:
        # TODO: read only after "Installation and use" section (do not read before)
        return f.read()


setup(
    name='speaking-eye',
    version=get_version('src/speaking_eye/__init__.py'),
    description="Track & analyze your computer activity. Focus on work and don't forget to take breaks",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/alena-bartosh/speaking-eye',
    python_requires='>=3.6, <4',
    install_requires=requires,
    package_dir={'': 'src'},
    packages=['speaking_eye'],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'speaking-eye = speaking_eye.__main__:main',
        ],
    },
    author='Alena Bartosh',
    author_email='alena.mathematics@gmail.com',
    keywords='worktracker timetracker gtk wnck dash',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
    ],
)
