
import re
import math

from unfi_api.utils.string import isnumber


def prep_upc_a(upc):
    out = str(upc)
    out = re.sub("\D", "", out)
    if isnumber(out):
        out = out.zfill(12)
        return out if out else upc
    else:
        return upc


def stripcheckdigit(upc, keep_formatting=False):
    """
    :param upc: upc string or int containing a check digit. Should remove the checkdigit and leave it alone if it
    has already had its check digit removed or is not a upc value.
    :type upc: str,int
    :param keep_formatting: keep the input formatting False by default
    :type keep_formatting: bool
    :return: int or str
    """

    upc = prep_upc_a(upc)
    upc_int = int(upc)

    if len(upc) == 13:
        return upc[:-1]

    if len(upc) == 12:
        truncated_upc = upc[:-1]
        truncated_upc_int = int(truncated_upc)
        truncated_upc_w_check_digit = add_check_digit(truncated_upc)
        truncated_upc_cd_int = int(truncated_upc_w_check_digit)
        if upc_int == truncated_upc_cd_int:
            return str(truncated_upc_int).zfill(11)
        else:
            return str(upc_int).zfill(11)
    else:
        return upc


def add_check_digit(upc, text=True):
    """
    Returns a 12 digit upc-a string from an 11-digit upc-a string by adding 
    a check digit
    """

    def _return_upc(u):
        if text:
            return u.zfill(12)
        else:
            return int(u)

    if isinstance(upc, (str, bytes)):
        upc_str = re.sub(r'\D', '', upc)
    else:
        upc_str = str(upc)
    if not isnumber(upc_str, 'int'):
        raise TypeError('Must be an integer value')
    else:
        upc_int = int(upc_str)

    if len(upc_str) == 12:
        # check if already has checkdigit
        if upc_int % 10 == calc_upc_a_check_digit(upc_str[:-1]):
            _return_upc(upc_str)

    if len(upc_str) > 12:
        raise ValueError("Value Too Long {} ({}) Must Be No More Than 12 Characters".format(len(upc_str), upc))
    # calc without fill
    check_digit = calc_upc_a_check_digit(upc_str.zfill(11))
    if check_digit == upc_int % 10:
        _return_upc(upc_str)

    output = upc_str + str(check_digit)
    return _return_upc(output)


def calc_upc_a_check_digit(num):
    num = str(num)
    odd_sum = 0
    even_sum = 0
    for i, char in enumerate(num):
        j = i + 1
        if j % 2 == 0:
            even_sum += int(char)
        else:
            odd_sum += int(char)
    total_sum = (odd_sum * 3) + even_sum
    mod = total_sum % 10
    cd = 10 - mod
    if cd == 10:
        cd = 0
    return cd


def calc_ean13_check_digit(num):
    num = str(num)
    odds = 0
    evens = 0
    for idx, n in enumerate(num, 1):
        if idx % 2 > 0:
            odds += int(n)
        else:
            evens += int(n) * 3
    t = odds + evens
    return (math.ceil(t / 10) * 10) - t
