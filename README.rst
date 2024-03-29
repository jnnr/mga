Modeling-to-generate alternatives with oemof
============================================

This repo hosts an implementation of a modeling-to-generate-alternatives
(MGA) algorithm with some examples within the modeling framework oemof.

The idea of MGA is to investigate alternative solutions
of an optimization model which can be different in other quantities but have nearly the same
total system cost as the global optimum.

A well-known approach is the "hop, skip and jump" algorithm ([Brill1982]_), which
finds alternative solutions in the following way: After finding the global optimum
of a LP, a new constraint is added which sets an upper bound on the total system costs
such that they are smaller than the optimal value plus some tolerance. Then, the
original objective function is dropped and instead, the euclidean distance to the
previous solution is maximized. This is repeated several times to sample alternative
solutions from the near-optimal feasible space.

The algorithm implemented here takes a different approach which is similar to the
one described in [Neumann2021]_.

Generic functions implementing the main steps of the algorithm (setting an upper
bound on the cost, replacing the objective function of the model) are to be found
in ``mga.py``.

How to use
----------

Install the requirements listed in requirements.txt in your environment by calling:

.. code-block::

    pip install -r requirements.txt

Then, run ``python invest_optimize_all_technologies.py`` as an example application.

Results
-------

Todo: Show plot.

References
----------

.. [Brill1982] Brill, E. Downey, Shoou-Yuh Chang, and Lewis D. Hopkins. "Modeling to Generate Alternatives: The HSJ Approach and an Illustration Using a Problem in Land Use Planning." Management Science 28, no. 3 (1982): 221-35. Accessed July 6, 2021. http://www.jstor.org/stable/2630877.
.. [Neumann2021] Neumann, Fabian, and Tom Brown. “The Near-Optimal Feasible Space of a Renewable Power System Model. ”Electric Power Systems Research 190 (January 2021): 106690. https://doi.org/10.1016/j.epsr.2020.106690.

