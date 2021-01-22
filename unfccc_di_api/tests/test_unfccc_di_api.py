#!/usr/bin/env python

"""Tests for `unfccc_di_api` package."""

import pytest

from unfccc_di_api import UNFCCCApiReader, UNFCCCSingleCategoryApiReader


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def _smoketest_non_annex_one():
    r = UNFCCCSingleCategoryApiReader(party_category="nonAnnexOne")
    r.query(party_codes=["MMR"])


def _smoketest_annex_one():
    r = UNFCCCSingleCategoryApiReader(party_category="annexOne")
    r.query(party_codes=["DEU"], gases=["N₂O"])


def _smoketest_unified():
    r = UNFCCCApiReader()
    r.query(party_code="AFG")
