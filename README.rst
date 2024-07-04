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

Due to a recent change in the UNFCCC's API, the UNFCCCApiReader class is
**not functional** any more in standard environments. To continue to access the data,
you have two options:

1. Use the new ZenodoReader. It provides access using the `query` function like the
   UNFCCCApiReader, but only supports querying for a full dataset with all data. It
   relies on our `data package <https://doi.org/10.5281/zenodo.4198782>`_, which we
   update regularly; however, the data is naturally not as recent as querying from
   the API directly.
2. Run your functions in an environment which is not blocked by the UNFCCC DI API.
   According to our tests, Azure virtual machines work, as well as github hosted
   runners, with the exception of Mac OS runners.


Features
--------

* High-level API to query all information for a given party.
* Low-level API to selectively query information with the same resolution as in the
  UNFCCC web query tool.

Citation
--------
If you use this library and want to cite it, please cite it as:

Mika Pflüger, Daniel Huppmann & Johannes Gütschow. (2024-01-08).
pik-primap/unfccc_di_api: Version 4.0.3.
Zenodo. https://doi.org/10.5281/zenodo.10471122

Data package
------------
If you just want all the data in CSV and parquet format (suitable for reading with
pandas), look at our `data package <https://doi.org/10.5281/zenodo.4198782>`_.

CI status and other links
-------------------------

.. image:: https://results.pre-commit.ci/badge/github/pik-primap/unfccc_di_api/main.svg
   :target: https://results.pre-commit.ci/latest/github/pik-primap/unfccc_di_api/main
   :alt: pre-commit.ci status
