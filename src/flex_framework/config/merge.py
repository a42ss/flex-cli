import copy

from .exception import InvalidConfigurationMergeParams


def dict_merge(dict1: dict, dict2: dict):
    if len(dict1) == 0:
        return dict2.copy()
    if len(dict2) == 0:
        return dict1.copy()
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict):
            result[key] = dict_merge(result[key], value)
            continue

        if isinstance(value, list) and key in result and isinstance(result[key], list):
            result[key] = merge_list(result[key], value)
            continue

        result[key] = copy.deepcopy(value)

    return result


def merge_list(list1: list, list2: list):
    result: dict = {}
    add_list_items_to_results(result, list1)
    add_list_items_to_results(result, list2)

    return list(result.values())


def add_list_items_to_results(result: dict, items: list):
    for value in items:
        if type(value) in [dict, list]:
            raise InvalidConfigurationMergeParams(
                "Invalid configuration values to be merged"
            )
        result[value] = value
