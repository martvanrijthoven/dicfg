:html_theme.sidebar_secondary.remove:

.. |nbsp| unicode:: 0xA0 
   :trim:

.. raw:: html

   <div style="visibility: hidden;">

Documentation
=============

.. raw:: html

   </div>

   <div style="width:50%;">
   <img src="_static/logo.svg" class="logo__image only-light" alt="Logo image">
   <img src="_static/logo-dark.svg" class="logo__image only-dark" alt="Logo image">
   

.. raw:: html

   </div>
   <div style="visibility: hidden;">

----

.. raw:: html

   </div>

.. include:: badges.md
   :parser: myst_parser.sphinx_

.. grid:: 1

    .. grid-item::
        :class: sd-text-white sd-bg-primary sd-pt-3
        
        Dicfg is a **configuration system** that supports **dependency injection** via **object interpolation** in config files.
        

.. grid:: 1 1 3 3

  .. grid-item-card:: :octicon:`rocket;2em;sd-text-info;` |nbsp| |nbsp| |nbsp| Get Started with Dicfg
     :link: getstarted.html

     +++

  .. grid-item-card:: :octicon:`book;2em;sd-text-info` |nbsp| |nbsp| |nbsp| User Guide
     :link: userguide/index.html

     +++      

  .. grid-item-card:: :octicon:`code;2em;sd-text-info` |nbsp| |nbsp| |nbsp| API Reference
     :link: api.html

     +++


Main Features
^^^^^^^^^^^^^

- Loading of predefined config files (YAML and JSON)
- Overwrite config with user_config files/dictionaries, command line interface, and/or presets.
- Customize merge/replace behavior for dictionaries and lists.
- Config interpolation support for subconfig files, config variables, and environment variables.
- Build python types and instances from objects directly in the config.
- Dependency inject via object interpolation: configure all object dependencies directly in the config
- Object attribute interpolation: referencing objects attributes directly in the config file

----

.. toctree::
  :hidden:

  getstarted
  userguide/index
  ./api
  releasenotes



.. .. raw:: html

..     <div class="container">
..     <div class="row">
..         <div class="col">
..             <div class="card">
..             <img class="mx-auto" style="width:4rem; height:auto;" src="./_static/injection-up.png" alt="Card image cap">
..             <a href="#" class="btn btn-primary">Get started</a>
..             </div>

..         </div>
..         <div class="col">

..             <div class="card">
..             <img class="mx-auto" style="width:4rem; height:auto;" src="./_static/injection-up.png" alt="Card image cap">
..             <a href="#" class="btn btn-primary">User Guide</a>
..             </div>

..         </div>
..         <div class="col">

..             <div class="card">
..             <img class="mx-auto" style="width:4rem; height:auto;" src="./_static/injection-up.png" alt="Card image cap">
..             <a href="#" class="btn btn-primary">API</a>
..             </div>

..         </div>
..     </div>
..     </div>