**UB** : Save and Restore Crystal Orientation
=============================================

see: https://github.com/bluesky/hklpy/issues/50

**Objectives**

1. Save the information defining the crystal orientation into the
   descriptor document
2. List runs that have orientation that can be restored
3. Restore crystal orientation from a given Bluesky run

--------------

Data collection
===============

Setup for data collection
-------------------------

Use a local, temporary, file-based databroker. It will reset after each
restart of the notebook. Prepare to define the diffractometers needed
here plus some items from the ophyd simulators.

.. code:: ipython3

    import gi
    gi.require_version('Hkl', '5.0')
    
    from bluesky import RunEngine
    from bluesky.callbacks.best_effort import BestEffortCallback
    import bluesky.plans as bp
    import bluesky.plan_stubs as bps
    import bluesky.preprocessors as bpp
    import databroker
    import hkl
    from hkl import *
    import numpy as np
    import pyRestTable
    from ophyd import Component, Device, EpicsSignal, Signal
    from ophyd.signal import AttributeSignal, ArrayAttributeSignal
    from ophyd.sim import *
    import pandas as pd
    
    bec = BestEffortCallback()
    bec.disable_plots()
    cat = databroker.temp().v2
    
    RE = RunEngine({})
    RE.subscribe(bec)
    RE.subscribe(cat.v1.insert)
    RE.md["notebook"] = "tst_UB_in_descriptor_document"
    RE.md["objective"] = "Demonstrate UB matrix save & restore in descriptor document of bluesky run"

--------------

Build simulated 4-circle diffractometer
---------------------------------------

Build two 4-circles so that we can test routines that differentiate
between similar diffractometers. Use the second one to restore
orientation saved from the first.

.. code:: ipython3

    class Fourc(SimulatedE4CV):
        pass
    
    fourc = Fourc("", name="fourc")
    fourc.energy.put(A_KEV / 1.54)
    a0 = SI_LATTICE_PARAMETER
    fourc.calc.new_sample("silicon", lattice=(a0, a0, a0, 90, 90, 90))
    fourc.calc.sample.compute_UB(
        fourc.calc.sample.add_reflection(4, 0, 0, (-145.451, 0, 0, 69.0966)),
        fourc.calc.sample.add_reflection(0, 4, 0, (-145.451, 0, 90, 69.0966))
    )
    fourc.pa()
    
    orange = Fourc("", name="orange")
    orange.pa()


.. parsed-literal::

    ===================== ===========================================================================
    term                  value                                                                      
    ===================== ===========================================================================
    diffractometer        fourc                                                                      
    geometry              E4CV                                                                       
    class                 Fourc                                                                      
    energy (keV)          8.05092                                                                    
    wavelength (angstrom) 1.54000                                                                    
    calc engine           hkl                                                                        
    mode                  bissector                                                                  
    positions             ===== =======                                                              
                          name  value                                                                
                          ===== =======                                                              
                          omega 0.00000                                                              
                          chi   0.00000                                                              
                          phi   0.00000                                                              
                          tth   0.00000                                                              
                          ===== =======                                                              
    constraints           ===== ========= ========== ===== ====                                      
                          axis  low_limit high_limit value fit                                       
                          ===== ========= ========== ===== ====                                      
                          omega -180.0    180.0      0.0   True                                      
                          chi   -180.0    180.0      0.0   True                                      
                          phi   -180.0    180.0      0.0   True                                      
                          tth   -180.0    180.0      0.0   True                                      
                          ===== ========= ========== ===== ====                                      
    sample: silicon       ================= =========================================================
                          term              value                                                    
                          ================= =========================================================
                          unit cell edges   a=5.431020511, b=5.431020511, c=5.431020511              
                          unit cell angles  alpha=90.0, beta=90.0, gamma=90.0                        
                          ref 1 (hkl)       h=4.0, k=0.0, l=0.0                                      
                          ref 1 positioners omega=-145.45100, chi=0.00000, phi=0.00000, tth=69.09660 
                          ref 2 (hkl)       h=0.0, k=4.0, l=0.0                                      
                          ref 2 positioners omega=-145.45100, chi=0.00000, phi=90.00000, tth=69.09660
                          [U]               [[-1.22173048e-05 -1.00000000e+00  0.00000000e+00]       
                                             [ 0.00000000e+00  0.00000000e+00  1.00000000e+00]       
                                             [-1.00000000e+00  1.22173048e-05  0.00000000e+00]]      
                          [UB]              [[-1.41342846e-05 -1.15690694e+00  7.08409844e-17]       
                                             [ 0.00000000e+00  0.00000000e+00  1.15690694e+00]       
                                             [-1.15690694e+00  1.41342846e-05  7.08392534e-17]]      
                          ================= =========================================================
    ===================== ===========================================================================
    
    ===================== ====================================================================
    term                  value                                                               
    ===================== ====================================================================
    diffractometer        orange                                                              
    geometry              E4CV                                                                
    class                 Fourc                                                               
    energy (keV)          8.05092                                                             
    wavelength (angstrom) 1.54000                                                             
    calc engine           hkl                                                                 
    mode                  bissector                                                           
    positions             ===== =======                                                       
                          name  value                                                         
                          ===== =======                                                       
                          omega 0.00000                                                       
                          chi   0.00000                                                       
                          phi   0.00000                                                       
                          tth   0.00000                                                       
                          ===== =======                                                       
    constraints           ===== ========= ========== ===== ====                               
                          axis  low_limit high_limit value fit                                
                          ===== ========= ========== ===== ====                               
                          omega -180.0    180.0      0.0   True                               
                          chi   -180.0    180.0      0.0   True                               
                          phi   -180.0    180.0      0.0   True                               
                          tth   -180.0    180.0      0.0   True                               
                          ===== ========= ========== ===== ====                               
    sample: main          ================ ===================================================
                          term             value                                              
                          ================ ===================================================
                          unit cell edges  a=1.54, b=1.54, c=1.54                             
                          unit cell angles alpha=90.0, beta=90.0, gamma=90.0                  
                          [U]              [[1. 0. 0.]                                        
                                            [0. 1. 0.]                                        
                                            [0. 0. 1.]]                                       
                          [UB]             [[ 4.07999046e+00 -2.49827363e-16 -2.49827363e-16] 
                                            [ 0.00000000e+00  4.07999046e+00 -2.49827363e-16] 
                                            [ 0.00000000e+00  0.00000000e+00  4.07999046e+00]]
                          ================ ===================================================
    ===================== ====================================================================
    




.. parsed-literal::

    <pyRestTable.rest_table.Table at 0x7fe5a805f6d0>



Build simulators for other diffractometer geometries to test code that
differentiates between various possibile sources for restore of
orientation information.

.. code:: ipython3

    class Kappa(SimulatedK4CV):
        pass
    
    kappa = Kappa("", name="kappa")
    kappa.energy.put(A_KEV / 1.54)
    a0 = SI_LATTICE_PARAMETER
    kappa.calc.new_sample("silicon", lattice=(a0, a0, a0, 90, 90, 90))
    kappa.calc.sample.compute_UB(
        kappa.calc.sample.add_reflection(4, 0, 0, (55.4507, 0, 90, -69.0966)), 
        kappa.calc.sample.add_reflection(0, 4, 0, (-1.5950, 134.7568, 123.3554, -69.0966))
    )
    kappa.pa()


.. parsed-literal::

    ===================== =================================================================================
    term                  value                                                                            
    ===================== =================================================================================
    diffractometer        kappa                                                                            
    geometry              K4CV                                                                             
    class                 Kappa                                                                            
    energy (keV)          8.05092                                                                          
    wavelength (angstrom) 1.54000                                                                          
    calc engine           hkl                                                                              
    mode                  bissector                                                                        
    positions             ====== =======                                                                   
                          name   value                                                                     
                          ====== =======                                                                   
                          komega 0.00000                                                                   
                          kappa  0.00000                                                                   
                          kphi   0.00000                                                                   
                          tth    0.00000                                                                   
                          ====== =======                                                                   
    constraints           ====== ========= ========== ===== ====                                           
                          axis   low_limit high_limit value fit                                            
                          ====== ========= ========== ===== ====                                           
                          komega -180.0    180.0      0.0   True                                           
                          kappa  -180.0    180.0      0.0   True                                           
                          kphi   -180.0    180.0      0.0   True                                           
                          tth    -180.0    180.0      0.0   True                                           
                          ====== ========= ========== ===== ====                                           
    sample: silicon       ================= ===============================================================
                          term              value                                                          
                          ================= ===============================================================
                          unit cell edges   a=5.431020511, b=5.431020511, c=5.431020511                    
                          unit cell angles  alpha=90.0, beta=90.0, gamma=90.0                              
                          ref 1 (hkl)       h=4.0, k=0.0, l=0.0                                            
                          ref 1 positioners komega=55.45070, kappa=0.00000, kphi=90.00000, tth=-69.09660   
                          ref 2 (hkl)       h=0.0, k=4.0, l=0.0                                            
                          ref 2 positioners komega=-1.59500, kappa=134.75680, kphi=123.35540, tth=-69.09660
                          [U]               [[-1.74532925e-05 -6.22695871e-06  1.00000000e+00]             
                                             [ 0.00000000e+00 -1.00000000e+00 -6.22695872e-06]             
                                             [ 1.00000000e+00 -1.08680932e-10  1.74532925e-05]]            
                          [UB]              [[-2.01918352e-05 -7.20401174e-06  1.15690694e+00]             
                                             [ 0.00000000e+00 -1.15690694e+00 -7.20401174e-06]             
                                             [ 1.15690694e+00 -1.25733795e-10  2.01918352e-05]]            
                          ================= ===============================================================
    ===================== =================================================================================
    




.. parsed-literal::

    <pyRestTable.rest_table.Table at 0x7fe58f3a3070>



.. code:: ipython3

    class Sixc(SimulatedE6C):
        pass
    
    sixc = Sixc("", name="sixc")
    sixc.energy.put(A_KEV / 1.54)
    a0 = SI_LATTICE_PARAMETER
    sixc.calc.new_sample("silicon", lattice=(a0, a0, a0, 90, 90, 90))
    sixc.calc.sample.compute_UB(
        sixc.calc.sample.add_reflection(4, 0, 0, (0, -145.451, 0, 0, 0, 69.0966)),
        sixc.calc.sample.add_reflection(0, 4, 0, (0, -145.451, 90, 0, 0, 69.0966))
    )
    sixc.pa()


.. parsed-literal::

    ===================== ========================================================================================================
    term                  value                                                                                                   
    ===================== ========================================================================================================
    diffractometer        sixc                                                                                                    
    geometry              E6C                                                                                                     
    class                 Sixc                                                                                                    
    energy (keV)          8.05092                                                                                                 
    wavelength (angstrom) 1.54000                                                                                                 
    calc engine           hkl                                                                                                     
    mode                  bissector_vertical                                                                                      
    positions             ===== =======                                                                                           
                          name  value                                                                                             
                          ===== =======                                                                                           
                          mu    0.00000                                                                                           
                          omega 0.00000                                                                                           
                          chi   0.00000                                                                                           
                          phi   0.00000                                                                                           
                          gamma 0.00000                                                                                           
                          delta 0.00000                                                                                           
                          ===== =======                                                                                           
    constraints           ===== ========= ========== ===== ====                                                                   
                          axis  low_limit high_limit value fit                                                                    
                          ===== ========= ========== ===== ====                                                                   
                          mu    -180.0    180.0      0.0   True                                                                   
                          omega -180.0    180.0      0.0   True                                                                   
                          chi   -180.0    180.0      0.0   True                                                                   
                          phi   -180.0    180.0      0.0   True                                                                   
                          gamma -180.0    180.0      0.0   True                                                                   
                          delta -180.0    180.0      0.0   True                                                                   
                          ===== ========= ========== ===== ====                                                                   
    sample: silicon       ================= ======================================================================================
                          term              value                                                                                 
                          ================= ======================================================================================
                          unit cell edges   a=5.431020511, b=5.431020511, c=5.431020511                                           
                          unit cell angles  alpha=90.0, beta=90.0, gamma=90.0                                                     
                          ref 1 (hkl)       h=4.0, k=0.0, l=0.0                                                                   
                          ref 1 positioners mu=0.00000, omega=-145.45100, chi=0.00000, phi=0.00000, gamma=0.00000, delta=69.09660 
                          ref 2 (hkl)       h=0.0, k=4.0, l=0.0                                                                   
                          ref 2 positioners mu=0.00000, omega=-145.45100, chi=90.00000, phi=0.00000, gamma=0.00000, delta=69.09660
                          [U]               [[-1.22173048e-05 -1.22173048e-05 -1.00000000e+00]                                    
                                             [ 0.00000000e+00 -1.00000000e+00  1.22173048e-05]                                    
                                             [-1.00000000e+00  1.49262536e-10  1.22173048e-05]]                                   
                          [UB]              [[-1.41342846e-05 -1.41342846e-05 -1.15690694e+00]                                    
                                             [ 0.00000000e+00 -1.15690694e+00  1.41342846e-05]                                    
                                             [-1.15690694e+00  1.72682934e-10  1.41342846e-05]]                                   
                          ================= ======================================================================================
    ===================== ========================================================================================================
    




.. parsed-literal::

    <pyRestTable.rest_table.Table at 0x7fe58f358ac0>



Collect data with all the diffractometers
-----------------------------------------

Show data collection with and without the orientation information.

**Tip**: To save orientation information, add the diffractometer as an
additional detector. That’s all! Works with any scan that supports
multiple detectors.

.. code:: ipython3

    def scan_all():
        ### count runs ###
        # this run will not save orientation information
        yield from bp.count([noisy_det])
        # this run _will_ save orientation information for fourc
        yield from bp.count([noisy_det, fourc])
        # this run _will_ save orientation information for several diffractometers
        yield from bp.count([noisy_det, fourc, orange, kappa, sixc])
    
        ### scan runs ###
        yield from bp.scan([noisy_det], fourc.h, 0.9, 1.1, 2)
        yield from bp.scan([noisy_det, fourc], fourc.h, 0.9, 1.1, 2)
        yield from bp.scan([noisy_det], kappa.h, 0.9, 1.1, 2)
        yield from bp.scan([noisy_det, kappa], kappa.h, 0.9, 1.1, 2)
        yield from bp.scan([noisy_det], sixc.h, 0.9, 1.1, 2)
        yield from bp.scan([noisy_det, sixc], sixc.h, 0.9, 1.1, 2)
    
        ### mesh runs at the (100) ###
        # first, move to the (100)
        yield from bps.mv(fourc.h, 1, fourc.k, 0, fourc.l, 0)
        yield from bp.rel_grid_scan([noisy_det], fourc.h, -0.1, 0.1, 3, fourc.k, -0.1, 0.1, 3)
        yield from bp.rel_grid_scan([noisy_det, fourc], fourc.h, -0.1, 0.1, 3, fourc.k, -0.1, 0.1, 3)

Run the scans, gather all the uids into a variable to be ignored. That
way, they do not print.

.. code:: ipython3

    _uids = RE(scan_all())


.. parsed-literal::

    
    
    Transient Scan ID: 1     Time: 2021-07-19 16:26:09
    Persistent Unique Scan ID: 'b4131d5b-fe00-4a7f-96d0-57ee925903bf'
    New stream: 'primary'
    +-----------+------------+------------+
    |   seq_num |       time |  noisy_det |
    +-----------+------------+------------+
    |         1 | 16:26:09.9 |      1.088 |
    +-----------+------------+------------+
    generator count ['b4131d5b'] (scan num: 1)
    
    
    
    
    
    Transient Scan ID: 2     Time: 2021-07-19 16:26:10
    Persistent Unique Scan ID: '586982ae-ba40-49b0-b9a6-e2f405f76481'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+------------+
    |   seq_num |       time |    fourc_h |    fourc_k |    fourc_l |  noisy_det |
    +-----------+------------+------------+------------+------------+------------+
    |         1 | 16:26:10.1 |      0.000 |      0.000 |      0.000 |      1.050 |
    +-----------+------------+------------+------------+------------+------------+
    generator count ['586982ae'] (scan num: 2)
    
    
    
    
    
    Transient Scan ID: 3     Time: 2021-07-19 16:26:10
    Persistent Unique Scan ID: '1a9f4aab-81bb-4633-aead-06f4632d1bc2'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
    |   seq_num |       time |     sixc_h |     sixc_k |     sixc_l |  noisy_det |   orange_h |   orange_k |   orange_l |    kappa_h |    kappa_k |    kappa_l |    fourc_h |    fourc_k |    fourc_l |
    +-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
    |         1 | 16:26:10.3 |     -0.000 |      0.000 |      0.000 |      0.943 |      0.000 |      0.000 |      0.000 |      0.000 |     -0.000 |      0.000 |      0.000 |      0.000 |      0.000 |
    +-----------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+------------+
    generator count ['1a9f4aab'] (scan num: 3)
    
    
    
    
    
    Transient Scan ID: 4     Time: 2021-07-19 16:26:10
    Persistent Unique Scan ID: '21fa3fbd-7035-4568-9184-246ba301f7ec'
    New stream: 'primary'
    +-----------+------------+------------+------------+
    |   seq_num |       time |    fourc_h |  noisy_det |
    +-----------+------------+------------+------------+
    |         1 | 16:26:10.5 |      0.900 |      0.983 |
    |         2 | 16:26:10.5 |      1.100 |      0.994 |
    +-----------+------------+------------+------------+
    generator scan ['21fa3fbd'] (scan num: 4)
    
    
    
    
    
    Transient Scan ID: 5     Time: 2021-07-19 16:26:10
    Persistent Unique Scan ID: 'f12094c1-a99f-453a-aeab-70b2c8c94d45'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+------------+
    |   seq_num |       time |    fourc_h |    fourc_k |    fourc_l |  noisy_det |
    +-----------+------------+------------+------------+------------+------------+
    |         1 | 16:26:10.6 |      0.900 |      0.000 |     -0.000 |      0.958 |
    |         2 | 16:26:10.7 |      1.100 |      0.000 |     -0.000 |      0.923 |
    +-----------+------------+------------+------------+------------+------------+
    generator scan ['f12094c1'] (scan num: 5)
    
    
    
    
    
    Transient Scan ID: 6     Time: 2021-07-19 16:26:10
    Persistent Unique Scan ID: '3b137b79-9d6f-4244-904f-9516ffbdc05f'
    New stream: 'primary'
    +-----------+------------+------------+------------+
    |   seq_num |       time |    kappa_h |  noisy_det |
    +-----------+------------+------------+------------+
    |         1 | 16:26:10.9 |      0.900 |      0.907 |
    |         2 | 16:26:10.9 |      1.100 |      0.914 |
    +-----------+------------+------------+------------+
    generator scan ['3b137b79'] (scan num: 6)
    
    
    
    
    
    Transient Scan ID: 7     Time: 2021-07-19 16:26:11
    Persistent Unique Scan ID: 'c051b2dc-cec5-4326-9928-dac8aa104f8c'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+------------+
    |   seq_num |       time |    kappa_h |    kappa_k |    kappa_l |  noisy_det |
    +-----------+------------+------------+------------+------------+------------+
    |         1 | 16:26:11.1 |      0.900 |      0.000 |     -0.000 |      0.982 |
    |         2 | 16:26:11.2 |      1.100 |     -0.000 |      0.000 |      1.088 |
    +-----------+------------+------------+------------+------------+------------+
    generator scan ['c051b2dc'] (scan num: 7)
    
    
    
    
    
    Transient Scan ID: 8     Time: 2021-07-19 16:26:11
    Persistent Unique Scan ID: '76f116f4-ace2-4bd0-bac0-78f0405cd29f'
    New stream: 'primary'
    +-----------+------------+------------+------------+
    |   seq_num |       time |     sixc_h |  noisy_det |
    +-----------+------------+------------+------------+
    |         1 | 16:26:11.3 |      0.900 |      0.901 |
    |         2 | 16:26:11.4 |      1.100 |      1.064 |
    +-----------+------------+------------+------------+
    generator scan ['76f116f4'] (scan num: 8)
    
    
    
    
    
    Transient Scan ID: 9     Time: 2021-07-19 16:26:11
    Persistent Unique Scan ID: 'f4deb68d-88e6-4ba9-b4c2-4308fc3fa805'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+------------+
    |   seq_num |       time |     sixc_h |     sixc_k |     sixc_l |  noisy_det |
    +-----------+------------+------------+------------+------------+------------+
    |         1 | 16:26:11.5 |      0.900 |      0.000 |      0.000 |      1.016 |
    |         2 | 16:26:11.6 |      1.100 |      0.000 |      0.000 |      0.994 |
    +-----------+------------+------------+------------+------------+------------+
    generator scan ['f4deb68d'] (scan num: 9)
    
    
    
    
    
    Transient Scan ID: 10     Time: 2021-07-19 16:26:11
    Persistent Unique Scan ID: '6c2937fb-3d6c-4ea1-b107-4ef1428f3b7f'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+------------+
    |   seq_num |       time |    fourc_h |    fourc_k |    fourc_l |  noisy_det |
    +-----------+------------+------------+------------+------------+------------+
    |         1 | 16:26:11.8 |      0.900 |     -0.100 |      0.000 |      1.040 |
    |         2 | 16:26:11.8 |      0.900 |     -0.000 |      0.000 |      0.982 |
    |         3 | 16:26:11.8 |      0.900 |      0.100 |      0.000 |      0.920 |
    |         4 | 16:26:11.8 |      1.000 |     -0.100 |      0.000 |      1.089 |
    |         5 | 16:26:11.8 |      1.000 |     -0.000 |      0.000 |      1.095 |
    |         6 | 16:26:11.8 |      1.000 |      0.100 |      0.000 |      1.014 |
    |         7 | 16:26:11.8 |      1.100 |     -0.100 |      0.000 |      1.098 |
    |         8 | 16:26:11.8 |      1.100 |     -0.000 |      0.000 |      1.040 |
    |         9 | 16:26:11.8 |      1.100 |      0.100 |      0.000 |      0.986 |
    +-----------+------------+------------+------------+------------+------------+
    generator rel_grid_scan ['6c2937fb'] (scan num: 10)
    
    
    
    
    
    Transient Scan ID: 11     Time: 2021-07-19 16:26:11
    Persistent Unique Scan ID: '9c21e27f-a3c4-4301-b0f0-57ca614bd39b'
    New stream: 'primary'
    +-----------+------------+------------+------------+------------+------------+
    |   seq_num |       time |    fourc_h |    fourc_k |    fourc_l |  noisy_det |
    +-----------+------------+------------+------------+------------+------------+
    |         1 | 16:26:12.0 |      0.900 |     -0.100 |      0.000 |      1.011 |
    |         2 | 16:26:12.0 |      0.900 |     -0.000 |      0.000 |      0.901 |
    |         3 | 16:26:12.0 |      0.900 |      0.100 |      0.000 |      0.938 |
    |         4 | 16:26:12.0 |      1.000 |     -0.100 |      0.000 |      0.985 |
    |         5 | 16:26:12.0 |      1.000 |     -0.000 |      0.000 |      1.016 |
    |         6 | 16:26:12.0 |      1.000 |      0.100 |      0.000 |      1.004 |
    |         7 | 16:26:12.0 |      1.100 |     -0.100 |      0.000 |      0.992 |
    |         8 | 16:26:12.0 |      1.100 |     -0.000 |      0.000 |      0.954 |
    |         9 | 16:26:12.0 |      1.100 |      0.100 |      0.000 |      1.009 |
    +-----------+------------+------------+------------+------------+------------+
    generator rel_grid_scan ['9c21e27f'] (scan num: 11)
    
    
    


--------------

Show the orientation information that was collected
===================================================

Show the full contents of the descriptor document (primary stream) for
the ``fourc`` “detector” from the run with ``scan_id=5``. This is where
the orientation information is saved. You may need to expand the *Data
variables* row to see all the orientation information.

.. code:: ipython3

    cat[5].primary.config["fourc"].read()




.. raw:: html

    <div><svg style="position: absolute; width: 0; height: 0; overflow: hidden">
    <defs>
    <symbol id="icon-database" viewBox="0 0 32 32">
    <path d="M16 0c-8.837 0-16 2.239-16 5v4c0 2.761 7.163 5 16 5s16-2.239 16-5v-4c0-2.761-7.163-5-16-5z"></path>
    <path d="M16 17c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
    <path d="M16 26c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
    </symbol>
    <symbol id="icon-file-text2" viewBox="0 0 32 32">
    <path d="M28.681 7.159c-0.694-0.947-1.662-2.053-2.724-3.116s-2.169-2.030-3.116-2.724c-1.612-1.182-2.393-1.319-2.841-1.319h-15.5c-1.378 0-2.5 1.121-2.5 2.5v27c0 1.378 1.122 2.5 2.5 2.5h23c1.378 0 2.5-1.122 2.5-2.5v-19.5c0-0.448-0.137-1.23-1.319-2.841zM24.543 5.457c0.959 0.959 1.712 1.825 2.268 2.543h-4.811v-4.811c0.718 0.556 1.584 1.309 2.543 2.268zM28 29.5c0 0.271-0.229 0.5-0.5 0.5h-23c-0.271 0-0.5-0.229-0.5-0.5v-27c0-0.271 0.229-0.5 0.5-0.5 0 0 15.499-0 15.5 0v7c0 0.552 0.448 1 1 1h7v19.5z"></path>
    <path d="M23 26h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    <path d="M23 22h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    <path d="M23 18h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
    </symbol>
    </defs>
    </svg>
    <style>/* CSS stylesheet for displaying xarray objects in jupyterlab.
     *
     */
    
    :root {
      --xr-font-color0: var(--jp-content-font-color0, rgba(0, 0, 0, 1));
      --xr-font-color2: var(--jp-content-font-color2, rgba(0, 0, 0, 0.54));
      --xr-font-color3: var(--jp-content-font-color3, rgba(0, 0, 0, 0.38));
      --xr-border-color: var(--jp-border-color2, #e0e0e0);
      --xr-disabled-color: var(--jp-layout-color3, #bdbdbd);
      --xr-background-color: var(--jp-layout-color0, white);
      --xr-background-color-row-even: var(--jp-layout-color1, white);
      --xr-background-color-row-odd: var(--jp-layout-color2, #eeeeee);
    }
    
    html[theme=dark],
    body.vscode-dark {
      --xr-font-color0: rgba(255, 255, 255, 1);
      --xr-font-color2: rgba(255, 255, 255, 0.54);
      --xr-font-color3: rgba(255, 255, 255, 0.38);
      --xr-border-color: #1F1F1F;
      --xr-disabled-color: #515151;
      --xr-background-color: #111111;
      --xr-background-color-row-even: #111111;
      --xr-background-color-row-odd: #313131;
    }
    
    .xr-wrap {
      display: block;
      min-width: 300px;
      max-width: 700px;
    }
    
    .xr-text-repr-fallback {
      /* fallback to plain text repr when CSS is not injected (untrusted notebook) */
      display: none;
    }
    
    .xr-header {
      padding-top: 6px;
      padding-bottom: 6px;
      margin-bottom: 4px;
      border-bottom: solid 1px var(--xr-border-color);
    }
    
    .xr-header > div,
    .xr-header > ul {
      display: inline;
      margin-top: 0;
      margin-bottom: 0;
    }
    
    .xr-obj-type,
    .xr-array-name {
      margin-left: 2px;
      margin-right: 10px;
    }
    
    .xr-obj-type {
      color: var(--xr-font-color2);
    }
    
    .xr-sections {
      padding-left: 0 !important;
      display: grid;
      grid-template-columns: 150px auto auto 1fr 20px 20px;
    }
    
    .xr-section-item {
      display: contents;
    }
    
    .xr-section-item input {
      display: none;
    }
    
    .xr-section-item input + label {
      color: var(--xr-disabled-color);
    }
    
    .xr-section-item input:enabled + label {
      cursor: pointer;
      color: var(--xr-font-color2);
    }
    
    .xr-section-item input:enabled + label:hover {
      color: var(--xr-font-color0);
    }
    
    .xr-section-summary {
      grid-column: 1;
      color: var(--xr-font-color2);
      font-weight: 500;
    }
    
    .xr-section-summary > span {
      display: inline-block;
      padding-left: 0.5em;
    }
    
    .xr-section-summary-in:disabled + label {
      color: var(--xr-font-color2);
    }
    
    .xr-section-summary-in + label:before {
      display: inline-block;
      content: '►';
      font-size: 11px;
      width: 15px;
      text-align: center;
    }
    
    .xr-section-summary-in:disabled + label:before {
      color: var(--xr-disabled-color);
    }
    
    .xr-section-summary-in:checked + label:before {
      content: '▼';
    }
    
    .xr-section-summary-in:checked + label > span {
      display: none;
    }
    
    .xr-section-summary,
    .xr-section-inline-details {
      padding-top: 4px;
      padding-bottom: 4px;
    }
    
    .xr-section-inline-details {
      grid-column: 2 / -1;
    }
    
    .xr-section-details {
      display: none;
      grid-column: 1 / -1;
      margin-bottom: 5px;
    }
    
    .xr-section-summary-in:checked ~ .xr-section-details {
      display: contents;
    }
    
    .xr-array-wrap {
      grid-column: 1 / -1;
      display: grid;
      grid-template-columns: 20px auto;
    }
    
    .xr-array-wrap > label {
      grid-column: 1;
      vertical-align: top;
    }
    
    .xr-preview {
      color: var(--xr-font-color3);
    }
    
    .xr-array-preview,
    .xr-array-data {
      padding: 0 5px !important;
      grid-column: 2;
    }
    
    .xr-array-data,
    .xr-array-in:checked ~ .xr-array-preview {
      display: none;
    }
    
    .xr-array-in:checked ~ .xr-array-data,
    .xr-array-preview {
      display: inline-block;
    }
    
    .xr-dim-list {
      display: inline-block !important;
      list-style: none;
      padding: 0 !important;
      margin: 0;
    }
    
    .xr-dim-list li {
      display: inline-block;
      padding: 0;
      margin: 0;
    }
    
    .xr-dim-list:before {
      content: '(';
    }
    
    .xr-dim-list:after {
      content: ')';
    }
    
    .xr-dim-list li:not(:last-child):after {
      content: ',';
      padding-right: 5px;
    }
    
    .xr-has-index {
      font-weight: bold;
    }
    
    .xr-var-list,
    .xr-var-item {
      display: contents;
    }
    
    .xr-var-item > div,
    .xr-var-item label,
    .xr-var-item > .xr-var-name span {
      background-color: var(--xr-background-color-row-even);
      margin-bottom: 0;
    }
    
    .xr-var-item > .xr-var-name:hover span {
      padding-right: 5px;
    }
    
    .xr-var-list > li:nth-child(odd) > div,
    .xr-var-list > li:nth-child(odd) > label,
    .xr-var-list > li:nth-child(odd) > .xr-var-name span {
      background-color: var(--xr-background-color-row-odd);
    }
    
    .xr-var-name {
      grid-column: 1;
    }
    
    .xr-var-dims {
      grid-column: 2;
    }
    
    .xr-var-dtype {
      grid-column: 3;
      text-align: right;
      color: var(--xr-font-color2);
    }
    
    .xr-var-preview {
      grid-column: 4;
    }
    
    .xr-var-name,
    .xr-var-dims,
    .xr-var-dtype,
    .xr-preview,
    .xr-attrs dt {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      padding-right: 10px;
    }
    
    .xr-var-name:hover,
    .xr-var-dims:hover,
    .xr-var-dtype:hover,
    .xr-attrs dt:hover {
      overflow: visible;
      width: auto;
      z-index: 1;
    }
    
    .xr-var-attrs,
    .xr-var-data {
      display: none;
      background-color: var(--xr-background-color) !important;
      padding-bottom: 5px !important;
    }
    
    .xr-var-attrs-in:checked ~ .xr-var-attrs,
    .xr-var-data-in:checked ~ .xr-var-data {
      display: block;
    }
    
    .xr-var-data > table {
      float: right;
    }
    
    .xr-var-name span,
    .xr-var-data,
    .xr-attrs {
      padding-left: 25px !important;
    }
    
    .xr-attrs,
    .xr-var-attrs,
    .xr-var-data {
      grid-column: 1 / -1;
    }
    
    dl.xr-attrs {
      padding: 0;
      margin: 0;
      display: grid;
      grid-template-columns: 125px auto;
    }
    
    .xr-attrs dt,
    .xr-attrs dd {
      padding: 0;
      margin: 0;
      float: left;
      padding-right: 10px;
      width: auto;
    }
    
    .xr-attrs dt {
      font-weight: normal;
      grid-column: 1;
    }
    
    .xr-attrs dt:hover span {
      display: inline-block;
      background: var(--xr-background-color);
      padding-right: 10px;
    }
    
    .xr-attrs dd {
      grid-column: 2;
      white-space: pre-wrap;
      word-break: break-all;
    }
    
    .xr-icon-database,
    .xr-icon-file-text2 {
      display: inline-block;
      vertical-align: middle;
      width: 1em;
      height: 1.5em !important;
      stroke-width: 0;
      stroke: currentColor;
      fill: currentColor;
    }
    </style><pre class='xr-text-repr-fallback'>&lt;xarray.Dataset&gt;
    Dimensions:                    (dim_0: 6, dim_1: 6, dim_10: 4, dim_11: 21, dim_2: 3, dim_3: 3, dim_4: 3, dim_5: 3, dim_6: 2, dim_7: 3, dim_8: 4, dim_9: 4, time: 2)
    Coordinates:
      * time                       (time) float64 1.627e+09 1.627e+09
    Dimensions without coordinates: dim_0, dim_1, dim_10, dim_11, dim_2, dim_3, dim_4, dim_5, dim_6, dim_7, dim_8, dim_9
    Data variables: (12/21)
        fourc_energy               (time) float64 8.051 8.051
        fourc_energy_units         (time) &lt;U3 &#x27;keV&#x27; &#x27;keV&#x27;
        fourc_energy_offset        (time) int64 0 0
        fourc_geometry_name        (time) &lt;U4 &#x27;E4CV&#x27; &#x27;E4CV&#x27;
        fourc_class_name           (time) &lt;U5 &#x27;Fourc&#x27; &#x27;Fourc&#x27;
        fourc_sample_name          (time) &lt;U7 &#x27;silicon&#x27; &#x27;silicon&#x27;
        ...                         ...
        fourc__hklpy_version       (time) &lt;U25 &#x27;0.3.16+168.geb1a3db.dirty&#x27; &#x27;0.3.1...
        fourc__pseudos             (time, dim_7) &lt;U1 &#x27;h&#x27; &#x27;k&#x27; &#x27;l&#x27; &#x27;h&#x27; &#x27;k&#x27; &#x27;l&#x27;
        fourc__reals               (time, dim_8) &lt;U5 &#x27;omega&#x27; &#x27;chi&#x27; ... &#x27;phi&#x27; &#x27;tth&#x27;
        fourc__constraints         (time, dim_9, dim_10) float64 -180.0 ... 1.0
        fourc__mode                (time) &lt;U9 &#x27;bissector&#x27; &#x27;bissector&#x27;
        fourc_orientation_attrs    (time, dim_11) &lt;U19 &#x27;orientation_attrs&#x27; ... &#x27;_...</pre><div class='xr-wrap' hidden><div class='xr-header'><div class='xr-obj-type'>xarray.Dataset</div></div><ul class='xr-sections'><li class='xr-section-item'><input id='section-80c5f536-ea05-4a19-86be-3eeebfae00f5' class='xr-section-summary-in' type='checkbox' disabled ><label for='section-80c5f536-ea05-4a19-86be-3eeebfae00f5' class='xr-section-summary'  title='Expand/collapse section'>Dimensions:</label><div class='xr-section-inline-details'><ul class='xr-dim-list'><li><span>dim_0</span>: 6</li><li><span>dim_1</span>: 6</li><li><span>dim_10</span>: 4</li><li><span>dim_11</span>: 21</li><li><span>dim_2</span>: 3</li><li><span>dim_3</span>: 3</li><li><span>dim_4</span>: 3</li><li><span>dim_5</span>: 3</li><li><span>dim_6</span>: 2</li><li><span>dim_7</span>: 3</li><li><span>dim_8</span>: 4</li><li><span>dim_9</span>: 4</li><li><span class='xr-has-index'>time</span>: 2</li></ul></div><div class='xr-section-details'></div></li><li class='xr-section-item'><input id='section-65cdb2cd-5df5-4544-b86b-7b1da413ffac' class='xr-section-summary-in' type='checkbox'  checked><label for='section-65cdb2cd-5df5-4544-b86b-7b1da413ffac' class='xr-section-summary' >Coordinates: <span>(1)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>time</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>1.627e+09 1.627e+09</div><input id='attrs-dd8c3290-dcb9-4e56-b896-1492f53969b5' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-dd8c3290-dcb9-4e56-b896-1492f53969b5' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-bb16e55a-7df4-4695-be2c-b5b6c8d037d1' class='xr-var-data-in' type='checkbox'><label for='data-bb16e55a-7df4-4695-be2c-b5b6c8d037d1' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([1.62673e+09, 1.62673e+09])</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-e14cc002-e17e-4703-b533-f27cdc46ca51' class='xr-section-summary-in' type='checkbox'  ><label for='section-e14cc002-e17e-4703-b533-f27cdc46ca51' class='xr-section-summary' >Data variables: <span>(21)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span>fourc_energy</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>8.051 8.051</div><input id='attrs-b38c6adc-c3bb-48dd-a140-91807c8fd8f4' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-b38c6adc-c3bb-48dd-a140-91807c8fd8f4' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-7b66506f-4acc-4d5b-8667-30de12197694' class='xr-var-data-in' type='checkbox'><label for='data-7b66506f-4acc-4d5b-8667-30de12197694' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([8.05092195, 8.05092195])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_energy_units</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>&lt;U3</div><div class='xr-var-preview xr-preview'>&#x27;keV&#x27; &#x27;keV&#x27;</div><input id='attrs-e9723ac2-9af4-4622-ad9f-a7e8272ff473' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-e9723ac2-9af4-4622-ad9f-a7e8272ff473' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-72121569-60b7-477c-a290-fe012e89fc86' class='xr-var-data-in' type='checkbox'><label for='data-72121569-60b7-477c-a290-fe012e89fc86' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;keV&#x27;, &#x27;keV&#x27;], dtype=&#x27;&lt;U3&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_energy_offset</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>int64</div><div class='xr-var-preview xr-preview'>0 0</div><input id='attrs-043960cf-e551-488b-9870-30d21393b736' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-043960cf-e551-488b-9870-30d21393b736' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-fe0d7cab-c82f-421e-ab54-805fd1b28920' class='xr-var-data-in' type='checkbox'><label for='data-fe0d7cab-c82f-421e-ab54-805fd1b28920' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([0, 0])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_geometry_name</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>&lt;U4</div><div class='xr-var-preview xr-preview'>&#x27;E4CV&#x27; &#x27;E4CV&#x27;</div><input id='attrs-247d7c94-5df3-4472-9e05-76a99b9066af' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-247d7c94-5df3-4472-9e05-76a99b9066af' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-2988d1bc-342f-463e-a58b-f3dc3494a68c' class='xr-var-data-in' type='checkbox'><label for='data-2988d1bc-342f-463e-a58b-f3dc3494a68c' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;E4CV&#x27;, &#x27;E4CV&#x27;], dtype=&#x27;&lt;U4&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_class_name</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>&lt;U5</div><div class='xr-var-preview xr-preview'>&#x27;Fourc&#x27; &#x27;Fourc&#x27;</div><input id='attrs-d700ddd5-7bef-4356-9af5-83542a4a0fcb' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-d700ddd5-7bef-4356-9af5-83542a4a0fcb' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-621268d7-3116-4e86-b87b-c455b11452eb' class='xr-var-data-in' type='checkbox'><label for='data-621268d7-3116-4e86-b87b-c455b11452eb' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;Fourc&#x27;, &#x27;Fourc&#x27;], dtype=&#x27;&lt;U5&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_sample_name</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>&lt;U7</div><div class='xr-var-preview xr-preview'>&#x27;silicon&#x27; &#x27;silicon&#x27;</div><input id='attrs-4ca5d560-f446-43f5-aaec-11d227ce0357' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-4ca5d560-f446-43f5-aaec-11d227ce0357' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-ae29369b-595c-4703-8723-3761b209f858' class='xr-var-data-in' type='checkbox'><label for='data-ae29369b-595c-4703-8723-3761b209f858' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;silicon&#x27;, &#x27;silicon&#x27;], dtype=&#x27;&lt;U7&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_lattice</span></div><div class='xr-var-dims'>(time, dim_0)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>5.431 5.431 5.431 ... 90.0 90.0</div><input id='attrs-edbfda48-a3de-4703-8432-c6bfabecfbb6' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-edbfda48-a3de-4703-8432-c6bfabecfbb6' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-9fd965ea-f632-4aa4-a2f9-71614d4a9721' class='xr-var-data-in' type='checkbox'><label for='data-9fd965ea-f632-4aa4-a2f9-71614d4a9721' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[ 5.43102051,  5.43102051,  5.43102051, 90.        , 90.        ,
            90.        ],
           [ 5.43102051,  5.43102051,  5.43102051, 90.        , 90.        ,
            90.        ]])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_lattice_reciprocal</span></div><div class='xr-var-dims'>(time, dim_1)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>1.157 1.157 1.157 ... 90.0 90.0</div><input id='attrs-37e1bd98-c2a8-42b0-adaf-dc4c82bcd867' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-37e1bd98-c2a8-42b0-adaf-dc4c82bcd867' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-5339efe7-8880-4dc5-bc3c-7488a562221b' class='xr-var-data-in' type='checkbox'><label for='data-5339efe7-8880-4dc5-bc3c-7488a562221b' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[ 1.15690694,  1.15690694,  1.15690694, 90.        , 90.        ,
            90.        ],
           [ 1.15690694,  1.15690694,  1.15690694, 90.        , 90.        ,
            90.        ]])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_U</span></div><div class='xr-var-dims'>(time, dim_2, dim_3)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>-1.222e-05 -1.0 ... 1.222e-05 0.0</div><input id='attrs-4328944d-a713-47c8-ae35-494b8a1bec4e' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-4328944d-a713-47c8-ae35-494b8a1bec4e' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-7c0eeb1f-5b42-4f6a-b837-c6e978bd4820' class='xr-var-data-in' type='checkbox'><label for='data-7c0eeb1f-5b42-4f6a-b837-c6e978bd4820' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[[-1.22173048e-05, -1.00000000e+00,  0.00000000e+00],
            [ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00],
            [-1.00000000e+00,  1.22173048e-05,  0.00000000e+00]],
    
           [[-1.22173048e-05, -1.00000000e+00,  0.00000000e+00],
            [ 0.00000000e+00,  0.00000000e+00,  1.00000000e+00],
            [-1.00000000e+00,  1.22173048e-05,  0.00000000e+00]]])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_UB</span></div><div class='xr-var-dims'>(time, dim_4, dim_5)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>-1.413e-05 -1.157 ... 7.084e-17</div><input id='attrs-7b4bc845-54c6-4b65-96b9-ef93e6fe6dd8' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-7b4bc845-54c6-4b65-96b9-ef93e6fe6dd8' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-8e8108e5-2417-4977-8161-380cc21369d9' class='xr-var-data-in' type='checkbox'><label for='data-8e8108e5-2417-4977-8161-380cc21369d9' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[[-1.41342846e-05, -1.15690694e+00,  7.08409844e-17],
            [ 0.00000000e+00,  0.00000000e+00,  1.15690694e+00],
            [-1.15690694e+00,  1.41342846e-05,  7.08392534e-17]],
    
           [[-1.41342846e-05, -1.15690694e+00,  7.08409844e-17],
            [ 0.00000000e+00,  0.00000000e+00,  1.15690694e+00],
            [-1.15690694e+00,  1.41342846e-05,  7.08392534e-17]]])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_reflections_details</span></div><div class='xr-var-dims'>(time, dim_6)</div><div class='xr-var-dtype'>object</div><div class='xr-var-preview xr-preview'>{&#x27;reflection&#x27;: {&#x27;h&#x27;: 4.0, &#x27;k&#x27;: 0...</div><input id='attrs-991bf714-fe14-4926-852c-fe4229164771' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-991bf714-fe14-4926-852c-fe4229164771' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-0080e70d-9bf0-4d75-94f6-3555ccb6fe2d' class='xr-var-data-in' type='checkbox'><label for='data-0080e70d-9bf0-4d75-94f6-3555ccb6fe2d' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[{&#x27;reflection&#x27;: {&#x27;h&#x27;: 4.0, &#x27;k&#x27;: 0.0, &#x27;l&#x27;: 0.0}, &#x27;flag&#x27;: 1, &#x27;wavelength&#x27;: 1.54, &#x27;position&#x27;: {&#x27;omega&#x27;: -145.451, &#x27;chi&#x27;: 0.0, &#x27;phi&#x27;: 0.0, &#x27;tth&#x27;: 69.0966}, &#x27;orientation_reflection&#x27;: True},
            {&#x27;reflection&#x27;: {&#x27;h&#x27;: 0.0, &#x27;k&#x27;: 4.0, &#x27;l&#x27;: 0.0}, &#x27;flag&#x27;: 1, &#x27;wavelength&#x27;: 1.54, &#x27;position&#x27;: {&#x27;omega&#x27;: -145.451, &#x27;chi&#x27;: 0.0, &#x27;phi&#x27;: 90.0, &#x27;tth&#x27;: 69.0966}, &#x27;orientation_reflection&#x27;: True}],
           [{&#x27;reflection&#x27;: {&#x27;h&#x27;: 4.0, &#x27;k&#x27;: 0.0, &#x27;l&#x27;: 0.0}, &#x27;flag&#x27;: 1, &#x27;wavelength&#x27;: 1.54, &#x27;position&#x27;: {&#x27;omega&#x27;: -145.451, &#x27;chi&#x27;: 0.0, &#x27;phi&#x27;: 0.0, &#x27;tth&#x27;: 69.0966}, &#x27;orientation_reflection&#x27;: True},
            {&#x27;reflection&#x27;: {&#x27;h&#x27;: 0.0, &#x27;k&#x27;: 4.0, &#x27;l&#x27;: 0.0}, &#x27;flag&#x27;: 1, &#x27;wavelength&#x27;: 1.54, &#x27;position&#x27;: {&#x27;omega&#x27;: -145.451, &#x27;chi&#x27;: 0.0, &#x27;phi&#x27;: 90.0, &#x27;tth&#x27;: 69.0966}, &#x27;orientation_reflection&#x27;: True}]],
          dtype=object)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_ux</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>-90.0 -90.0</div><input id='attrs-7b136301-24bc-4868-bad1-630f29993c6a' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-7b136301-24bc-4868-bad1-630f29993c6a' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-be6fa422-25db-4822-b635-8ff2a7f652d9' class='xr-var-data-in' type='checkbox'><label for='data-be6fa422-25db-4822-b635-8ff2a7f652d9' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([-90., -90.])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_uy</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>0.0 0.0</div><input id='attrs-9c4b0a65-6ef4-4905-9184-999f951ff40b' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-9c4b0a65-6ef4-4905-9184-999f951ff40b' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-efd49528-76a1-4a99-88ad-e78e94ba3ec0' class='xr-var-data-in' type='checkbox'><label for='data-efd49528-76a1-4a99-88ad-e78e94ba3ec0' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([0., 0.])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_uz</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>90.0 90.0</div><input id='attrs-f998d79b-c523-4cd2-845c-c50ae6361586' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-f998d79b-c523-4cd2-845c-c50ae6361586' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-b9ae0ec2-97f7-4c76-bff4-82ab18f0b325' class='xr-var-data-in' type='checkbox'><label for='data-b9ae0ec2-97f7-4c76-bff4-82ab18f0b325' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([90.0007, 90.0007])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_diffractometer_name</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>&lt;U5</div><div class='xr-var-preview xr-preview'>&#x27;fourc&#x27; &#x27;fourc&#x27;</div><input id='attrs-9a520918-d3d3-4b00-826f-29ef0430bc43' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-9a520918-d3d3-4b00-826f-29ef0430bc43' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-d392e617-002a-4a51-bbd1-a8b335582bd9' class='xr-var-data-in' type='checkbox'><label for='data-d392e617-002a-4a51-bbd1-a8b335582bd9' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;fourc&#x27;, &#x27;fourc&#x27;], dtype=&#x27;&lt;U5&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc__hklpy_version</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>&lt;U25</div><div class='xr-var-preview xr-preview'>&#x27;0.3.16+168.geb1a3db.dirty&#x27; &#x27;0.3...</div><input id='attrs-33b95244-1849-4688-8647-070b2ecd23d4' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-33b95244-1849-4688-8647-070b2ecd23d4' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-f075cc8e-03cc-4b6c-9114-4e4299c95707' class='xr-var-data-in' type='checkbox'><label for='data-f075cc8e-03cc-4b6c-9114-4e4299c95707' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;0.3.16+168.geb1a3db.dirty&#x27;, &#x27;0.3.16+168.geb1a3db.dirty&#x27;],
          dtype=&#x27;&lt;U25&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc__pseudos</span></div><div class='xr-var-dims'>(time, dim_7)</div><div class='xr-var-dtype'>&lt;U1</div><div class='xr-var-preview xr-preview'>&#x27;h&#x27; &#x27;k&#x27; &#x27;l&#x27; &#x27;h&#x27; &#x27;k&#x27; &#x27;l&#x27;</div><input id='attrs-1c2411ea-6f48-4afb-8cf4-686801acd48c' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-1c2411ea-6f48-4afb-8cf4-686801acd48c' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-b1728782-e4dc-4a5c-91c0-0fb17d178292' class='xr-var-data-in' type='checkbox'><label for='data-b1728782-e4dc-4a5c-91c0-0fb17d178292' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[&#x27;h&#x27;, &#x27;k&#x27;, &#x27;l&#x27;],
           [&#x27;h&#x27;, &#x27;k&#x27;, &#x27;l&#x27;]], dtype=&#x27;&lt;U1&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc__reals</span></div><div class='xr-var-dims'>(time, dim_8)</div><div class='xr-var-dtype'>&lt;U5</div><div class='xr-var-preview xr-preview'>&#x27;omega&#x27; &#x27;chi&#x27; &#x27;phi&#x27; ... &#x27;phi&#x27; &#x27;tth&#x27;</div><input id='attrs-31dd2434-3419-4b66-bce7-5b4ee21a2985' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-31dd2434-3419-4b66-bce7-5b4ee21a2985' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-352ea330-cbbf-4fd0-82b7-802beb336445' class='xr-var-data-in' type='checkbox'><label for='data-352ea330-cbbf-4fd0-82b7-802beb336445' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[&#x27;omega&#x27;, &#x27;chi&#x27;, &#x27;phi&#x27;, &#x27;tth&#x27;],
           [&#x27;omega&#x27;, &#x27;chi&#x27;, &#x27;phi&#x27;, &#x27;tth&#x27;]], dtype=&#x27;&lt;U5&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc__constraints</span></div><div class='xr-var-dims'>(time, dim_9, dim_10)</div><div class='xr-var-dtype'>float64</div><div class='xr-var-preview xr-preview'>-180.0 180.0 -7.331 ... -14.66 1.0</div><input id='attrs-5e71e416-e2cf-4749-be16-8b2d21b3cf47' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-5e71e416-e2cf-4749-be16-8b2d21b3cf47' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-ceb85554-2d88-46dc-a611-6191ffb25a86' class='xr-var-data-in' type='checkbox'><label for='data-ceb85554-2d88-46dc-a611-6191ffb25a86' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[[-1.80000000e+02,  1.80000000e+02, -7.33094638e+00,
              1.00000000e+00],
            [-1.80000000e+02,  1.80000000e+02,  1.94355120e-86,
              1.00000000e+00],
            [-1.80000000e+02,  1.80000000e+02,  7.00000001e-04,
              1.00000000e+00],
            [-1.80000000e+02,  1.80000000e+02, -1.46618928e+01,
              1.00000000e+00]],
    
           [[-1.80000000e+02,  1.80000000e+02, -7.33094638e+00,
              1.00000000e+00],
            [-1.80000000e+02,  1.80000000e+02,  1.94355120e-86,
              1.00000000e+00],
            [-1.80000000e+02,  1.80000000e+02,  7.00000001e-04,
              1.00000000e+00],
            [-1.80000000e+02,  1.80000000e+02, -1.46618928e+01,
              1.00000000e+00]]])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc__mode</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>&lt;U9</div><div class='xr-var-preview xr-preview'>&#x27;bissector&#x27; &#x27;bissector&#x27;</div><input id='attrs-2d93ccc9-a6f3-4ad3-8923-791753dd508a' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-2d93ccc9-a6f3-4ad3-8923-791753dd508a' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-e18a53b0-9fce-43ac-b798-8ea6f4c281f9' class='xr-var-data-in' type='checkbox'><label for='data-e18a53b0-9fce-43ac-b798-8ea6f4c281f9' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;bissector&#x27;, &#x27;bissector&#x27;], dtype=&#x27;&lt;U9&#x27;)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>fourc_orientation_attrs</span></div><div class='xr-var-dims'>(time, dim_11)</div><div class='xr-var-dtype'>&lt;U19</div><div class='xr-var-preview xr-preview'>&#x27;orientation_attrs&#x27; ... &#x27;_hklpy_...</div><input id='attrs-ff331204-25c9-41e3-aeae-c4635b7faed4' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-ff331204-25c9-41e3-aeae-c4635b7faed4' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-969e9a5b-0fee-46b5-83a2-2803bb8c44a7' class='xr-var-data-in' type='checkbox'><label for='data-969e9a5b-0fee-46b5-83a2-2803bb8c44a7' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([[&#x27;orientation_attrs&#x27;, &#x27;geometry_name&#x27;, &#x27;class_name&#x27;, &#x27;UB&#x27;, &#x27;U&#x27;,
            &#x27;ux&#x27;, &#x27;uy&#x27;, &#x27;uz&#x27;, &#x27;energy&#x27;, &#x27;energy_units&#x27;, &#x27;energy_offset&#x27;,
            &#x27;sample_name&#x27;, &#x27;lattice&#x27;, &#x27;lattice_reciprocal&#x27;,
            &#x27;reflections_details&#x27;, &#x27;_pseudos&#x27;, &#x27;_reals&#x27;, &#x27;_constraints&#x27;,
            &#x27;_mode&#x27;, &#x27;diffractometer_name&#x27;, &#x27;_hklpy_version&#x27;],
           [&#x27;orientation_attrs&#x27;, &#x27;geometry_name&#x27;, &#x27;class_name&#x27;, &#x27;UB&#x27;, &#x27;U&#x27;,
            &#x27;ux&#x27;, &#x27;uy&#x27;, &#x27;uz&#x27;, &#x27;energy&#x27;, &#x27;energy_units&#x27;, &#x27;energy_offset&#x27;,
            &#x27;sample_name&#x27;, &#x27;lattice&#x27;, &#x27;lattice_reciprocal&#x27;,
            &#x27;reflections_details&#x27;, &#x27;_pseudos&#x27;, &#x27;_reals&#x27;, &#x27;_constraints&#x27;,
            &#x27;_mode&#x27;, &#x27;diffractometer_name&#x27;, &#x27;_hklpy_version&#x27;]], dtype=&#x27;&lt;U19&#x27;)</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-66ff43e5-d793-49e2-9153-47e59f569c2e' class='xr-section-summary-in' type='checkbox' disabled ><label for='section-66ff43e5-d793-49e2-9153-47e59f569c2e' class='xr-section-summary'  title='Expand/collapse section'>Attributes: <span>(0)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><dl class='xr-attrs'></dl></div></li></ul></div></div>



Show orientation that was saved
-------------------------------

In ``scan_id=3``, orientation information from 4 different
diffractometers was saved with the run. Show what is available from each
of those diffractometers. The columns in the next table are the
diffractometers, the rows are the orientation information saved for
each.

.. code:: ipython3

    roi = run_orientation_info(cat[3])
    pd.DataFrame(roi)




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>fourc</th>
          <th>kappa</th>
          <th>orange</th>
          <th>sixc</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>energy</th>
          <td>8.050922</td>
          <td>8.050922</td>
          <td>8.0</td>
          <td>8.050922</td>
        </tr>
        <tr>
          <th>energy_units</th>
          <td>keV</td>
          <td>keV</td>
          <td>keV</td>
          <td>keV</td>
        </tr>
        <tr>
          <th>energy_offset</th>
          <td>0</td>
          <td>0</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <th>geometry_name</th>
          <td>E4CV</td>
          <td>K4CV</td>
          <td>E4CV</td>
          <td>E6C</td>
        </tr>
        <tr>
          <th>class_name</th>
          <td>Fourc</td>
          <td>Kappa</td>
          <td>Fourc</td>
          <td>Sixc</td>
        </tr>
        <tr>
          <th>sample_name</th>
          <td>silicon</td>
          <td>silicon</td>
          <td>main</td>
          <td>silicon</td>
        </tr>
        <tr>
          <th>lattice</th>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>[1.54, 1.54, 1.54, 90.0, 90.0, 90.0]</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
        </tr>
        <tr>
          <th>lattice_reciprocal</th>
          <td>[1.156906937555034, 1.156906937555034, 1.15690...</td>
          <td>[1.156906937555034, 1.156906937555034, 1.15690...</td>
          <td>[4.079990459207523, 4.079990459207523, 4.07999...</td>
          <td>[1.156906937555034, 1.156906937555034, 1.15690...</td>
        </tr>
        <tr>
          <th>U</th>
          <td>[[-1.2217304763832569e-05, -0.9999999999253688...</td>
          <td>[[-1.7453292519418075e-05, -6.226958714415446e...</td>
          <td>[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, ...</td>
          <td>[[-1.2217304763832569e-05, -1.2217304762008981...</td>
        </tr>
        <tr>
          <th>UB</th>
          <td>[[-1.4134284639502065e-05, -1.1569069374686927...</td>
          <td>[[-2.019183519889215e-05, -7.204011736576005e-...</td>
          <td>[[4.079990459207523, -2.4982736282101165e-16, ...</td>
          <td>[[-1.4134284639502065e-05, -1.4134284637392343...</td>
        </tr>
        <tr>
          <th>reflections_details</th>
          <td>[{'reflection': {'h': 4.0, 'k': 0.0, 'l': 0.0}...</td>
          <td>[{'reflection': {'h': 4.0, 'k': 0.0, 'l': 0.0}...</td>
          <td>[]</td>
          <td>[{'reflection': {'h': 4.0, 'k': 0.0, 'l': 0.0}...</td>
        </tr>
        <tr>
          <th>ux</th>
          <td>-90.0</td>
          <td>19.635305</td>
          <td>0.0</td>
          <td>-45.0</td>
        </tr>
        <tr>
          <th>uy</th>
          <td>0.0</td>
          <td>89.998938</td>
          <td>0.0</td>
          <td>-89.99901</td>
        </tr>
        <tr>
          <th>uz</th>
          <td>90.0007</td>
          <td>160.364695</td>
          <td>0.0</td>
          <td>135.0</td>
        </tr>
        <tr>
          <th>diffractometer_name</th>
          <td>fourc</td>
          <td>kappa</td>
          <td>orange</td>
          <td>sixc</td>
        </tr>
        <tr>
          <th>_hklpy_version</th>
          <td>0.3.16+168.geb1a3db.dirty</td>
          <td>0.3.16+168.geb1a3db.dirty</td>
          <td>0.3.16+168.geb1a3db.dirty</td>
          <td>0.3.16+168.geb1a3db.dirty</td>
        </tr>
        <tr>
          <th>_pseudos</th>
          <td>[h, k, l]</td>
          <td>[h, k, l]</td>
          <td>[h, k, l]</td>
          <td>[h, k, l]</td>
        </tr>
        <tr>
          <th>_reals</th>
          <td>[omega, chi, phi, tth]</td>
          <td>[komega, kappa, kphi, tth]</td>
          <td>[omega, chi, phi, tth]</td>
          <td>[mu, omega, chi, phi, gamma, delta]</td>
        </tr>
        <tr>
          <th>_constraints</th>
          <td>[[-180.0, 180.0, 0.0, 1.0], [-180.0, 180.0, 0....</td>
          <td>[[-180.0, 180.0, 0.0, 1.0], [-180.0, 180.0, 0....</td>
          <td>[[-180.0, 180.0, 0.0, 1.0], [-180.0, 180.0, 0....</td>
          <td>[[-180.0, 180.0, 0.0, 1.0], [-180.0, 180.0, 0....</td>
        </tr>
        <tr>
          <th>_mode</th>
          <td>bissector</td>
          <td>bissector</td>
          <td>bissector</td>
          <td>bissector_vertical</td>
        </tr>
        <tr>
          <th>orientation_attrs</th>
          <td>[orientation_attrs, geometry_name, class_name,...</td>
          <td>[orientation_attrs, geometry_name, class_name,...</td>
          <td>[orientation_attrs, geometry_name, class_name,...</td>
          <td>[orientation_attrs, geometry_name, class_name,...</td>
        </tr>
      </tbody>
    </table>
    </div>



Show runs with orientation information
--------------------------------------

Since a given run (``scan_id``) may have more than one set of
orientation information, corresponding to more than one diffractometer,
report for each when found. Here, extra columns are reported for energy
& units, and the crystal lattice parameters. The names are taken from
the above table. (They must be one of the names in the
``orientation_attrs`` list.)

Use this type of listing to determine which **scan_id** and
**diffractometer_name** has the orientation you wish to recover. If the
``scan_id`` is not unique, identify the run with the **uid** (as a
string, such as ``cat["007abcd"]``).

.. code:: ipython3

    list_orientation_runs(cat, "energy", "energy_units", "lattice")




.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>scan_id</th>
          <th>sample_name</th>
          <th>diffractometer_name</th>
          <th>geometry_name</th>
          <th>energy</th>
          <th>energy_units</th>
          <th>lattice</th>
          <th>uid</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>2</td>
          <td>silicon</td>
          <td>fourc</td>
          <td>E4CV</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>586982a</td>
        </tr>
        <tr>
          <th>1</th>
          <td>3</td>
          <td>silicon</td>
          <td>fourc</td>
          <td>E4CV</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>1a9f4aa</td>
        </tr>
        <tr>
          <th>2</th>
          <td>3</td>
          <td>silicon</td>
          <td>kappa</td>
          <td>K4CV</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>1a9f4aa</td>
        </tr>
        <tr>
          <th>3</th>
          <td>3</td>
          <td>main</td>
          <td>orange</td>
          <td>E4CV</td>
          <td>8.000000</td>
          <td>keV</td>
          <td>[1.54, 1.54, 1.54, 90.0, 90.0, 90.0]</td>
          <td>1a9f4aa</td>
        </tr>
        <tr>
          <th>4</th>
          <td>3</td>
          <td>silicon</td>
          <td>sixc</td>
          <td>E6C</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>1a9f4aa</td>
        </tr>
        <tr>
          <th>5</th>
          <td>5</td>
          <td>silicon</td>
          <td>fourc</td>
          <td>E4CV</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>f12094c</td>
        </tr>
        <tr>
          <th>6</th>
          <td>7</td>
          <td>silicon</td>
          <td>kappa</td>
          <td>K4CV</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>c051b2d</td>
        </tr>
        <tr>
          <th>7</th>
          <td>9</td>
          <td>silicon</td>
          <td>sixc</td>
          <td>E6C</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>f4deb68</td>
        </tr>
        <tr>
          <th>8</th>
          <td>10</td>
          <td>silicon</td>
          <td>fourc</td>
          <td>E4CV</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>6c2937f</td>
        </tr>
        <tr>
          <th>9</th>
          <td>11</td>
          <td>silicon</td>
          <td>fourc</td>
          <td>E4CV</td>
          <td>8.050922</td>
          <td>keV</td>
          <td>[5.431020511, 5.431020511, 5.431020511, 90.0, ...</td>
          <td>9c21e27</td>
        </tr>
      </tbody>
    </table>
    </div>



--------------

Restore orientation information
===============================

This demo will restore the orientation information from a ``fourc`` run
(choosing ``scan_id=2``) to the ``orange`` diffractometer. They have the
same **geometry_name** so the information is compatible.

First, get the orientation information from the chosen run. Show the
information for the ``fourc`` diffractometer.

.. code:: ipython3

    info = run_orientation_info(cat[2])
    
    import pprint
    pprint.pprint(info["fourc"])


.. parsed-literal::

    {'U': [[-1.2217304763832569e-05, -0.9999999999253688, 0.0],
           [0.0, 0.0, 1.0],
           [-0.9999999999253688, 1.2217304763832569e-05, 0.0]],
     'UB': [[-1.4134284639502065e-05, -1.1569069374686927, 7.084098436944218e-17],
            [0.0, 0.0, 1.156906937555034],
            [-1.1569069374686927, 1.4134284639572905e-05, 7.083925341879798e-17]],
     '_constraints': [[-180.0, 180.0, 0.0, 1.0],
                      [-180.0, 180.0, 0.0, 1.0],
                      [-180.0, 180.0, 0.0, 1.0],
                      [-180.0, 180.0, 0.0, 1.0]],
     '_hklpy_version': '0.3.16+168.geb1a3db.dirty',
     '_mode': 'bissector',
     '_pseudos': ['h', 'k', 'l'],
     '_reals': ['omega', 'chi', 'phi', 'tth'],
     'class_name': 'Fourc',
     'diffractometer_name': 'fourc',
     'energy': 8.050921948051947,
     'energy_offset': 0,
     'energy_units': 'keV',
     'geometry_name': 'E4CV',
     'lattice': [5.431020511, 5.431020511, 5.431020511, 90.0, 90.0, 90.0],
     'lattice_reciprocal': [1.156906937555034,
                            1.156906937555034,
                            1.156906937555034,
                            90.00000000000001,
                            90.00000000000001,
                            90.00000000000001],
     'orientation_attrs': ['orientation_attrs',
                           'geometry_name',
                           'class_name',
                           'UB',
                           'U',
                           'ux',
                           'uy',
                           'uz',
                           'energy',
                           'energy_units',
                           'energy_offset',
                           'sample_name',
                           'lattice',
                           'lattice_reciprocal',
                           'reflections_details',
                           '_pseudos',
                           '_reals',
                           '_constraints',
                           '_mode',
                           'diffractometer_name',
                           '_hklpy_version'],
     'reflections_details': [{'flag': 1,
                              'orientation_reflection': True,
                              'position': {'chi': 0.0,
                                           'omega': -145.451,
                                           'phi': 0.0,
                                           'tth': 69.0966},
                              'reflection': {'h': 4.0, 'k': 0.0, 'l': 0.0},
                              'wavelength': 1.54},
                             {'flag': 1,
                              'orientation_reflection': True,
                              'position': {'chi': 0.0,
                                           'omega': -145.451,
                                           'phi': 90.0,
                                           'tth': 69.0966},
                              'reflection': {'h': 0.0, 'k': 4.0, 'l': 0.0},
                              'wavelength': 1.54}],
     'sample_name': 'silicon',
     'ux': -90.0,
     'uy': 0.0,
     'uz': 90.00070000000002}


Earlier, the sample and orientation were setup on the ``fourc`` with
these steps:

.. code:: python

   fourc.energy.put(A_KEV / 1.54)
   a0 = SI_LATTICE_PARAMETER
   fourc.calc.new_sample("silicon", lattice=(a0, a0, a0, 90, 90, 90))
   fourc.calc.sample.compute_UB(
       fourc.calc.sample.add_reflection(4, 0, 0, (-145.451, 0, 0, 69.0966)),
       fourc.calc.sample.add_reflection(0, 4, 0, (-145.451, 0, 90, 69.0966))
   )

We have all the information here to repeat those steps for the
``orange`` diffractometer (same ``E4CV`` geometry).

+-----------------------------------+-----------------------------------+
| term                              | recovered orientation             |
+===================================+===================================+
| energy                            | ``info["fourc"]["energy"]``       |
+-----------------------------------+-----------------------------------+
| sample name                       | ``info["fourc"]["sample_name"]``  |
+-----------------------------------+-----------------------------------+
| sample lattice                    | ``info["fourc"]["lattice"]``      |
+-----------------------------------+-----------------------------------+
| first reflection                  | ``info["fou                       |
|                                   | rc"]["reflections_details"][0]``: |
|                                   | ``["reflection"]`` and            |
|                                   | ``["position"]``                  |
+-----------------------------------+-----------------------------------+
| second reflection                 | ``info["fou                       |
|                                   | rc"]["reflections_details"][1]``: |
|                                   | ``["reflection"]`` and            |
|                                   | ``["position"]``                  |
+-----------------------------------+-----------------------------------+

The energy and sample info are ready to use. Both the constraints and
reflections info will take a bit of reformatting.

Due to issues with how bluesky writes data, the constraints info was
written with all floating point numbers (including the boolean for the
``fit`` parameter).

1. The order of constraints is exactly the order of the ``_reals`` so
   those associations and conversions must be handled.
2. We can’t just use the dictionaries for ``reflection`` and
   ``position`` in ``info`` since order is important and those are
   recovered in alphabetical order. That’s why the ordered lists for
   *pseudo* and *real* positioners have been saved with the orientation
   information. Those lists provide the canonical order for *any*
   diffractometer geometry.

**Before restoring**, need to check the target diffractometer to see if
it already has these settings.

.. code:: ipython3

    print(f"{info['fourc']['energy'] = }")
    print(f"{info['fourc']['energy_units'] = }")
    print(f"{info['fourc']['energy_offset'] = }")
    print(f"{orange.energy.get() = }")
    print(f"{orange.energy_units.get() = }")
    print(f"{orange.energy_offset.get() = }")
    print()
    print(f"{info['fourc']['sample_name'] = }")
    print(f"{list(orange.calc._samples.keys()) = }")
    print()
    print(f"{orange.calc._samples = }")


.. parsed-literal::

    info['fourc']['energy'] = 8.050921948051947
    info['fourc']['energy_units'] = 'keV'
    info['fourc']['energy_offset'] = 0
    orange.energy.get() = 8.0
    orange.energy_units.get() = 'keV'
    orange.energy_offset.get() = 0
    
    info['fourc']['sample_name'] = 'silicon'
    list(orange.calc._samples.keys()) = ['main']
    
    orange.calc._samples = {'main': HklSample(name='main', lattice=LatticeTuple(a=1.54, b=1.54, c=1.54, alpha=90.0, beta=90.0, gamma=90.0), ux=Parameter(name='None (internally: ux)', limits=(min=-180.0, max=180.0), value=0.0, fit=True, inverted=False, units='Degree'), uy=Parameter(name='None (internally: uy)', limits=(min=-180.0, max=180.0), value=0.0, fit=True, inverted=False, units='Degree'), uz=Parameter(name='None (internally: uz)', limits=(min=-180.0, max=180.0), value=0.0, fit=True, inverted=False, units='Degree'), U=array([[1., 0., 0.],
           [0., 1., 0.],
           [0., 0., 1.]]), UB=array([[ 4.07999046e+00, -2.49827363e-16, -2.49827363e-16],
           [ 0.00000000e+00,  4.07999046e+00, -2.49827363e-16],
           [ 0.00000000e+00,  0.00000000e+00,  4.07999046e+00]]), reflections=[])}


We need to change the energy (units and offset do not need to be
changed), create a new sample, define the two reflections, then compute
**UB**. Then compare that computed **UB** with the recovered value.

Restore the recovered ``fourc`` orientation into ``orange``
-----------------------------------------------------------

.. code:: ipython3

    from hkl import restore_orientation
    orange = Fourc("", name="orange")  # TODO: remove this line before publishing
    restore_orientation(info["fourc"], orange)

Compare the **UB** matrices. (Convert the recovered **UB** matrix to a
numpy array to match the type in the diffractometer. Expect ``True`` in
all cells of the 3x3 matrix.)

.. code:: ipython3

    print(f'{np.array(info["fourc"]["UB"]) = }')
    print(f"{orange.UB.get() = }")
    # finally, compare the two matrices cell by cell
    np.array(info["fourc"]["UB"]) == orange.UB.get()


.. parsed-literal::

    np.array(info["fourc"]["UB"]) = array([[-1.41342846e-05, -1.15690694e+00,  7.08409844e-17],
           [ 0.00000000e+00,  0.00000000e+00,  1.15690694e+00],
           [-1.15690694e+00,  1.41342846e-05,  7.08392534e-17]])
    orange.UB.get() = array([[-1.41342846e-05, -1.15690694e+00,  7.08409844e-17],
           [ 0.00000000e+00,  0.00000000e+00,  1.15690694e+00],
           [-1.15690694e+00,  1.41342846e-05,  7.08392534e-17]])




.. parsed-literal::

    array([[ True,  True,  True],
           [ True,  True,  True],
           [ True,  True,  True]])



.. code:: ipython3

    orange.pa()


.. parsed-literal::

    ===================== ===========================================================================
    term                  value                                                                      
    ===================== ===========================================================================
    diffractometer        orange                                                                     
    geometry              E4CV                                                                       
    class                 Fourc                                                                      
    energy (keV)          8.05092                                                                    
    wavelength (angstrom) 1.54000                                                                    
    calc engine           hkl                                                                        
    mode                  bissector                                                                  
    positions             ===== =======                                                              
                          name  value                                                                
                          ===== =======                                                              
                          omega 0.00000                                                              
                          chi   0.00000                                                              
                          phi   0.00000                                                              
                          tth   0.00000                                                              
                          ===== =======                                                              
    constraints           ===== ========= ========== ===== ====                                      
                          axis  low_limit high_limit value fit                                       
                          ===== ========= ========== ===== ====                                      
                          omega -180.0    180.0      0.0   True                                      
                          chi   -180.0    180.0      0.0   True                                      
                          phi   -180.0    180.0      0.0   True                                      
                          tth   -180.0    180.0      0.0   True                                      
                          ===== ========= ========== ===== ====                                      
    sample: silicon       ================= =========================================================
                          term              value                                                    
                          ================= =========================================================
                          unit cell edges   a=5.431020511, b=5.431020511, c=5.431020511              
                          unit cell angles  alpha=90.0, beta=90.0, gamma=90.0                        
                          ref 1 (hkl)       h=4.0, k=0.0, l=0.0                                      
                          ref 1 positioners omega=-145.45100, chi=0.00000, phi=0.00000, tth=69.09660 
                          ref 2 (hkl)       h=0.0, k=4.0, l=0.0                                      
                          ref 2 positioners omega=-145.45100, chi=0.00000, phi=90.00000, tth=69.09660
                          [U]               [[-1.22173048e-05 -1.00000000e+00  0.00000000e+00]       
                                             [ 0.00000000e+00  0.00000000e+00  1.00000000e+00]       
                                             [-1.00000000e+00  1.22173048e-05  0.00000000e+00]]      
                          [UB]              [[-1.41342846e-05 -1.15690694e+00  7.08409844e-17]       
                                             [ 0.00000000e+00  0.00000000e+00  1.15690694e+00]       
                                             [-1.15690694e+00  1.41342846e-05  7.08392534e-17]]      
                          ================= =========================================================
    ===================== ===========================================================================
    




.. parsed-literal::

    <pyRestTable.rest_table.Table at 0x7fe5a94e6310>



Try to restore the recovered ``fourc`` orientation in ``kappa``
---------------------------------------------------------------

Try to share a recovered orientation from ``fourc``, ``scan_id=2`` with
the ``kappa`` diffractometer.

.. code:: ipython3

    try:
        info = run_orientation_info(cat[2])
        restore_orientation(info["fourc"], kappa)
    except ValueError as exc:
        print(f"{exc = }")


.. parsed-literal::

    exc = ValueError('Geometries do not match: Orientation=E4CV, kappa=K4CV, will not restore.')


Restore is not be possible since the geometries are not identical. (To
avoid stopping the notebook with an exception here, we used a
``try..except`` clause.)

Try to create a sample when it already exists
---------------------------------------------

Then, try to restore the sample and lattice when they already exist.

.. code:: ipython3

    from hkl import restore_sample
    
    print(f"{kappa.sample_name.get() = }")
    try:
        info = run_orientation_info(cat[2])
        restore_sample(info["fourc"], kappa)
        kappa.wh()
    except Exception as exc:
        print(f"{exc = }")


.. parsed-literal::

    kappa.sample_name.get() = 'silicon'
    exc = ValueError("Sample 'silicon' already exists in kappa.")


Restore the energy
------------------

.. code:: ipython3

    from hkl import restore_energy
    
    # make a new kappa, then restore the sample
    kappa = Kappa("", name="kappa")
    print(f"{kappa.sample_name.get() = }")
    try:
        info = run_orientation_info(cat[2])
        restore_energy(info["fourc"], kappa)
        restore_sample(info["fourc"], kappa)
        kappa.wh()
    except Exception as exc:
        print(f"{exc = }")


.. parsed-literal::

    kappa.sample_name.get() = 'main'
    ===================== ========= =========
    term                  value     axis_type
    ===================== ========= =========
    diffractometer        kappa              
    sample name           silicon            
    energy (keV)          8.05092            
    wavelength (angstrom) 1.54000            
    calc engine           hkl                
    mode                  bissector          
    h                     0.0       pseudo   
    k                     0.0       pseudo   
    l                     0.0       pseudo   
    komega                0         real     
    kappa                 0         real     
    kphi                  0         real     
    tth                   0         real     
    ===================== ========= =========
    

