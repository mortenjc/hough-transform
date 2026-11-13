
Files
=====



hough.py
--------

This application loads (x,y) data from csv files, applies the Hough transform
and calculates the line equations. Calls various plotting functions at
the end. Also saves the line equations to file.

rectify.py
----------

This application uses the (saved) line equations to correct the skewed straws. Calls
the relevant plotting function at the end.


plots.py
--------

tiled_accumulator
^^^^^^^^^^^^^^^^^

Multiplot of the accumulator heatmap using the results of the Hough transform **hough.py**.

tiled_lines
^^^^^^^^^^^

Plots the raw (x,y) points and the skewed lines using the results of the Hough transform **hough.py**.


fileops.py
----------

readfiles
^^^^^^^^^

Loads the raw data into a dictionary with keys xx_yy_zz (ring, fen, tube)


save_data
^^^^^^^^^

Saves python data structures to json. Only used to save dictionaries in **hough.py**.


load_data
^^^^^^^^^

Loads python data structures from json.
