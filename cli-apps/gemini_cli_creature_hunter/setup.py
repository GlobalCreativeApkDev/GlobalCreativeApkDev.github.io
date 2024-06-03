from setuptools import setup


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()
        return long_description


setup(
    name='gemini_cli_creature_hunter',
    version='1',
    packages=['gemini_cli_creature_hunter'],
    url='https://github.com/GlobalCreativeApkDev/GlobalCreativeApkDev.github.io/tree/main/cli-apps/gemini_cli_creature_hunter',
    license='MIT',
    author='GlobalCreativeApkDev',
    author_email='globalcreativeapkdev2022@gmail.com',
    description='This package contains implementation of a Pokemon-like game on command-line interface '
                'with Google Gemini AI integrated into it.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    entry_points={
        "console_scripts": [
            "gemini_cli_creature_hunter=gemini_cli_creature_hunter.gemini_cli_creature_hunter:main",
        ]
    }
)