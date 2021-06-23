Diffractometer “Parameters”
===========================

Some of the diffractometer *modes* use additional parameters. The
`E4CV <https://people.debian.org/~picca/hkl/hkl.html#org7ef08ba>`__
geometry, for example, has a ``double_diffraction`` mode which requires
a reference :math:`hkl_2` vector. The vector is set and accessed by a
Python command that calls directly the corresponding *libhkl* function:

+-----------------------------------+-----------------------------------+
| action                            | ``E4CV`` method                   |
+===================================+===================================+
| read names                        | ``e4cv.calc.engine._engine.p      |
|                                   | arameters_names_get(units_code)`` |
+-----------------------------------+-----------------------------------+
| read values                       | ``e4cv.calc.engine._engine.pa     |
|                                   | rameters_values_get(units_code)`` |
+-----------------------------------+-----------------------------------+
| write names                       | Names are pre-defined by *libhkl* |
|                                   | and cannot be changed.            |
+-----------------------------------+-----------------------------------+
| write values                      | ``e4                              |
|                                   | cv.calc.engine._engine.parameters |
|                                   | _values_set(values, units_code)`` |
+-----------------------------------+-----------------------------------+

**Objective**

Show how to use the ``double_diffraction`` mode in the ``E4CV``
geometry.

First, we start by importing the ``gi`` (gobject-introspection) package
which is required to link the *libhkl* library ``('Hkl', 5.0)`` into
Python. Then import the constant, ``A_KEV`` (product of Planck’s
constant and speed of light in a vacuum). The value of this constant is
obtained from the `2019 NIST publication of 2018 CODATA Fundamental
Physical
Constants <https://www.nist.gov/programs-projects/codata-values-fundamental-physical-constants>`__.

.. code:: ipython3

    import gi
    gi.require_version('Hkl', '5.0')
    from hkl import A_KEV

``E4CV``, ``hkl``, ``double_diffraction``
-----------------------------------------

======== ======================
term     value
======== ======================
geometry ``E4CV``
engine   ``hkl``
mode     ``double_diffraction``
======== ======================

Using the standard ``E4CV`` geometry with simulated motors, we copy the
`E4CV setup for the LNO_LAO
sample <https://blueskyproject.io/hklpy/examples/notebooks/tst_e4cv_fourc.html#read-the-spec-scan-from-the-data-file>`__.
Using a kwarg, we can automatically compute the UB matrix once we define
the second reflection. (This means we do not have to call
``compute_UB()`` on a separate line.)

.. code:: ipython3

    from hkl import SimulatedE4CV
    e4cv = SimulatedE4CV("", name="e4cv")
    
    # order:  a b c  alpha beta gamma
    lattice = (3.781726143, 3.791444574, 3.79890313, 90.2546203, 90.01815424, 89.89967858)
    e4cv.calc.new_sample("LNO_LAO", lattice=lattice)
    
    wavelength = 1.239424258
    e4cv.energy.put(A_KEV / wavelength)
    
    # order:   omega    chi      phi  tth
    p_002 = (19.1335, 90.0135, 0.0, 38.09875)
    r_002 = e4cv.calc.sample.add_reflection(0, 0, 2, p_002)
    
    p_113 = (32.82125, 115.23625, 48.1315, 65.644)
    r_113 = e4cv.calc.sample.add_reflection(1, 1, 3, p_113, compute_ub=True)
    
    # e4cv.calc.sample.compute_UB(r_002, r_113)

Set the ``double_diffraction`` mode.

.. code:: ipython3

    print(f"{e4cv.calc.engine.mode = }")
    e4cv.calc.engine.mode = "double_diffraction"
    print(f"{e4cv.calc.engine.mode = }")


.. parsed-literal::

    e4cv.calc.engine.mode = 'bissector'
    e4cv.calc.engine.mode = 'double_diffraction'


To read and write the :math:`hkl_2` parameters (``h2``, ``k2``, ``l2``),
we must use (at least for now) the low-level *libhkl* interface. Expect
this code to become easier in a future *hklpy* release.

First, there is a shorcut *property* in the ``calc`` module. It
simplifies a more complicated to the lower level support.

.. code:: ipython3

    e4cv.calc.parameters




.. parsed-literal::

    ['h2', 'k2', 'l2']



This is the lower-level call simplified by the above:

.. code:: ipython3

    e4cv.calc.engine._engine.parameters_names_get()




.. parsed-literal::

    ['h2', 'k2', 'l2']



Read the parameters. The supplied argument is either ``0`` or ``1``,
pick ``1`` for user units. (*libhkl*: ``Hkl.UnitEnum.USER`` == 1)
although either might give the same result. This ``units`` feature of
*libhkl* is not used at this time.

.. code:: ipython3

    e4cv.calc.engine._engine.parameters_values_get(1)




.. parsed-literal::

    [1.0, 1.0, 1.0]



Set the parameters. First are the values, then the 0 or 1.

.. code:: ipython3

    # no shortcut to this one.  Yet.
    e4cv.calc.engine._engine.parameters_values_set((2,2,0), 1)




.. parsed-literal::

    1



Calculate (002) with (220) as second diffracting plane
------------------------------------------------------

.. code:: ipython3

    print(f"{e4cv.calc.engine._engine.parameters_values_get(1) = }")
    print("(002) :", e4cv.forward((0, 0, 2)))


.. parsed-literal::

    e4cv.calc.engine._engine.parameters_values_get(1) = [2.0, 2.0, 0.0]
    (002) : PosCalcE4CV(omega=19.125954018919906, chi=89.98529317061228, phi=19.05658549375108, tth=38.08406317115545)


Calculate (002) with (222) as second diffracting plane
------------------------------------------------------

.. code:: ipython3

    e4cv.calc.engine._engine.parameters_values_set((2,2,2), 1)
    print(f"{e4cv.calc.engine._engine.parameters_values_get(1) = }")
    print("(002) :", e4cv.forward((0, 0, 2)))


.. parsed-literal::

    e4cv.calc.engine._engine.parameters_values_get(1) = [2.0, 2.0, 2.0]
    (002) : PosCalcE4CV(omega=19.125992826777846, chi=89.98551636715723, phi=18.904239486428256, tth=38.084063171155435)

