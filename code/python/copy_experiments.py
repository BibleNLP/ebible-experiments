"""Copy files specified with patterns and filters along with their folders."""

from pathlib import Path
from pprint import pprint
from tqdm import tqdm
import shutil
from utilities import choose_yes_no, is_excluded, is_included


language_families = [
    "Afro-Asiatic",
    "Austronesian",
    "Dravidian",
    "Indo-European",
    "Niger-Congo",
    "Otomanguean",
    "Sino-Tibetan",
    "Trans-NewGuinea",
]

# Only copy from folder if all these exist.
required_exp_files_patterns = ["scores-*.csv", "config.yml", "effective-config*.yml",]

file_include_strings = []


source_base_folder_str = "S:/eBible/MT/experiments"
dest_base_folder_str = "F:/Github/BibleNLP/ebible-experiments/MT/experiments" 
source_base_folder = Path(source_base_folder_str)
dest_base_folder = Path(dest_base_folder_str)
series_folders = [source_base_folder / language_family for language_family in language_families]

subfolders_to_omit = []
#     "PartialNT.Scenario",
#     "NewToOld",
#     "SourceText.Greek.Scenario",
# ]

subfolders = []

for series_folder in series_folders:
    family_subfolders = [folder for folder in series_folder.iterdir() if series_folder.is_dir()]
    subfolders.extend(family_subfolders)


#pprint(subfolders)
destination_folders_to_create = []
for subfolder in subfolders:
    destination_folder = dest_base_folder / str(subfolder)[len(source_base_folder_str)+1:]
    if not destination_folder.is_dir():
        destination_folders_to_create.append(destination_folder)

source_files = [file for subfolder in subfolders for file in subfolder.iterdir() if file.is_file()]
print(f"Found {len(source_files)} source files that may need to be copied.")
print("Checking to see which already exist on the destination.")
#pprint(files[:10])
copy_pairs = [(source_file, dest_base_folder / str(source_file.parent)[len(source_base_folder_str)+1:] / source_file.name ) for source_file in source_files]
filtered_copy_pairs = [(source_file, destination_file) for (source_file, destination_file) in tqdm(copy_pairs) if not destination_file.is_file()]
count_experiments_with_scores = len(set(source_file.parent for source_file in source_files if "scores" in source_file.name ))

if filtered_copy_pairs:
    if destination_folders_to_create:
        print(f"Will create these destination folders:")
        pprint(destination_folders_to_create)

    print(f"Will copy {len(filtered_copy_pairs)} files, including {count_experiments_with_scores} experiments with scores.")
    print(f"From: {filtered_copy_pairs[0][0]}\nTo {filtered_copy_pairs[0][1]}")
    if not choose_yes_no("Continue with copy? y/n?"):
        exit()

    for destination_folder_to_create in destination_folders_to_create:
        destination_folder_to_create.mkdir(parents=True, exist_ok=True)
        print(f"Created destination folder: {destination_folder_to_create}")

    print(f"Copying from {source_base_folder} to {dest_base_folder}.")
    for filtered_copy_pair in tqdm(filtered_copy_pairs): 
        source_file, destination_file = filtered_copy_pair
        shutil.copy(source_file, destination_file)
        #print(f"Copied {source_file} to {destination_file}")
    # else:
    #     if not destination_folders_to_create:
    #         print(f"All {len(subfolders)} experiment folders already exist on the destination.")
                    
else: 
    print("All files already exist in the destination folder.")
    exit()




