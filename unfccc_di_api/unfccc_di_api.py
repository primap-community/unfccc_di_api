__license__ = """
Copyright 2020 Potsdam-Institut für Klimafolgenforschung e.V.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import itertools
import logging
import typing

import pandas as pd
import requests
import treelib


class UNFCCCApiReader:
    """Provides simplified unified access to the Flexible Query API of the UNFCCC data
    access for all parties.

    Essentially encapsulates https://di.unfccc.int/flex_non_annex1 and
    https://di.unfccc.int/flex_annex1 .

    Attributes
    ----------
    parties : pandas.DataFrame
        All parties, with their ID, code, and full name.
    gases : pandas.DataFrame
        The available gases and their IDs.
    annex_one_reader : UNFCCCSingleCategoryApiReader
        The API reader object for Annex I parties.
    non_annex_one_reader : UNFCCCSingleCategoryApiReader
        The API reader object for non-Annex I parties.
    """

    def __init__(self, *, base_url="https://di.unfccc.int/api/"):
        """
        Parameters
        ----------
        base_url : str
            Location of the UNFCCC api.
        """
        self.annex_one_reader = UNFCCCSingleCategoryApiReader(
            party_category="annexOne", base_url=base_url
        )
        self.non_annex_one_reader = UNFCCCSingleCategoryApiReader(
            party_category="nonAnnexOne", base_url=base_url
        )

        self.parties = pd.concat(
            [self.annex_one_reader.parties, self.non_annex_one_reader.parties]
        ).sort_index()
        self.gases = pd.concat(
            [self.annex_one_reader.gases, self.non_annex_one_reader.gases]
        ).sort_index()
        # drop duplicated gases
        self.gases = self.gases[~self.gases.index.duplicated(keep="first")]

    def query(
        self,
        *,
        party_code: str,
        gases: typing.Union[typing.List[str], None] = None,
        progress: bool = False,
    ) -> pd.DataFrame:
        """Query the UNFCCC for data.

        Parameters
        ----------
        party_code : str
            ISO code of a party for which to query. For possible values, see
            :py:attr:`~UNFCCCApiReader.parties`.
        gases : list of str, optional
            Limit the query to these gases. For possible values, see
            :py:attr:`~UNFCCCApiReader.gases`. Default: query for all gases.
        progress : bool
            Display a progress bar. Requires the :py:mod:`tqdm` library. Default: false.

        Returns
        -------
        pandas.DataFrame

        Notes
        -----
        If you need more fine-grained control over which variables to query for,
        including restricting the query to specific measures, categories, or
        classifications or to query for multiple parties at once, please see the
        corresponding methods :py:meth:`UNFCCCApiReader.annex_one_reader.query` and
        :py:meth:`UNFCCCApiReader.non_annex_one_reader.query`.
        """
        if party_code in self.annex_one_reader.parties["code"].values:
            reader = self.annex_one_reader
        elif party_code in self.non_annex_one_reader.parties["code"].values:
            reader = self.non_annex_one_reader
        else:
            help = "try `UNFCCCApiReader().parties` for a list of valid codes"
            raise ValueError(f"Unknown party `{party_code}`, {help}!")

        return reader.query(party_codes=[party_code], gases=gases, progress=progress)


class UNFCCCSingleCategoryApiReader:
    """Provides access to the Flexible Query API of the UNFCCC data access for a single
    category, either annexOne or nonAnnexOne.

    Use this class if you want to do fine-grained queries for specific measures,
    categories, years, or classifications.

    Essentially encapsulates https://di.unfccc.int/flex_non_annex1
    or https://di.unfccc.int/flex_annex1 .

    Attributes
    ----------
    parties : pandas.DataFrame
        All parties in this category, with their ID, code, and full name.
    years : pandas.DataFrame
        All years for which data is available, mapping the ID to the year.
    category_tree : treelib.Tree
        The available categories and their relationships. Use
        :py:meth:`~UNFCCCSingleCategoryApiReader.show_category_hierarchy` for displaying
        the category tree.
    classifications : pandas.DataFrame
        All classifications and their IDs.
    measure_tree : treelib.Tree
        The available measures and their relationsips. Use
        :py:meth:`~UNFCCCSingleCategoryApiReader.show_measure_hierarchy` for displaying
        the measure tree.
    gases : pandas.DataFrame
        The available gases and their IDs.
    units : pandas.DataFrame
        The available units and their IDs.
    conversion_factors : pandas.DataFrame
        Conversion factors between units for the specified gases.
    variables : pandas.DataFrame
        The available variables with the corresponding category, classification,
        measure, gas, and unit.
    """

    def __init__(self, *, party_category: str, base_url="https://di.unfccc.int/api/"):
        """
        Parameters
        ----------
        party_category : str
           Either ``nonAnnexOne`` or ``annexOne``.
        base_url : str
           Location of the UNFCCC api.
        """
        self.base_url = base_url

        parties_raw = self._get(f"parties/{party_category}")
        parties_entries = []
        for entry in parties_raw:
            if entry["categoryCode"] == party_category and entry["name"] != "Groups":
                parties_entries.append(entry["parties"])
        if not parties_entries:
            raise ValueError(
                f"Could not find parties for the party_category {party_category!r}."
            )

        self.parties = (
            pd.DataFrame(itertools.chain(*parties_entries))
            .set_index("id")
            .sort_index()
            .drop_duplicates()
        )
        self._parties_dict = dict(self.parties["code"])
        self.years = (
            pd.DataFrame(self._get("years/single")[party_category])
            .set_index("id")
            .sort_index()
        )
        self._years_dict = dict(self.years["name"])
        for i in self._years_dict:
            if self._years_dict[i].startswith("Last Inventory Year"):
                self._years_dict[i] = self._years_dict[i][-5:-1]

        # note that category names are not unique!
        category_hierarchy = self._get("dimension-instances/category")[party_category][
            0
        ]
        self.category_tree = self._walk(category_hierarchy)

        self.classifications = (
            pd.DataFrame(
                self._get("dimension-instances/classification")[party_category]
            )
            .set_index("id")
            .sort_index()
        )
        self._classifications_dict = dict(self.classifications["name"])

        measure_hierarchy = self._get("dimension-instances/measure")[party_category]
        self.measure_tree = treelib.Tree()
        sr = self.measure_tree.create_node("__root__")
        for i in range(len(measure_hierarchy)):
            self._walk(measure_hierarchy[i], tree=self.measure_tree, parent=sr)

        self.gases = (
            pd.DataFrame(self._get("dimension-instances/gas")[party_category])
            .set_index("id")
            .sort_index()
        )
        self._gases_dict = dict(self.gases["name"])

        unit_info = self._get("conversion/fq")
        self.units = pd.DataFrame(unit_info["units"]).set_index("id").sort_index()
        self._units_dict = dict(self.units["name"])
        self.conversion_factors = pd.DataFrame(unit_info[party_category])

        # variable IDs are not unique, because category names are not unique
        # just give up and delete the duplicated ones
        variables_raw = self._get(f"variables/fq/{party_category}")
        self.variables = (
            pd.DataFrame(variables_raw).set_index("variableId").sort_index()
        )
        self.variables = self.variables[~self.variables.index.duplicated(keep="first")]
        self._variables_dict = {x["variableId"]: x for x in variables_raw}

    def _flexible_query(
        self,
        *,
        variable_ids: typing.List[int],
        party_ids: typing.List[int],
        year_ids: typing.List[int],
    ) -> typing.List[dict]:

        if len(variable_ids) > 3000:
            logging.warning(
                "Your query parameters lead to a lot of variables selected at once. "
                "If the query fails, try restricting your query more."
            )

        return self._post(
            "records/flexible-queries",
            json={
                "variableIds": variable_ids,
                "partyIds": party_ids,
                "yearIds": year_ids,
            },
        )

    def query(
        self,
        *,
        party_codes: typing.List[str],
        category_ids: typing.Union[None, typing.List[int]] = None,
        classifications: typing.Union[None, typing.List[str]] = None,
        measure_ids: typing.Union[None, typing.List[int]] = None,
        gases: typing.Union[None, typing.List[str]] = None,
        batch_size: int = 1000,
        progress: bool = False,
    ) -> pd.DataFrame:
        """Query the UNFCCC for data.

        Parameters
        ----------
        party_codes : list of str
            List of ISO codes of parties for which to query. For possible values, see
            :py:attr:`~UNFCCCSingleCategoryApiReader.parties`.
        category_ids : list of int, optional
            List of category IDs to query. For possible values, see
            :py:meth:`~UNFCCCSingleCategoryApiReader.show_category_hierarchy()`.
            Default: query for all categories.
        classifications : list of str, optional
            List of classifications to query. For possible values, see
            :py:attr:`~UNFCCCSingleCategoryApiReader.classifications`.
            Default: query for all classifications.
        measure_ids : list of int, optional
            List of measure IDs to query. For possible values, see
            :py:meth:`~UNFCCCSingleCategoryApiReader.show_measure_hierarchy()`.
            Default: query for all measures.
        gases : list of str, optional
            Limit the query to these gases. For possible values, see
            :py:attr:`~UNFCCCApiReader.gases`. Default: query for all gases.
        batch_size : int, optional
            Number of variables to query in a single API query in the same batch to
            avoid internal server errors. Larger queries are split automatically.
            The default is 1000, which seems to work fine.
        progress : bool
            Display a progress bar. Requires the :py:mod:`tqdm` library. Default: false.


        Returns
        -------
        pandas.DataFrame

        Notes
        -----
        Further documentation about the meaning of parties, categories, classifications,
        measures and gases is available at the `UNFCCC documentation`_.

        .. _UNFCCC documentation: https://unfccc.int/process-and-meetings/\
transparency-and-reporting/greenhouse-gas-data/data-interface-help#eq-7
        """
        party_ids = []
        for code in party_codes:
            try:
                party_ids.append(self._name_id(self.parties, code, key="code"))
            except KeyError:
                help = (
                    "try `UNFCCCSingleCategoryApiReader.parties` for a list of"
                    " valid codes"
                )
                raise ValueError(f"Unknown party `{code}`, {help}!")

        # always query all years
        year_ids = list(self.years.index)

        variable_ids = self._select_variable_ids(
            classifications, category_ids, measure_ids, gases
        )

        i = 0
        raw_response = []
        if progress:
            import tqdm

            pbar = tqdm.tqdm(total=len(variable_ids))

        while i < len(variable_ids):
            batched_variable_ids = variable_ids[i : i + batch_size]
            i += batch_size

            batched_response = self._flexible_query(
                variable_ids=batched_variable_ids,
                party_ids=party_ids,
                year_ids=year_ids,
            )
            raw_response += batched_response
            if progress:
                pbar.update(len(batched_variable_ids))

        if progress:
            pbar.close()

        return self._parse_raw_answer(raw_response)

    def _parse_raw_answer(self, raw: typing.List[dict]) -> pd.DataFrame:
        data = []
        for dp in raw:
            variable = self._variables_dict[dp["variableId"]]

            try:
                category = self.category_tree[variable["categoryId"]].tag
            except treelib.tree.NodeIDAbsentError:
                category = f'unknown category nr. {variable["categoryId"]}'

            row = {
                "party": self._parties_dict[dp["partyId"]],
                "category": category,
                "classification": self._classifications_dict[
                    variable["classificationId"]
                ],
                "measure": self.measure_tree[variable["measureId"]].tag,
                "gas": self._gases_dict[variable["gasId"]],
                "unit": self._units_dict[variable["unitId"]],
                "year": self._years_dict[dp["yearId"]],
                "numberValue": dp["numberValue"],
                "stringValue": dp["stringValue"],
            }
            data.append(row)

        df = pd.DataFrame(data)
        df.sort_values(
            ["party", "category", "classification", "measure", "gas", "unit", "year"],
            inplace=True,
        )
        df.drop_duplicates(inplace=True)
        df.reset_index(inplace=True, drop=True)

        return df

    def _select_variable_ids(
        self, classifications, category_ids, measure_ids, gases
    ) -> typing.List[int]:
        # select variables from classification
        if classifications is None:
            classification_mask = pd.Series(
                data=[True] * len(self.variables), index=self.variables.index
            )
        else:
            classification_mask = pd.Series(
                data=[False] * len(self.variables), index=self.variables.index
            )
            for classification in classifications:
                cid = self._name_id(self.classifications, classification)
                classification_mask[self.variables["classificationId"] == cid] = True

        # select variables from categories
        if category_ids is None:
            category_mask = pd.Series(
                data=[True] * len(self.variables), index=self.variables.index
            )
        else:
            category_mask = pd.Series(
                data=[False] * len(self.variables), index=self.variables.index
            )
            for cid in category_ids:
                category_mask[self.variables["categoryId"] == cid] = True

        # select variables from measures
        if measure_ids is None:
            measure_mask = pd.Series(
                data=[True] * len(self.variables), index=self.variables.index
            )
        else:
            measure_mask = pd.Series(
                data=[False] * len(self.variables), index=self.variables.index
            )
            for mid in measure_ids:
                measure_mask[self.variables["measureId"] == mid] = True

        # select variables from gases
        if gases is None:
            gas_mask = pd.Series(
                data=[True] * len(self.variables), index=self.variables.index
            )
        else:
            gas_mask = pd.Series(
                data=[False] * len(self.variables), index=self.variables.index
            )
            for gas in gases:
                gid = self._name_id(self.gases, gas)
                gas_mask[self.variables["gasId"] == gid] = True

        selected_variables = self.variables[
            classification_mask & category_mask & measure_mask & gas_mask
        ]
        return [int(x) for x in selected_variables.index]

    @staticmethod
    def _name_id(df, name, key="name"):
        try:
            return int(df[df[key] == name].index[0])
        except IndexError:
            raise KeyError(name)

    def show_category_hierarchy(self) -> None:
        """Print the hierarchy of categories and their IDs."""
        return self.category_tree.show(idhidden=False)

    def show_measure_hierarchy(self) -> None:
        """Print the hierarchy of measures and their IDs."""
        return self.measure_tree.show(idhidden=False)

    @classmethod
    def _walk(cls, node: dict, tree: treelib.Tree = None, parent=None) -> treelib.Tree:
        if tree is None:
            tree = treelib.Tree()

        tree.create_node(tag=node["name"], identifier=node["id"], parent=parent)

        if "children" in node:
            for child in node["children"]:
                cls._walk(child, tree=tree, parent=node["id"])

        return tree

    def _get(self, component: str) -> typing.Union[dict, list]:
        resp = requests.get(self.base_url + component)
        resp.raise_for_status()
        return resp.json()

    def _post(self, component: str, json: dict) -> typing.List[dict]:
        resp = requests.post(self.base_url + component, json=json)
        resp.raise_for_status()
        return resp.json()
