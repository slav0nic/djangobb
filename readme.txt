This is a fork of DjangoBB forums, modified to plug into Scratch 2.0.

The connection points are as follows:
* Scratchr2 should have a relative symlink to djangobb_forum in its parent directory, which points to ../s2forums/djangobb_forum
* It also needs a relative symlink to djangobb_forum inside its static directory( /scratchr2/static/djangobb_forum ) that points to ../../s2forums/djangobb_forum/static/djangobb_forum
* Settings.py should be modified to import ../s2forums/djangobb_forum/scratchr2_settings.py, so that the necessary settings for ScratchR can be found in this repository. Yeah!
