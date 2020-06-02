# GF2 - Software - Team 15

## Getting started

To install, first clone the repository by running the following from your terminal:

```
git clone https://github.com/ethantattersall/GF2/
cd GF2/
```

You will also need to install wxPython and PyOpenGL, which can be done through the instructions found [here](https://www.vle.cam.ac.uk/mod/page/view.php?id=12084171).

## Running the program

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

## Using the program

INSERT USER GUIDE 

## Unit test

Unit tests for this logic simulator can simply be run by typing 

```
pytest
```

into the console.


