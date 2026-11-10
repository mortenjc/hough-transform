

An application of the Hough Transform
=====================================

This repo holds data and code snippets used to demonstrate
how the Hough Transform can be applied to points in 2D 
space to identify lines in the data.

The application comes from the LOKI small angle scattering instrumet
at European Spallation Source, but the problem and solution is 
rather general and can probably be used elsewhere.

So the situation is that we have a set of points (x,y) that cluster around
lines as shown below in the left image. We want to 'straighten' these lines
out so they look like those on the right image.

.. figure:: images/goal.png
  :width: 800
  :align: center

  End goal is to 'rectify' points that cluster around lines

Algorithm History
-----------------

I recently discovered the Hough Transform, first mentioned in 1959, that seems 
to solve the problem in an elegant and effectve way.

The original paper (REF) is not directly applicable and so later developments
have made the idea more tenable. Applied to the field of finding geometric
figures in images, the first 'modern' reference is (https://dl.acm.org/doi/10.1145/361237.361242)
"Use of the Hough transformation to detect lines and curves in pictures".

Interestingly, the Hough Transform is claimed to be a particular application of 
the Radon Transform (https://en.wikipedia.org/wiki/Radon_transform).


Finding Lines
-------------

A line is described by two parameters, (:math:`\rho, \theta`). Where :math:`\rho` is the 
perpendicular (algebraic) distance to the line, and :math:`\theta` is the angle of :math:`\rho`.
In general, the parameters can be restricted to :math:`-R \le \rho \le R` and 
:math:`\theta \in [0 ; \pi[`.

.. figure:: images/rhotheta.png
  :width: 600
  :align: center

  Definition of :math:`\rho` and :math:`\theta`.




