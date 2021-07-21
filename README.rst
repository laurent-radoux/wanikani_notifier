=================
WaniKani Notifier
=================


.. image:: https://img.shields.io/pypi/v/wanikani_notifier.svg
        :target: https://pypi.python.org/pypi/wanikani_notifier

.. image:: https://img.shields.io/travis/laurent-radoux/wanikani_notifier.svg
        :target: https://travis-ci.com/laurent-radoux/wanikani_notifier

.. image:: https://readthedocs.org/projects/wanikani-notifier/badge/?version=latest
        :target: https://wanikani-notifier.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Notifies a WaniKani user for new reviews to do.


* Free software: MIT license
* Documentation: https://wanikani-notifier.readthedocs.io.


Features
--------

* Fetches new assignments available as of the start of the hour at which the call is performed
* Sends a notification via PushSafer whenever new reviews and/or lessons are available
* Optionally specifies the time before which assignments are ignored

  * Helps preventing many notifications once at least one assignment is available

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
