.. gitWebhook documentation master file, created by
   sphinx-quickstart on Thu Apr 18 14:07:22 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to gitWebhook's documentation!
======================================

gitWebhook is a Python package that provides Flask blueprints for creating webhooks for various git services.
As of right now GitHub, GitLab and Gitea webhooks are supported.
The package provides these blueprints as subclasses of Flask's Blueprint class, so they can be easily integrated into existing Flask applications, and expanded with custom behavior.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

   tutorials

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
