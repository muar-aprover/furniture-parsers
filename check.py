
import json, os


CHECKPOINT = "checkpoint.json"
def save_checkpoint(page, item_index, n):
    data = {"page": page, "item_index": item_index, "n": n}
    with open(CHECKPOINT, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=3)
    
def load_checkpoint():
    if not os.path.exists(CHECKPOINT):
        return 1, 0, 1
    
    with open(CHECKPOINT, "r", encoding="utf-8") as file:
        data = json.load(file)
        
    return data["page"], data["item_index"], data["n"]

def delete_checkpoint(CHECKPOINT):
    if os.path.exists(CHECKPOINT):
        os.remove(CHECKPOINT)
