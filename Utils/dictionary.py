def to_dict(payload, keys):

    temp = {}
    for key in keys:
        if key not in payload:
            temp[key] = None
        else:
            temp[key] = payload[key]
    return temp