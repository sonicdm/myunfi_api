from __future__ import annotations
from collections import Counter, OrderedDict
from typing import List, Any, Dict, MutableMapping


def find_most_common_member(l):
    counts = Counter(l).most_common(1)
    if len(counts) > 0:
        return counts[0][0]


def sort_dict(d):
    od = OrderedDict((k, v) for k, v in sorted(d.items()))
    return od


def is_cur_col(key, cur_cols):
    cur_cols = set(["%s".lower() % x for x in cur_cols])
    key = u"%s" % key
    return len(set(key.lower().split(" ")).intersection(cur_cols)) > 0


def rstrip_list(iterable, value):
    """
    Remove all instances of given value from the end of a list. Works like str().rstrip()
    :param iterable: iterable
    :param value: value to strip
    :return: list

    >>> rstrip_list([1,2,3,4,None,6,None,None,None], None)
    [1, 2, 3, 4, None, 6]
    >>> rstrip_list([1,2,3,4,5,5,5,5,5], 5)
    [1, 2, 3, 4]
    """
    i = iterable[::-1]
    if len(i) > 1:
        for idx, x in enumerate(i):
            while i[0] == value:
                i.remove(value)
    return i[::-1]


def lstrip_list(iterable, value):
    """
    Remove all instances of given value from the end of a list. Works like str().rstrip()
    :param iterable: iterable
    :param value: value to strip
    :return: list

    >>> lstrip_list([1,2,3,4,None,6,None,None,None], None)
    [1, 2, 3, 4, None, 6]
    >>> lstrip_list([1,2,3,4,5,5,5,5,5], 1)
    [1, 2, 3, 4]
    """
    i = iterable
    if len(i) > 1:
        for idx, x in enumerate(i):
            while i[0] == value:
                i.remove(value)
    return i


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


def table_to_dicts(
    table: List[Any], header_row: int = 0, verbose: bool = False
) -> List[Dict]:
    """
    Convert a table to a dict
    :param table:
    :return:
    """
    colindex = {val: idx for idx, val in enumerate(table[header_row])}
    return [dict(zip(colindex.keys(), row)) for row in table[header_row + 1 :]]


def normalize_dict(d: MutableMapping, parent_key="", sep="_") -> dict:
    """
    take a dict of nested dicts and normalize the data into a flat dict
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(normalize_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def lower_case_keys(d):
    """
    Convert all string keys in a dictionary to lowercase.
    """
    new_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            lower_case_keys(v)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    lower_case_keys(item)
        if isinstance(k, str):
            new_dict[k.lower()] = v
        else:
            new_dict[k] = v
    return new_dict


def flatten_dict_overwrite(d: dict) -> dict:
    """
    take a dict of nested dicts and turn all keys into a single dict. overwriting any existing keys
    """
    new_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            new_dict.update(flatten_dict_overwrite(v))
        else:
            new_dict[k] = v
    return new_dict
