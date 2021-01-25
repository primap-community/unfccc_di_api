"""The API provided by the UNFCCC distinguishes between parties listed in Annex I
and the other parties, likely because the reporting requirements for Annex I parties
and non-Annex I parties differ substantially.
This library provides a wrapper class :py:class:`UNFCCCApiReader` which unifies both
APIs so that you don't have to worry about the status of a particular party. However,
if you want to filter for specific variables and only query a subset of the data,
you have to use the individual API objects for Annex I and non-Annex I parties,
which are available at :py:attr:`UNFCCCApiReader.annex_one_reader` and
:py:attr:`UNFCCCApiReader.non_annex_one_reader`, respectively."""

__author__ = """Mika Pflüger"""
__email__ = "mika.pflueger@pik-potsdam.de"
__version__ = "1.1.0"

from .unfccc_di_api import UNFCCCApiReader, UNFCCCSingleCategoryApiReader

__all__ = ["UNFCCCApiReader", "UNFCCCSingleCategoryApiReader"]
