
Release Notes
=============

.. raw:: html

   <div style="zoom: 0.8;-moz-transform: scale(0.8);">

.. include:: badges.md
   :parser: myst_parser.sphinx_

.. raw:: html

   </div>

----

Version 0.0.7
^^^^^^^^^^^^^

 - Fix: multiple replace behavior (e.g., with cli, presets, env vars)


Version 0.0.6
^^^^^^^^^^^^^

 - Fix: replace behavior for type differences



Version 0.0.5
^^^^^^^^^^^^^

 - Feature: added direct/python object interpolation
 - Removed: return type option (can now be done via direct/python object interpolation)
 - Packages: added conda forge package
 - Docs: fixed api formating 
 - CI: added pre-commit



Version 0.0.4
^^^^^^^^^^^^^

 - ConfigReader and build_config can now be imported directly form dicfg
 - name argument in ConfigReader is now mandatory
 - renamed configs_name to main_config_path
 - configs folder is now inferred from main_config_path
 - update readme with absolute path to image
 - refactored github workflows



Version 0.0.3
^^^^^^^^^^^^^

 - Added environment interpolation feature
 - Fixed bug when using multiple object interpolations
 - Automatic release via github actions
 - Updated docs


Version 0.0.2
^^^^^^^^^^^^^

 - Refactoring
 - Changed ConfigReader class calls to method calls
 - Extracted build function from ObjectFactory 
 - Added python and os versions tests
 - Updated docs


Version 0.0.1
^^^^^^^^^^^^^

 - Documentation online
 - Tests online



.. toctree::
  :hidden:

  self