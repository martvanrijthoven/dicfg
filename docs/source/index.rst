:html_theme.sidebar_secondary.remove:

.. |nbsp| unicode:: 0xA0 
   :trim:

.. raw:: html
   
   <div style="display: none;">

Documentation
=============

.. raw:: html

   </div>
   <div style="display: block;">
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

- Loading of predefined config files (YAML and JSON).
- Overwrite config with user_config files/dictionaries, command line interface, and/or presets.
- Customize merge/replace behavior for dictionaries and lists.
- Interpolation support for sub-config files, config variables, environment variables, and python objects.
- Build object instances directly in the config.
- Dependency injection via object interpolation: configure all object dependencies directly in the config.
- Use object attribute interpolation for referencing object attributes directly in the config file.



----


.. toctree::
  :hidden:

  getstarted
  userguide/index
  ./api
  releasenotes

.. raw:: html

   </div>

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