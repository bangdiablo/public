def str_is_empty(value):
    if value is None or value == '' or len(value) < 1:
        return True
    else:
        return False


def str_is_not_empty(value):
    if str_is_empty(value):
        return False
    else:
        return True


def str_default_if_empty(value, default_value):
    if str_is_empty(value):
        if str_is_not_empty(default_value):
            return default_value
        else:
            return value
    else:
        return value


def str_to_bool(value):
    if str_is_empty(value) or value.upper() == 'FALSE':
        return False
    else:
        return True


def num_is_empty(value):
    if value is None or value == '' or value == 0:
        return True
    else:
        return False


def num_is_not_empty(value):
    if num_is_empty(value):
        return False
    else:
        return True


def num_default_if_empty(value, default_value):
    if num_is_empty(value):
        if num_is_not_empty(default_value):
            return default_value
        else:
            return value
    else:
        return value


def arr_is_empty(arr):
    if arr is None or len(arr) < 1:
        return True
    else:
        return False


def arr_is_not_empty(arr):
    if arr_is_empty(arr):
        return False
    else:
        return True