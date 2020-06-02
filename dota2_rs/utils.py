from typing import List


def load_key(file_path) -> str:
    with open(file_path) as file:
        line = file.readline()
    return line.strip()


def subset_of_dict(dictionary: dict, keys: List[str]) -> dict:
    return {key: dictionary[key] for key in keys if key in dictionary}
