"""Copy files specified with patterns and filters along with their folders."""
from collections import Counter
import filecmp
from pathlib import Path
from pprint import pprint
from tqdm import tqdm
import shutil
from utilities import choose_yes_no, is_excluded, is_included


def is_excluded(source, excludes):

    for exclude in excludes:
        if exclude in source:
            return True
        
    return False


def get_dest_file(source_file):
    return dest_base_folder / str(source_file.parent)[len(source_base_folder_str)+1:] / source_file.name 


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
# required_exp_files_patterns = ["config.yml",] # "effective-config*.yml","scores-*.csv", ]

# Don't include any subfolders (i.e. run or engine)
# For SMT folders include all the files.
# For OpenNMT folders omit these files:
open_nmt_omit = ["src-onmt.vocab", "src-sp.model", "src-sp.vocab", "test.trg-predictions.txt.", "trg-omnt.vocab", "trg-sp.model", "trg-sp.vocab"]
nllb_omit = ["added_tokens.json", "sentencepiece.bpe.model", "special_tokens_map.json", "test.trg-predictions.txt.", "tokenizer.json", "tokenizer_config.json" ]

files_to_omit = nllb_omit.copy()
files_to_omit.extend(open_nmt_omit)
print(f"These file patterns will not be copied")
pprint(files_to_omit)

file_include_patterns = None

source_base_folder_str = "S:/eBible/MT/experiments"
dest_base_folder_str = "F:/Github/BibleNLP/ebible-experiments/MT/experiments" 
source_base_folder = Path(source_base_folder_str)
dest_base_folder = Path(dest_base_folder_str)
family_folders = [source_base_folder / language_family for language_family in language_families]

subfolders_to_omit = []

subfolders = []
print(f"Looking for source folders.")
for family_folder in family_folders:
    family_subfolders = [folder for folder in family_folder.iterdir() if family_folder.is_dir()]
    subfolders.extend(family_subfolders)
    
    # If any not-to-be-copied files exist on the destination remove them a family folder at a time.
    dest_files_to_remove = []
    for family_subfolder in family_subfolders:
        destination_folder = dest_base_folder / str(family_subfolder)[len(source_base_folder_str)+1:]
        if destination_folder.is_dir():
            dest_files_to_remove.extend([dest_file_to_remove for dest_file_to_remove in destination_folder.iterdir() if dest_file_to_remove.is_file() and is_excluded(dest_file_to_remove.name, files_to_omit) ])

    if dest_files_to_remove:
        print(f"Found {len(dest_files_to_remove)} files to remove from {family_folder}.")
        pprint([dest_file_to_remove.resolve() for dest_file_to_remove in dest_files_to_remove])
        if choose_yes_no(f"Delete these files? y/n?"):
            for dest_file_to_remove in dest_files_to_remove:
                dest_file_to_remove.unlink()
            print(f"Deleted files.\n")

destination_folders = []
destination_folders_to_create = []
for subfolder in subfolders:
    destination_folder = dest_base_folder / str(subfolder)[len(source_base_folder_str)+1:]
    destination_folders.append(destination_folder)
    if not destination_folder.is_dir():
        destination_folders_to_create.append(destination_folder)


# If any not-to-be-copied files exist on the destination remove them a family folder at a time.
# for destination_folder in destination_folders:
#     if destination_folder.is_dir():
#         dest_files_to_remove = [dest_file_to_remove for dest_file_to_remove in destination_folder.iterdir() if is_excluded(dest_file_to_remove.name, files_to_omit) and dest_file_to_remove.is_file()]
#         if dest_files_to_remove:
#             print(f"Found {len(dest_files_to_remove)} files to remove from {destination_folder}.")
#             pprint(dest_files_to_remove)
#             if choose_yes_no(f"Delete these files? y/n?"):
#                 for dest_file_to_remove in dest_files_to_remove:
#                     dest_file_to_remove.unlink()
#                     print(f"Deleted files.\n")


# If file_include_patterns is set, only copy files matching those patterns.
if file_include_patterns:
    print(f"Found {len(subfolders)} folders. Looking in subfolders for files matching these patterns")
    pprint(file_include_patterns)
    source_files = []
    for subfolder in tqdm(subfolders):
        for file_include_pattern in file_include_patterns:
                source_files.extend([file for file in subfolder.glob(file_include_pattern)])
else:
    print(f"Found {len(subfolders)} folders. Looking for all source files in subfolders.")
    source_files = [source_file for subfolder in tqdm(subfolders) for source_file in subfolder.iterdir() if not is_excluded(source_file.name, files_to_omit) and source_file.is_file()]



#pprint(source_files[:10])
print("Checking whether files have changed")
filtered_copy_pairs = []
for source_file in tqdm(source_files):
    destination_file = get_dest_file(source_file)
    if destination_file.is_file() and not filecmp.cmp(source_file, destination_file, shallow=True):
        filtered_copy_pairs.append((source_file, destination_file))

experiments_with_scores = set(source_file.parent for (source_file, destination_file) in filtered_copy_pairs if "scores" in source_file.name )


if filtered_copy_pairs:
    if destination_folders_to_create:
        print(f"Will create these destination folders:")
        pprint(destination_folders_to_create)

    print(f"Will copy {len(filtered_copy_pairs)} files, including {len(experiments_with_scores)} experiments with new scores.")
    pprint(sorted(experiments_with_scores))
    print(f"From: {filtered_copy_pairs[0][0]}\nTo {filtered_copy_pairs[0][1]}")
    if not choose_yes_no("Continue with copy? y/n?"):
        exit()

    for destination_folder_to_create in destination_folders_to_create:
        destination_folder_to_create.mkdir(parents=True, exist_ok=True)
        print(f"Created destination folder: {destination_folder_to_create}")
    copied = Counter()
    print(f"Copying from {source_base_folder} to {dest_base_folder}.")
    for filtered_copy_pair in tqdm(filtered_copy_pairs): 
        source_file, destination_file = filtered_copy_pair
        copied.update([destination_file.name])
        shutil.copy(source_file, destination_file)
        #print(f"Copied {source_file} to {destination_file}")
    # else:
    #     if not destination_folders_to_create:
    #         print(f"All {len(subfolders)} experiment folders already exist on the destination.")
    print(f"Copied these files")
    pprint(sorted(copied.most_common()))

else: 
    print("All files already exist in the destination folder.")
    exit()




