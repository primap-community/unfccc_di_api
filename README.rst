=============
UNFCCC DI API
=============


.. image:: https://img.shields.io/pypi/v/unfccc_di_api.svg
        :target: https://pypi.python.org/pypi/unfccc_di_api
        :alt: PyPI release

.. image:: https://readthedocs.org/projects/unfccc-di-api/badge/?version=main
        :target: https://unfccc-di-api.readthedocs.io/en/main/
        :alt: Documentation

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.4457483.svg
   :target: https://doi.org/10.5281/zenodo.4457483


Python wrapper around the `Flexible Query API <https://di.unfccc.int/flex_annex1>`_ of
the UNFCCC.


* Free software: Apache Software License 2.0
* Documentation: https://unfccc-di-api.readthedocs.io.

Warning
-------

Due to a recent change in the UNFCCC's API, this package is **not** functional
anymore. We are looking for a fix, but can't promise anything.


Features
--------

* High-level API to query all information for a given party.
* Low-level API to selectively query information with the same resolution as in the
  UNFCCC web query tool.

Citation
--------
If you use this library and want to cite it, please cite it as:

Mika Pflüger, Daniel Huppmann & Johannes Gütschow. (2022-12-13).
pik-primap/unfccc_di_api: unfccc_di_api version 3.0.2.
Zenodo. https://doi.org/10.5281/zenodo.7431899

Data package
------------
If you just want all the data in CSV and parquet format (suitable for reading with
pandas), look at our `data package <https://doi.org/10.5281/zenodo.4198782>`_.

CI status and other links
-------------------------

.. image:: https://results.pre-commit.ci/badge/github/pik-primap/unfccc_di_api/main.svg
   :target: https://results.pre-commit.ci/latest/github/pik-primap/unfccc_di_api/main
   :alt: pre-commit.ci status
