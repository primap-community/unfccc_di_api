=========
Changelog
=========

Unreleased
----------

* Fix pre-commit config for newer mypy type checking versions.
* Raise a more informative NoDataError (subclass of KeyError) instead of a generic
  KeyError when a query result is empty.

2.0.1 (2021-04-23)
------------------

* Change build system.

2.0.0 (2021-02-09)
------------------

* Accept ASCII format for ``gases`` when querying data
  and return gases & units normalized to ASCII (optional), thanks to Daniel Huppmann.
  Note that gases and units are normalized to ASCII by default, if you need the old
  behaviour for compatibility reasons, pass ``normalize_gas_names=False`` to your
  ``query()`` calls.

1.1.1 (2021-02-08)
------------------

* Include ipython notebooks and CHANGELOG in release tarballs.

1.1.0 (2021-01-25)
------------------

* Add a useful error message when querying for unknown parties, thanks to
  Daniel Huppmann.

1.0.0 (2021-01-22)
------------------

* Add continuous integration using GitHub actions.
* Add tests.
* Add usage documentation in notebook format.
* Documentation fixes.

0.1.0 (2021-01-22)
------------------

* First release on PyPI.
* Convert API wrapper into standalone Python package.
