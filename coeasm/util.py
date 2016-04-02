def is_harvestable(digit_str):
    if digit_str[0] in 'bx':
        return digit_str[1:].isdigit()
    else:
        return digit_str.isdigit()


def harvest(digit_str):
    """
    Attempt to convert an numeric string into an integer
    examples
        'b1000' returns 8
        'x8F'   returns 143
        '123'   returns 123
    """
    assert is_harvestable(digit_str)
    if digit_str[0] in 'bx':
        if digit_str[0] == 'b':
            return int(digit_str[1:], 2)
        else:
            return int(digit_str[1:], 16)
    else:
        return int(digit_str)
