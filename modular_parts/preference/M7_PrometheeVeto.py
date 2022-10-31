from core.aliases import NumericValue, PerformanceTable
import core.preference_commons as pc
import pandas as pd

__all__ = ["compute_veto"]


def compute_veto(
        alternatives_performances: PerformanceTable,
        weights: pd.Series,
        v_list: pd.Series,
        directions: pd.Series,
        profiles_performance: PerformanceTable = None,
        decimal_place: NumericValue = 3,
        full_veto: bool = True,
        preferences=None):
    """
    Calculates veto of every alternative over other alternatives
    or profiles based on partial veto

    :param alternatives_performances: Dataframe of alternatives' value at every criterion
    :param weights: criteria with weights
    :param v_list: veto threshold for each criteria
    :param directions: directions of preference of criteria
    :param profiles_performance: Dataframe of profiles performance (value) at every criterion
    :param decimal_place: with this you can choose the decimal_place of the output numbers
    :param full_veto: choose methode of calculating vetoes
    :param preferences: if not None function returns already calculated preference instead of just veto
    :return: veto
    :return: partial veto
    """
    alternatives = alternatives_performances.index
    criteria = weights.keys()
    alternatives_performances = pc.directed_alternatives_performances(alternatives_performances, directions)
    if profiles_performance is not None:
        categories_profiles = profiles_performance.keys()
        profile_performance_table = pc.directed_alternatives_performances(profiles_performance, directions)
    else:
        categories_profiles = None
        profile_performance_table = None

    partialVet = _partial_veto(v_list, criteria, alternatives_performances, profile_performance_table,
                               categories_profiles)

    if not categories_profiles:
        veto = _vetoes(criteria, weights, full_veto, partialVet, alternatives)
        partial_veto = partialVet
    else:
        partial_veto = partialVet[1], partialVet[0]
        veto = (_vetoes(criteria, weights, full_veto, partialVet[1], categories_profiles,
                        alternatives),
                _vetoes(criteria, weights, full_veto, partialVet[0], alternatives,
                        categories_profiles))
    if preferences is not None:
        return pc.overall_preference(preferences, veto, categories_profiles)
    else:
        return veto, partial_veto


def _vetoes(criteria, weights, full_veto, partial_veto, i_iter, j_iter=None):
    if j_iter is None:
        j_iter = i_iter
    Vetoes = []
    index = partial_veto.loc[criteria[0]].index
    columns = partial_veto.loc[criteria[0]].columns
    for j in j_iter:
        aggregated_v = []
        for i in i_iter:
            Pi_A_B = 0
            for k in criteria:
                if full_veto:
                    if partial_veto.loc[k, j][i] == 1:
                        Pi_A_B = 1
                        break
                else:
                    Pi_A_B += partial_veto.loc[k, j][i] * weights[k]

            aggregated_v.append(Pi_A_B)
        Vetoes.append(aggregated_v)

    return pd.DataFrame(data=Vetoes, index=index, columns=columns)


def _partial_veto(v_list, criteria, alternatives_performances, profile_performance_table, categories_profiles):
    """
    Calculates partial veto of every alternative over other alternatives
    or profiles at every criterion based on deviations.

    :return: partial veto
    """
    deviations = pc.deviations(criteria=criteria, alternatives_performances=alternatives_performances,
                               profile_performance_table=profile_performance_table)
    if not categories_profiles:

        pvetos = _veto_deep(v_list=v_list, criteria=criteria, deviations=deviations, i_iter=alternatives_performances,
                            j_iter=alternatives_performances)
    else:
        pvetos = [
            _veto_deep(v_list=v_list, criteria=criteria, deviations=deviations[0], i_iter=alternatives_performances,
                       j_iter=profile_performance_table),
            _veto_deep(v_list=v_list, criteria=criteria, deviations=deviations[1], i_iter=profile_performance_table,
                       j_iter=alternatives_performances)]
    return pvetos


def _veto_deep(v_list, criteria, deviations, i_iter, j_iter):
    pvetos = []
    for k in range(criteria.size):
        v = v_list[k]
        criterionIndices = []
        for j in range(i_iter.shape[0]):
            alternative_Vetoes = []
            for i in range(j_iter.shape[0]):
                if v is None:
                    alternative_Vetoes.append(0)
                elif deviations[k][i][j] >= v:
                    alternative_Vetoes.append(1)
                else:
                    alternative_Vetoes.append(0)
            criterionIndices.append(alternative_Vetoes)
        pvetos.append(criterionIndices)

    names = ['criteria'] + i_iter.index.names
    pvetos = pd.concat([pd.DataFrame(data=x, index=i_iter.index, columns=j_iter.index) for x in pvetos],
                       keys=criteria,
                       names=names)
    return pvetos
