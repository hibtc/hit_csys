CHANGELOG
~~~~~~~~~

20.11.0
-------
Date: 25.01.2020

- debug auto load model feature
  
20.1.0
------
Date: 25.01.2020

- revisit auto load model feature implementation

19.8.0
------
Date: 19.08.2019

- add auto load model feature
  
19.5.1
------
Date: 13.05.2019

- make parameter lookup case-insensitive again (was accidentally made
  case-sensitive when changing order of parameters)


19.5.0
------
Date: 09.05.2019

- add knobs for remaining MEFI params
- add method to read all/multiple parameters at once
  (required by madgui 19.5.1)
- fix outdated code in menuitem for editting model init conditions


19.4.1
------
Date: 30.04.2019

- suppress irritating error message about 'gantry_angle' when uploading params
- warn if the model gantry_angle differs from the active MEFI
- don't modify the user's model when initializing stub backend


19.4.0
------
Date: 13.04.2019

- simplifications in travis configuration and setup.cfg


19.3.0
------
Date: 21.03.2019

- let the stub work with its own independent model (for simulating a backend)
- add dialog to edit our model
- requires madgui 19.3.2
- fix py2 compatibility issue in beamoptikdll.py (again…)
- require importlib_resources
- update package name
- cleanup in setup script


19.01.0
-------
Date: 19.01.2019

- rename package to ``hit_acs``
- fix another error in ``SetNewValueCallback`` due to using missing ``.value``
  attribute on string parameter
- fix ``SetNewValueCallback`` string parameter type: ANSI string
- use ctypes argtypes declarations for DLL functions
- improve startup performance by cleaning up csv parser logic
- keep units as strings (requires newer madgui)
- avoid unused parameter grouping by element
- fix potential startup exception if MEFI is given in settings but VAcc is not
- simplify ``read_monitor`` implementation
- set the beamoptikdll as *permanent* variable into the user namespace as
  simplification (i.e. not removing the variable after disconnecting)
- improve some internal variable names
- change beamoptikdll variable name in user namespace (``beamoptikdll``)
- the ``load_library`` classmethod has been removed, in favor of letting the
  the normal ``BeamOptikDLL`` constructor now load the DLL directly
- special case ``GetLastFloatValueSD`` for the MIT variant
- remove two lonely warnings
- return the IID integer value (not the ``ctypes.c_int`` instance) from
  ``GetInterfaceInstance``
- don't log ``GetFloatValueSD`` calls for now (temporary, to avoid too much
  noise in debug log)


18.12.0
-------
Date: 11.12.2018

- fix exception in ``OnlineBackend.__init__`` due to missing parenthesis
- keep a reference to the ctypes callback for ``SetNewValueCallback``, to
  prevent garbage collection
- fix incorrect parameter type (pointer to pointer) for
  ``SetNewValueCallback``
- allow removing the callback by passing None


18.10.0
-------
Date: 18.10.2018

Now in calver_ (calendaric versioning) ``YY.MM.patch`` since this better fits
the nature of madgui development and is I believe more useful for end-users.

.. _calver: https://calver.org/

- fix TypeError during MEFI initialization
- jitter SD values on retrieval, periodically (like shots)
- use gaussian jitter for monitor readouts
- take care of settings menu [madgui >= 2018.10.18]
- aberrate magnet strengths only explicitly
- add menu options for internal settings
- add menuitems for loading readouts/strengths
- load/save more stub settings
- aberrate only ax/kL values, gaussian distribution
- disturb beam *widths* using gamma distribution
- adapt to updated madgui module qualnames in madgui 2018.10.18
- adapt to changes in new madgui Plugin API (-> Backend)
- getting passed Session object instead of mainwindow now
- safeguard against invalid paths - fixes ValueError on exit
- fix the test backend when no window is present
- add automatic sanity checks (missing imports, syntax errors, etc)
- add automatic style checks and fix several style issues
- automatically upload releases to PyPI
- add debug trace log for the real online dll


0.13.0
------
Date: 24.07.2018

- retrieve variant from config (autodetection was a failure)
- load config settings from new ``settings`` argument (madgui 1.14.0)
- reselect previous vacc/mefi on startup
- suppress exception when reading/writing missing parameters
- update import path for read_str_file from madgui


0.12.0
------
Date: 15.07.2018

- in test stub: use gantry angle from param list
- fix outdated run.py
- for ExecuteChanges set ``options`` parameter default as ``CalcDif``
- adapt beamoptikdll module for Marburg variant
- simplify the test stub module (directly mocks BeamOptikDLL class now,
  instead of the ctypes backend)


0.11.0
------
Date: 25.06.2018

- revert "Automatically read beam and strengths on connect", it was broken
  because usually there will be no MEFI combination selected at this point
- cleanup some unnecessary imports
- fix NameError in ``csv_unicode_reader`` on py2
- fix ``importlib_resources`` import and use within ``util`` as well
- remove obsolete config file and YAML dependency with it
- make the ``frame`` argument optional (useful for testing)
- adapt to backward incompatible changes in ``madgui 1.0.2``: ``frame.model``
  is now a ``Boxed`` object!
- pass offsets as parameters to ``HitOnlineControl`` and fake DLL
  (dependency injection!)
- remove more knowledge from ``HitOnlineControl``
- can now remove ``control`` member from fake DLL
- remove ``.instances`` (~IID) logic in fake DLL
- add methods to load parameters and SD values from disk
- update fake SD values on "Execute" rather than on every call


0.10.0
------
Date: 01.06.2018

- add beam parameters for test stub
- automatically read beam and strengths on connect

0.9.0
-----
Date: 31.05.2018

- fully simplify knobs to being only var names, all conversions are now done
  by using appropriate expressions in the model!!

0.8.0
-----
Date: 16.04.2018

- adapt to changes in madgui ``1.9.0`` API
- simplify ``get_knob`` logic significantly
- remove support for inserted kickers into SBENDs (now modelled as ``K0 !=
  ANGLE/L``)
- fix an error in stub with 32bit
- flip monitor X position to convert from HIT to MAD-X coordinate system (HIT
  uses a left-handed system in HEBT!)
- discard ``-9999`` records from monitors
- remove setuptools entrypoint for madgui, must now be loaded manually using
  the ``onload`` handler
- expose ``dll`` variable to user shell
- read and add offsets to MWPC measurements

0.7.0
-----
Date: 25.03.2018

- update madgui plugin to new unit handling in madgui
- compatible with madgui 1.8.0, hit_models 0.8.0

0.6.0
-----
Date: 02.03.2018

- fix knob access for skew quadrupoles
- compatible with madgui 1.7.1, hit_models 0.7.0

0.5.0
-----
Date: 26.01.2018

- update to madqt 0.0.6: unification of workspace/segment -> model

0.4.0
-----
Date: 24.01.2018

- 64bit support
- add win32 and qt standalone modes
- port to madqt
- initialize strengths/monitors from current model instead of using the
  example values in the parameter list (which would often lead to crashes)
- renamed package
- finally implement SetNewValueCallback (untested)
- massive simplification of the madqt interface (knobs API)
- can query beam parameters
- ship DVM parameter list with the package itself
- always load DVM parameters from CSV (no more YAML)
- can guess correct parameter names more reliably, based on several clues
