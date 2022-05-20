import json

enemy_ids = []
shurikens = []
explosions = []
spawners = []
general_info = [None]
with open("assets/data/metadata.json") as f:
    METADATA = json.load(f)

PARENTS = {"sprites", "fonts", "data", "audio"}
