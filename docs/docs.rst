Rebuild the Docs!
=================

To rebuild the docs, first ensure the required packages are installed:

.. code-block:: bash

    pip install Sphinx sphinx_rtd_theme

Once these are installed, navigate to the ``/docs`` folder of the repo and build the docs with commands:

.. code-block:: bash

    sphinx-apidoc -o source/ ../src --force
    make html

If you have an installation of LaTeX on your machine, you can also generate a pdf with:

.. code-block:: bash

    make latexpdf
