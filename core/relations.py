"""In this module we define a preference structure based on
:class:`RelationType` relation types.

A preference structure in this package should not contain conflicted relations.
"""
from enum import Enum, auto
from itertools import product
from typing import Any, List, Optional, Tuple

from numpy import fill_diagonal
from pandas import Series
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, floyd_warshall

from mcda.core.aliases import PerformanceTable


class RelationType(Enum):
    """Enumeration of MCDA relation types."""

    PREFERENCE = auto()
    INDIFFERENCE = auto()
    INCOMPARABLE = auto()

    @classmethod
    def has_value(cls, x: "RelationType") -> bool:
        """Check if value is in enumeration.

        :param x:
        :return:
        """
        return x in cls

    @classmethod
    def content_message(cls) -> str:
        """Return list of items and their values.

        :return:
        """
        s = ", ".join(f"{item}: {item.value}" for item in cls)
        return "RelationType only has following values " + s


Relation = Tuple[Any, Any, RelationType]


def scores_to_relations(
    scores: Series, ascending: bool = False
) -> List[Relation]:
    """Convert scores into relation list.

    :param scores: alternatives' score
    :param ascending: if ``True``, the best alternative has the lowest score
    :return: list of relations

    .. note::
        The minimum number of relations representing the scores is returned.
        (w.r.t transitivity of preference and indifference relations)
    """
    res = []
    sorted_scores = scores.sort_values(ascending=ascending)
    for a, b in zip(
        sorted_scores.index.tolist()[:-1], sorted_scores.index.tolist()[1:]
    ):
        if sorted_scores[a] == sorted_scores[b]:
            res.append((a, b, RelationType.INDIFFERENCE))
        else:
            res.append((a, b, RelationType.PREFERENCE))
    return res


def valid(r: Relation) -> bool:
    """Check whether a relation is valid or not.

    :param r:
    :return: check result
    """
    return r[2] == RelationType.INDIFFERENCE or r[0] != r[1]


def same_alternatives(r1: Relation, r2: Relation) -> bool:
    """Check whether the relations are about the same pair of alternatives.

    :param r1: first relation
    :param r2: second relation
    :return:
        ``True`` if both relations share the same alternatives pair, ``False``
        otherwise

    .. warning:: Does not check for relations' validity!
    """
    return r1[:-1] == r2[:-1] or r1[:-1] == r2[1::-1]


def equal(r1: Relation, r2: Relation) -> bool:
    """Check whether relations are equal.

    :param r1:
    :param r2:
    :return: check result

    .. warning:: Does not check for relations' validity!
    """
    if r1 == r2:
        return True
    if not same_alternatives(r1, r2):
        return False
    if r1[2] != r2[2]:
        return False
    if r1[2] == RelationType.PREFERENCE:
        return False
    return True


def compatible(r1: Relation, r2: Relation) -> bool:
    """Check whether both relations can coexist in the same preference
    structure.

    Relations are compatible if equal or having different elements pair.

    :param r1:
    :param r2:
    :return: check result

    .. warning:: Does not check for relations' validity!
    """
    if r1 == r2:
        return True
    if not same_alternatives(r1, r2):
        return True
    if r1[2] != r2[2]:
        return False
    if r1[2] != RelationType.PREFERENCE:
        return True
    return False


def in_relations(r: Relation, relations: List[Relation]) -> bool:
    """Check whether a relation is already in the preference structure.

    :param r: relation
    :param relations:
    :return: check result

    .. warning:: Does not check for a relation's validity!
    """
    for r2 in relations:
        if equal(r, r2):
            return True
    return False


def elements(relations: List[Relation]) -> List[Any]:
    """Return elements present in relations list.

    :param relations:
    :return:
    """
    res = set()
    for (a, b, _) in relations:
        res.add(a)
        res.add(b)
    return list(res)


def relation(a: Any, b: Any, relations: List[Relation]) -> Optional[Relation]:
    """Return relation between `a` and `b` if it exists in the preference
    structure.

    :param a:
    :param b:
    :param relations:
    :return:

    .. note:: Returns the first relation found

    .. warning:: Does not check for a relation's validity or redundancy!
    """
    for r in relations:
        if r[0] == a and r[1] == b:
            return r
        if r[0] == b and r[1] == a:
            return r
    return None


def alternative_relations(a: Any, relations: List[Relation]) -> List[Relation]:
    """Return all relations involving given element.

    :param a: element
    :param relations:
    :return:

    .. warning:: Does not check for a relation's validity or redundancy!
    """
    res: List[Relation] = []
    for r in relations:
        if r[0] == a or r[1] == a:
            res.append(r)
    return res


def relations_typed(
    r: RelationType, relations: List[Relation]
) -> List[Relation]:
    """Return all relations of given type.

    :param r: relation type
    :param relations:
    :return:

    .. warning:: Does not check for a relation's validity or redundancy!
    """
    res: List[Relation] = []
    for rr in relations:
        if rr[2] == r:
            res.append(rr)
    return res


def relations_pair_unicity(relations: List[Relation]) -> bool:
    """Check whether each pair of alternative has at most one relation.

    :param relations:
    :return: check result

    .. warning:: Does not check for a valid preference structure!
    """
    for i, r1 in enumerate(relations):
        for r2 in relations[(i + 1) :]:
            if same_alternatives(r1, r2):
                return False
    return True


def is_preference_structure(relations: List[Relation]) -> bool:
    """Check whether the relations define a preference structure.

    :param relations:
    :return: check result
    """
    for i, r1 in enumerate(relations):
        if not valid(r1):
            return False
        for r2 in relations[(i + 1) :]:
            if not compatible(r1, r2):
                return False
    return True


def is_total_preorder(relations: List[Relation]) -> bool:
    """Check whether relations list is a total preorder or not.

    :param relations:
    :return: check result
    """
    if not is_preference_structure(relations):
        return False
    res = matrix_to_relations(
        transitive_closure(relations_to_matrix(relations))
    )
    return len(relations_typed(RelationType.INCOMPARABLE, res)) == 0


def is_total_order(relations: List[Relation]) -> bool:
    """Check whether relations list is a total order or not.

    :param relations:
    :return: check result
    """
    if not is_preference_structure(relations):
        return False
    res = matrix_to_relations(
        transitive_closure(relations_to_matrix(relations))
    )
    return (
        len(relations_typed(RelationType.INCOMPARABLE, res))
        + len(relations_typed(RelationType.INDIFFERENCE, res))
        == 0
    )


def transitive_closure(matrix: PerformanceTable) -> PerformanceTable:
    """Return transitive closure of outranking matrix.

    :param matrix:
    :return:
    """
    _m = floyd_warshall(csr_matrix(matrix.to_numpy())) < float("inf")
    m = PerformanceTable(
        _m,
        index=matrix.index,
        columns=matrix.columns,
    )
    res = PerformanceTable(
        0,
        index=matrix.index,
        columns=matrix.columns,
    )
    res[m] = 1
    return res


def add_transitivity(relations: List[Relation]) -> List[Relation]:
    """Add transitive relations to list.

    :param relations:
    :return: result

    .. warning:: Does not check for a valid preference structure!
    """
    return matrix_to_relations(
        transitive_closure(relations_to_matrix(relations))
    )


def remove_transitivity(relations: List[Relation]) -> List[Relation]:
    """Remove transitive relations from list.

    :param relations:
    :return: result

    .. warning:: Does not check for a valid preference structure!

    .. warning:: This function may bundle together multiple elements
    """
    return matrix_to_relations(
        transitive_reduction_matrix(relations_to_matrix(relations))
    )


def relations_to_matrix(relations: List[Relation]) -> PerformanceTable:
    """Transform a list of relations to an outranking matrix.

    :param relations: List of relations
    :return: outranking matrix
    """
    actions = list(set(aa for relation_ in relations for aa in relation_[:-1]))
    matrix = PerformanceTable(0, index=actions, columns=actions)
    fill_diagonal(matrix.values, 1)
    for a, b, r in relations:
        if r == RelationType.PREFERENCE:
            matrix.loc[matrix.index == a, matrix.columns == b] = 1
        if r == RelationType.INDIFFERENCE:
            matrix.loc[matrix.index == a, matrix.columns == b] = 1
            matrix.loc[matrix.index == b, matrix.columns == a] = 1
    return matrix


def matrix_to_relations(
    matrix: PerformanceTable,
) -> List[Relation]:
    """Transform an outranking matrix to a list of relations

    :param matrix: the matrix of relations
    :return: List of relations
    """
    relations: List[Relation] = list()
    for ii, i in enumerate(matrix.index.tolist()):
        for j in matrix.columns.tolist()[ii + 1 :]:
            if matrix.loc[matrix.index == i, matrix.columns == j].all(None):
                if matrix.loc[matrix.index == j, matrix.columns == i].all(
                    None
                ):
                    relations.append((i, j, RelationType.INDIFFERENCE))
                else:
                    relations.append((i, j, RelationType.PREFERENCE))
            elif matrix.loc[matrix.index == j, matrix.columns == i].all(None):
                relations.append((j, i, RelationType.PREFERENCE))
            else:
                relations.append((i, j, RelationType.INCOMPARABLE))
    return relations


def transitive_reduction_matrix(matrix: PerformanceTable) -> PerformanceTable:
    """Perform transitive reduction on preference graph through its outranking
    matrix.

    :param matrix: outranking matrix
    :return: reduced matrix with only shortest path
    """
    matrix = graph_condensation_matrix(matrix)
    path_matrix = floyd_warshall(csr_matrix(matrix.to_numpy())) == 1
    nodes = range(len(matrix))
    for u in nodes:
        for v in nodes:
            if path_matrix[u][v]:
                for w in nodes:
                    if path_matrix[v][w]:
                        matrix.iloc[u, w] = 0
    return matrix


def graph_condensation_matrix(matrix: PerformanceTable) -> PerformanceTable:
    """Return the condensation graph

    :param matrix: outranking matrix
    :return: condensation graph as a matrix

    .. note:: the matrix output by this function is acyclic

    .. warning:: this function changes the matrix shape
    """

    n_components, labels = connected_components(
        matrix.to_numpy(), connection="strong"
    )
    # Return input matrix if no cycle found
    if n_components == len(matrix):
        return matrix
    # Create new matrix with appropriate names for components
    components = []
    for component_index in range(n_components):
        component = tuple(matrix.index[labels == component_index].tolist())
        components.append(component)
    new_matrix = PerformanceTable(0, index=components, columns=components)
    for component_a, component_b in product(
        range(n_components), range(n_components)
    ):
        if component_a != component_b:
            new_matrix.iloc[component_a, component_b] = (
                matrix.iloc[labels == component_a, labels == component_b]
                .to_numpy()
                .any()
            )

    return new_matrix.astype(int)
