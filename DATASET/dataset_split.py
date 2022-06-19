# ==============================================================
#  Command instruction 
# ==============================================================

"""
conda activate <env>
cd path/to/dataset_split.py
python dataset_split.py
"""

# ==============================================================
#  Library 
# ==============================================================

import os
import json
import random
import shutil

# ==============================================================
#  Argument 
# ==============================================================

# Directory of source JSON file, image folder, and output folder
JSON_PATH  = "./DATASET/OralCancer/cancer/_OralCancer_via_project_17Jun2022_2h25m_json.json"
IMG_DIR    = "./DATASET/OralCancer/cancer/"
OUTPUT_DIR = "./DATASET/DATA_220624/"

# Subset of dataset & splitting ratio
SUBSET = ['train', 'val', 'test']
RATIO  = [0.8, 0.1, 0.1]

# Category namespace defined by VIA annotation
SOURCE = "OralCancer" 

# Random seed of shuffling for particular formula
SEED = 9

# ==============================================================
#  Function 
# ==============================================================

def Get_index(len_JSON, ratio):
    idx_train = round(len_JSON * ratio[0])
    idx_val   = round(len_JSON * ratio[1]) + idx_train
    idx_test  = len_JSON
    return [0, idx_train, idx_val, idx_test]

def Count_instance(annotations):
    Num_cls = {'G':0, 'Y':0, 'R':0, 'Neg':0}
    for anno in annotations:
        if type(anno['regions']) is dict:
            regions = [s for s in anno['regions'].values()]
        else:
            regions = [s for s in anno['regions']]
        
        for rgn in regions:
            if rgn['region_attributes'][SOURCE] == "G":
                Num_cls['G'] += 1
            elif rgn['region_attributes'][SOURCE] == "Y":
                Num_cls['Y'] += 1
            elif rgn['region_attributes'][SOURCE] == "R":
                Num_cls['R'] += 1
        if regions == []:
            Num_cls['Neg'] += 1
    return Num_cls

def Count_margin(Num_cls, ratio):
    Range_margin = {
        'G': [round(Num_cls['G'] * ratio * 0.95), round(Num_cls['G'] * ratio * 1.05)], 
        'Y': [round(Num_cls['Y'] * ratio * 0.95), round(Num_cls['Y'] * ratio * 1.05)], 
        'R': [round(Num_cls['R'] * ratio * 0.95), round(Num_cls['R'] * ratio * 1.05)], 
        'Neg': [round(Num_cls['Neg'] * ratio * 0.95), round(Num_cls['Neg'] * ratio * 1.05)]
    }
    return Range_margin


# ==============================================================
#  Split proper proportion of sub-dataset 
# ==============================================================

# - Load JSON file - 
JSON_load = json.load(open(JSON_PATH))
JSON_load = list(JSON_load.values())

# - Caculate original number of instance - 
Num_cls_original = Count_instance(JSON_load)
print(f'\n* Total class quantity: {Num_cls_original}')

# - Shuffle JSON file - 
random.seed(SEED)
random.shuffle(JSON_load)

# - Set train/val/test index - 
Idx = Get_index(len(JSON_load), RATIO)

print(f'- idx_train: {Idx[0]} ~ {Idx[1]}')
print(f'- idx_val  : {Idx[1]} ~ {Idx[2]}')
print(f'- idx_test : {Idx[2]} ~ {Idx[3]}')

# - Train / Val / Test -
for i, sub in enumerate(SUBSET):
    
    # - Split JSON file - 
    JSON_shuffle = JSON_load[Idx[i]:Idx[i+1]]
    
    # - Set VIA ID - 
    JSON_save = {}
    for sub_json in JSON_shuffle: # [Err] Never use "json" as variable
        ID = sub_json['filename'] + str(sub_json['size'])
        JSON_save.update({ID: sub_json})
    
    # - Analyze instance of each class - 
    Num_cls = Count_instance(JSON_shuffle)
    
    # - Analyze margin of each split - 
    Margin_cls = Count_margin(Num_cls_original, RATIO[i])
    
    print(f'\n ({sub}) class quantity: {Num_cls}')
    print(f' ({sub}) class distribution margin: {Margin_cls}\n')
    
    # - Compare & show imbalance content - 
    for c in ['G', 'Y', 'R', 'Neg']: 
        if Num_cls[c] not in range(Margin_cls[c][0],Margin_cls[c][1]):
            print(f" > Num_cls[{c}]: {Num_cls[c]} is not in range of {Margin_cls[c]}")
    
    # Build saving folder
    out_dir = OUTPUT_DIR + sub
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    
    # - Save JSON file - 
    save_path = out_dir + f'/{sub}.json'
    if os.path.exists(save_path):
        os.remove(save_path)
    with open(save_path, 'w') as JSON_file:
        json.dump(JSON_save, JSON_file)


# ==============================================================
#  - Image file distributing according to JSON - 
# ==============================================================

# [Input] Wheter to split dataset from JSON?
opt_separate = ""
while opt_separate not in ['y','n']:
    print(f"\n[Input] Would you wanna separate dataset according to the JSON patches?")
    opt_separate = input("[y/n] => ")

if opt_separate == 'y':
    
    for i, sub in enumerate(SUBSET):
        in_dir = OUTPUT_DIR + f'{sub}/{sub}.json'
        JSON_load = json.load(open(in_dir))
        JSON_load = list(JSON_load.values())
        
        for anno in JSON_load:
            filename = anno['filename']
            src_path = IMG_DIR + filename
            dst_path = OUTPUT_DIR + f"{sub}/{filename}"
            
            if not os.path.exists(dst_path):
                shutil.copyfile(src_path, dst_path)
    
    print(f'\n[Info] Finish separating datasets into train/val/test sets.')

else:
    print(f'\n[Info] Not to separate dataset. Please try other seed to get proper proportion.')
