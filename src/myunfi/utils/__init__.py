from __future__ import print_function

import re
from typing import Dict, List, Union

from unfi_api.utils.string import convert_strings_to_number, isnumber


def round_retails(price):
    """
    if tenth is 0, hundreth is  < 5, and whole is > 0, round down to whole-1 .99.
    if tenth is 0, whole is 0 and hund is < 5, round to 0.05
    """
    price = str(price)
    # find currency symbols and remove them
    currency_symbol = ""
    float_symbols = ["$", "€", "£"]
    cent_symbols = ["¢", "c", "p"]
    currency_symbol = ""
    for symbol in float_symbols:
        if symbol in price:
            currency_symbol = symbol
            price = price.replace(symbol, "")
            break
    for symbol in cent_symbols:
        if symbol in price:
            currency_symbol = symbol
            price = price.replace(symbol, "")
            break

    # make sure price is a number and float
    if not isnumber(price):
        raise TypeError("a number value is required")
    price = float(price)
    # if curenncy symbol is a cent symbol, convert to float and divide by 100
    if currency_symbol in cent_symbols:
        price = price / 100
    # break price into whole number tenths and hudredths
    whole, tenth, hund = explode_number(price)
    round_to_lower_99_tails = ["00", "01", "02", "03", "04", "05"]
    round_to_15_tails = ["06", "07", "08", "09", "10", "11", "12", "13", "14"]
    round_to_15_xtails = ["09", "10", "11", "12", "13", "14"]
    round_to_lower_x9_tails = ["x0", "x1", "x2", "x3"]
    round_to_x5_tails = ["x4", "x5", "x6"]
    round_to_x9_tails = ["x7", "x8"]
    tail = str(tenth) + str(hund)
    xtail = "x" + tail[1]
    if whole == 0 and tail in round_to_lower_99_tails:
        if tenth == 0:
            if hund < 5:
                price = 0.05
            else:
                price = 0.09
    elif whole == 0 and tail in round_to_15_tails:
        price = 0.15

    elif tenth == 0:
        if tail in round_to_lower_99_tails:
            price = "{}.{}".format(whole - 1, "99")
        elif tail in round_to_15_tails:
            price = "{}.{}".format(whole, "15")
    else:
        if xtail in round_to_x5_tails:
            price = "{}.{}{}".format(whole, tenth, 5)
        elif tail in round_to_15_tails:
            price = "{}.{}".format(whole, "15")
        elif xtail in round_to_x5_tails:
            price = "{}.{}{}".format(whole, tenth, 5)
        elif xtail in round_to_x9_tails:
            price = "{}.{}{}".format(whole, tenth, 9)
        elif xtail in round_to_15_xtails:
            price = "{}.{}".format(whole, "15")
        elif xtail in round_to_lower_x9_tails:
            price = "{}.{}{}".format(whole, tenth-1, "9")
        else:
            price = "{}.{}{}".format(whole, tenth, hund)

    return float(price)
 


# Collection Utils


def index_header(
    header: Union[List[List], List], header_end: int = None, verbose=False
) -> Dict[int, str]:
    """
    :param header_end: last index of the header to include in the colindex
    :param header: list of header rows to index
    :type ws: iterable
    :param header_row: starting row of data default 1
    :type header_row: int
    :return: dict
    :rtype dict: `outcolindex`
    """
    # check if header is a list or a list of lists
    if isinstance(header, list):
        if isinstance(header[0], list):
            header = header
        else:
            header = [header]
    else:
        raise TypeError("header must be a list or a list of lists")

    # for each index in the headers list create a dict of the header name from all headers combined with the column index
    outcolindex = {}  # type: Dict[int: str]
    for i, h in enumerate(header):
        for ii, hh in enumerate(h[:header_end]):
            if hh:
                current_index = outcolindex.setdefault(ii, None)
                if current_index:
                    if verbose:
                        print("{} {} {}".format(i, ii, hh))
                    outcolindex[ii] = "{} {}".format(current_index, hh)
                else:
                    outcolindex[ii] = hh
    return outcolindex

    # header_end = header_end if header_end >= header_row else header_row
    # colindex = {u"{}".format(k).lower(): [] for k in ws[header_row]}
    # for idx, val in enumerate(ws[header_row]):
    #     colindex[u"{}".format(val).lower()].append(idx)

    # if verbose:
    #     print(colindex)

    return colindex


def explode_number(number):
    """
    breaks down number into whole, tenth, and hundreth
    """
    s = u"%s" % round(float(number), 2) if isnumber(number) else None
    if not s:
        raise TypeError("a number value is required")
    hund = None
    tenth = None
    whole = None
    if isnumber(number, "float"):
        whl, dec = s.split(".")
        hund = int(dec[-1]) if len(dec) == 2 else 0
        tenth = int(s[-2]) if len(dec) == 2 else int(s[-1])
        whole = int(whl)
    elif isnumber(number, "int"):
        hund = 0
        tenth = 0
        whole = int(number)

    return whole, tenth, hund


def simple_round_retail(price):
    """
    Round prices to our standard structure.
    1.09 -> 1.15
    1.05 -> .99
    1.00 -> .99
    1.11 -> 1.15
    1.16 -> 1.19
    1.20 -> 1.19
    1.92 -> 1.95
    1.96 -> 1.99
    :param price:
    :return:
    """
    whole, tenth, hund = explode_number(price)

    def __zero_x(w, t, h):
        if h < 9:
            if w > 0:
                w -= 1
                t = 9
                h = 9
            else:
                t = 1
                h = 5
        else:
            t = 1
            h = 5
        return w, t, h

    if tenth == 0:
        whole, tenth, hund = __zero_x(whole, tenth, hund)
        return float("{}.{}{}".format(whole, tenth, hund))

    elif hund not in [9, 5]:
        if hund < 5:
            if tenth == 1:
                tenth -= 1
                hund = 9
                whole, tenth, hund = __zero_x(whole, tenth, hund)
                return float("{}.{}{}".format(whole, tenth, hund))

            elif 5 < tenth < 9:
                tenth -= 1
                hund = 9

            else:
                hund = 5

            return float("{}.{}{}".format(whole, tenth, hund))

        if hund > 5:
            hund = 9
            return float("{}.{}{}".format(whole, tenth, hund))

    else:
        return float("{}.{}{}".format(whole, tenth, hund))


def yesno(text, default=True):
    """
    Parse a user input into true or false based on yes/no questions
    :param text:
    :param default:
    :return: bool
    """
    yesre = re.compile(r"^\s*?((?P<yes>Y(ES)?)|(?P<no>NO?))\s*?", re.IGNORECASE)
    yesnomatch = yesre.match(text)
    yes = default
    if yesnomatch or not text:
        yes = default
        if yesnomatch:
            yes = True if yesnomatch.group("yes") else False
            return yes
        if yes:
            return yes

    return yes

def ask_yesno(text, default=True):
    """
    Ask a yes/no question to the user
    """
    y = "Y" if default else "y"
    n = "N" if not default else "n"
    text = f"{text} [{y}/{n}]: "
    response = input(text)
    return yesno(response, default)
