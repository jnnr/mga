Modeling-to-generate alternatives with oemof
============================================

This repo hosts an implementation of a modeling-to-generate-alternatives
(MGA) algorithm with some examples within the modeling framework oemof.

The algorithm is similar to the one described in [Neumann2021]_.

Generic functions implementing the main steps of the algorithm (setting an upper
bound on the cost, replacing the objective function of the model) are to be found
in ``mga.py``.

Have a look at `invest_optimize_all_technologies.py` for an example application.

Results
-------

Todo

References
----------

.. [Neumann2021] Neumann, Fabian, and Tom Brown. “The Near-Optimal Feasible Space of a Renewable Power System Model. ”Electric Power Systems Research 190 (January 2021): 106690. https://doi.org/10.1016/j.epsr.2020.106690.

