def check_dominance_condition(criteria, profiles_performances):
    """
    Check if each boundary profile is strictly worse in each criterion than betters profiles

    :raise ValueError: if any profile is not strictly worse in any criterion than anny better profile
    """
    for criteria_i in range(len(criteria[0])):
        for i, profile_i in enumerate(profiles_performances):
            for j, profile_j in enumerate(profiles_performances[i:]):
                if profile_j[criteria_i] < profile_i[criteria_i]:
                    raise ValueError("Profiles don't fulfill the dominance condition")


def pandas_check_dominance_condition(criteria, category_profiles):
    """
    Check if each boundary profile is strictly worse in each criterion than betters profiles

    :raise ValueError: if any profile is not strictly worse in any criterion than anny better profile
    """
    for (criterion, _) in criteria['criteria_names'].items():
        for i, (_, profile_i) in enumerate(category_profiles.iloc[:-1].iterrows()):
            for _, profile_j in category_profiles.iloc[i + 1:].iterrows():
                if profile_j[criterion] < profile_i[criterion]:
                    raise ValueError("Profiles don't fulfill the dominance condition")
