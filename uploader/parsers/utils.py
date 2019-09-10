import json
import re

from json import JSONEncoder


class PropertyEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def convert_json(d, convert):
    new_d = {}
    for k, v in d.items():
        if isinstance(v, list):
            new_d[convert(k)] = []
            for i, vv in enumerate(v):
                new_d[convert(k)].append(convert_json(v[i], convert))
        else:
            new_d[convert(k)] = convert_json(v, convert) if isinstance(v, dict) else v
    return new_d


camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def convert_load(*args, **kwargs):
    json_obj = json.load(*args, **kwargs)
    return convert_json(json_obj, camel_to_underscore)


def convert_dump(*args, **kwargs):
    args = (convert_json(args[0], underscore_to_camel),) + args[1:]
    json.dump(*args, **kwargs)

FLOOR_MAP = {
    "Upper Ground Floor": "0",
    "Other Floor": "0",
    "Lower Ground Floor": "-1",
    "Ground Floor - Vacant": "0",
    "Ground Floor - Vacant - Vacant": "0",
    "Ground Floor - Vacant In Use": "0",
    "Ground Floor": "0",
    "Basement 2": "-2",
    "Basement 1": "-1",
    "Basement 3": "-3",
    "25th Floor": "25",
    "24th Floor": "24",
    "23th Floor": "23",
    "22th Floor": "22",
    "21th Floor": "21",
    "20th Floor": "20",
    "19th Floor": "19",
    "18th Floor": "18",
    "17th Floor": "17",
    "16th Floor": "16",
    "15th Floor": "15",
    "14th Floor": "14",
    "13th Floor": "13",
    "12th Floor": "12",
    "11th Floor": "11",
    "10th Floor": "10",
    "9th Floor": "9",
    "8th Floor": "8",
    "7th Floor": "7",
    "6th Floor": "6",
    "5th Floor": "5",
    "4th Floor": "4",
    "3rd Floor": "3",
    "2nd Floor": "2",
    "1st Floor": "1",
}


def get_floor_number(floor: str):
    if floor in FLOOR_MAP:
        return FLOOR_MAP[floor]

    if "GROUND" in floor.upper():
        return "0"
    elif " 1ST" in floor:
        return "1"
    elif " 2ND" in floor:
        return "2"