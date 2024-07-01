import json


def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    return json_data


def write_json(file_path, json_data):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(dumps_json(json_data))


def dumps_json(json_data):
    return json.dumps(json_data, indent=4, ensure_ascii=False)