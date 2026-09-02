import json

def json_reader(file):
    with open(file, "r") as f:
        data = json.load(f)
    return data
    
