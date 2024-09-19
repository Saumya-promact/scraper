from fuzzywuzzy import fuzz
from db import get_all_judges


def abbreviate_justice_name(full_name):
    # Split the name into parts
    name_parts = full_name.split("JUSTICE")
    div_name = name_parts[-1].split()
    # Identify the position of "JUSTICE"
    if len(div_name) == 3:
        div_name[0] = div_name[0][0] + "."
        div_name[1] = div_name[1][0] + "."
        return ["".join(div_name), full_name]
    return [full_name]


def find_similar_names(target_name, threshold=75):
    similar_names = []
    judges = get_all_judges()
    name_list = [judge.name for judge in judges]

    for name in name_list:
        # Check similarity with both full name and its permutations
        possible_name = abbreviate_justice_name(name)
        similarity_score = fuzz.token_set_ratio(target_name, possible_name)
        if similarity_score >= threshold:
            similar_names.append(name)
    return similar_names
