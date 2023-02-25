"""Copy files specified with patterns and filters along with their folders."""

from pathlib import Path
from pprint import pprint
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

if not destination_folders_to_create:
    print(f"All {len(subfolders)} experiment folders already exist on the destination.")
else:
    for destination_folder_to_create in destination_folders_to_create:
        destination_folder_to_create.mkdir(parents=True, exist_ok=True)
        print(f"Created destination folder: {destination_folder_to_create}")

source_files = [file for subfolder in subfolders for file in subfolder.iterdir() if file.is_file()]

#pprint(files[:10])
copy_pairs = [(source_file, dest_base_folder / str(source_file.parent)[len(source_base_folder_str)+1:] / source_file.name ) for source_file in source_files]
filtered_copy_pairs = [(source_file, destination_file) for (source_file, destination_file) in copy_pairs if not destination_file.is_file()]
print(f"Found {len(filtered_copy_pairs)} files to copy")

for filtered_copy_pair in filtered_copy_pairs: 
    source_file, destination_file = filtered_copy_pair
    shutil.copy(source_file, destination_file)
    print(f"Copied {source_file} to {destination_file}")
exit()   

# https://stackoverflow.com/questions/4568580/python-glob-multiple-filetypes
#Not recursive?
#files = [file for file in source.iterdir() if any(file.match(pattern) for pattern in patterns)]
for subfolder in subfolders:
    source = source / subfolder
    #print(f"Looking for files to copy from {subfolder}")
    #scores_files = [file for file in source.rglob(scores_pattern) if (file.parent / "config.yml").is_file()]
    scores_files = [file for file in test_source.rglob(scores_pattern) if (file.parent / "config.yml").is_file()]
    config_files = [file.with_name("config.yml") for file in scores_files]

    source_folders = sorted(set([file.parent for file in scores_files]))

    #infer_folders = []
    #for source_folder in source_folders:
    #    source_infer_folder = source_folder / infer_folder
    #    if source_infer_folder.is_dir():
    #        dest_infer_folder = dest / str(file_to_copy.parent)[len(source_folder_str) + 1:] / infer_folder
    #        print(f"Copying {source_infer_folder} to {dest_infer_folder}")
    #        #shutil.copytree(source_infer_folder ,dest_infer_folder)

    #effective_config_files = []
    #for source_folder in source_folders:
    #    for file in source_folder.glob("effective-config*.yml"):
    #        effective_config_files.append(file)

    effective_config_files = [file for source_folder in source_folders for file in source_folder.glob("effective-config*.yml")]
    inferred_files = [file for source_folder in source_folders for file in source_folder.rglob("*.sfm")]

    files_to_copy = scores_files
    files_to_copy.extend(config_files)
    files_to_copy.extend(effective_config_files)
    files_to_copy.extend(inferred_files)

    # Filter out existing files
    filtered_files_to_copy = []
    for file_to_copy in files_to_copy:
        
        copy_to = dest / str(file_to_copy.parent)[len(source_folder_str) + 1:] / file_to_copy.name
        #print(f"Checking to see if {copy_to} exists: {copy_to.is_file()}.")
        if not copy_to.is_file():
            filtered_files_to_copy.append((file_to_copy, copy_to))

           
    #     print(f"Found {len(files_to_copy)} files to copy from {subfolder}.  {len(files_to_copy) - len(filtered_files_to_copy)} already exist on the destination.")
    # else: 
    #     print(f"Found {len(files_to_copy)} files to copy from {subfolder}")

    # if not filtered_files_to_copy:
    #     continue
    # elif not choose_yes_no("Continue y/n ?"):
    #     exit()
if filtered_files_to_copy:
    for files in tqdm(filtered_files_to_copy):
        source_file, dest_file = files
        #print(s,d)
        #print(s.is_file(), d.is_file())
        dest_folder = dest / str(source_file.parent)[len(source_folder_str) + 1:]
        #if not dest_folder.is_dir():
        #    print(f"Creating folder:  {dest_folder}")
        dest_folder.mkdir(parents=True, exist_ok=True)

        # Write an exact copy of the file from the source to the new destination folder if necessary.
        #print(f"Writing:  {dest_file}")
        shutil.copyfile(source_file, dest_file)

        #    copy_to = dest / str(file_to_copy.parent)[len(source_folder_str) + 1:] / file_to_copy.name
        #    print(copy_to)
        #    print(copy_to.is_file())
else :
    print(f"All specified files already exist in {dest}")
exit()

#for file_pattern in file_patterns:
#    files = source.rglob(file_pattern)

for file in files:
    for idx, parent in enumerate(file.parents):
#        print(parent, "    ", idx, "    ", parent.name)
        if parent.name == bottom_shared_folder_name:
            
            # Create the folders on the destination drive.
            new_dest = dest_root
            #print(f"Starting to add to {new_dest}")
            for i in reversed(range(idx)):
                #print(f"Adding {file.parents[i].name}")
                new_dest = Path(new_dest , file.parents[i].name)
                #print(f"Dest is now: {new_dest}")

            # Make the folders required if necessary
            if not new_dest.is_dir():
                print(f"Creating folder:  {new_dest}")
                new_dest.mkdir(parents=True, exist_ok=True)
            
            destination_file = new_dest / file.name

            # Write an exact copy of the file from the source to the new destination folder if necessary.
            if not destination_file.is_file():
                print(f"Writing:  {destination_file}")
                shutil.copyfile(file, destination_file)

            


