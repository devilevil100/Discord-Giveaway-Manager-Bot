import json
with open("config.json", "r+") as f:
    config = json.load(f)
    print(list(config["logs"].keys())[0])  
