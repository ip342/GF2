# GF2 - Software - Team 15

# Table of Contents

[Getting Started](https://github.com/ethantattersall/GF2#getting-started)

[Running the Program](https://github.com/ethantattersall/GF2#running-the-program)

[Language Support](https://github.com/ethantattersall/GF2#language-support)

[User Guide](https://github.com/ethantattersall/GF2#user-guide)

[Unit Test](https://github.com/ethantattersall/GF2#unit-test)

[Installing wxPython and PyOpenGL](https://github.com/ethantattersall/GF2#installing-wxpython-and-opengl)

## Getting Started

To install, first clone the repository by running the following from your terminal:

```
git clone https://github.com/ethantattersall/GF2/
cd GF2/final
```

You will also need to install wxPython and PyOpenGL, which can be done through the instructions found [below](https://github.com/ethantattersall/GF2#installing-wxpython-and-opengl).

## Running the Program

You can then run the program and open up the GUI using:

```
python logsim.py
```
or 
```
python3 logsim.py
```
or
```
pythonw logsim.py
```

### Language Support 

Currently both English and Spanish languages are supported, with both the GUI and error messages translated. The default program language is English. To run in Spanish, on Linux and Windows launch the program using:

```
LANG=es_ES.utf8 python logsim.py
```

If using MacOS, the language must be changed in System Preferences to Spanish. This can be done through the Terminal using:

```
defaults write NSGlobalDomain AppleLanguages "(es-ES)"
```

Then launch the program as usual. 

## User Guide

![here](https://github.com/ethantattersall/GF2/blob/master/final/UserGuide.png)

## Unit Test

Unit tests for this logic simulator can simply be run by typing 

```
pytest
```

into the console.

## Installing wxPython and PyOpenGL

#### Windows

- In your Python terminal, type either **pip install wxpython** or **conda install wxpython**, depending on whether you are using a pip or conda  environment.
- Download an unofficial WIndows binary of PyOpenGL from here. You need to make sure you download the right version, for example **PyOpenGL‑3.1.5‑cp38‑cp38‑win_amd64.whl**  for 64-bit Python 3.8.  If you are not sure which version you need, run python and check the first line of output, which contains version and architecture information.
- Type **pip install PyOpenGL-////.whl** (substitute //// for the version you downloaded). Make sure you first navigate to the folder containing the downloaded .whl file.
- Check you have **pytest** installed if you wish to run unit tests: if not, install using pip or conda.

#### MacOS

- In your Python terminal, type either **pip3 install wxpython** or **conda install wxpython**, depending on whether you are using a pip or conda  environment.
- Next, type  **pip3/conda install PyOpenGL**.
- For Anaconda distributions only, type **conda install python.app**. To allow Anaconda to access graphics, scripts must be run using the command **pythonw filename.py** rather than the usual **python3 filename.py**.
- Check you have **pytest** installed if you wish to run unit tests: if not, install using pip or conda.

#### Linux
- For Ubuntu 18.04, you will find everything you need in the standard Python packages. Anaconda is not required. Specific packages to install include **python3-pycodestyle, python3-pydocstyle, python3-pytest,  python3-opengl, python3-wxgtk4.0 and freeglut3-dev**.



