""" Take a folder of experiments as templates and create modifed copies
in order to run similar experiments with data from different languages."""
import argparse
import shutil
from pathlib import Path
from pprint import pprint
from typing import Dict

import yaml

config_filename = "config.yml"

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
# These parts of foldernames represent the various kinds of experiments that we've run.
# Specify parts of foldernames plain strings, not regexes
# subfolders_to_omit = "Overall.Run" "PartialNT.Scenario", "NewToOld",
subfolders_to_omit = [
    "PartialNT.Scenario",
    "SourceText.Greek.Scenario",
    "Overall.Run",
]

queue = "langtech_40gb"
# queue = "idx_40gb"


# TODO
# Split the logic into three parts:
# 1) Copy configs from one location to antother with filtering.
# 2) Modify configs in place.
# 3) Print the commands required to train experiments.

def is_excluded(source, excludes):

    for exclude in excludes:
        if exclude in source:
            return True

    return False


def make_parent_folders(files):
    for file in files:
        if not file.parent.is_dir():
            print(f"Creating destination folder: {file.parent}")
            file.parent.mkdir(parents=True, exist_ok=True)


def copy_files(source_files, destination_files):
    for source_file, destination_file in zip(source_files, destination_files):
        # shutil.copy(source_file, destination_file)
        print(f"Pretended to copy {source_file} to {destination_file}")


def copy_one_series(source_family_folder, destination_family_folder):

    source_subfolders = [folder for folder in source_family_folder.iterdir()]
    print(f"filtering folders containing :")
    pprint(subfolders_to_omit)

    filtered_source_subfolders = [
        source_subfolder
        for source_subfolder in source_subfolders
        if not is_excluded(source_subfolder.name, excludes=subfolders_to_omit)
    ]
    source_files = [
        source_file
        for filtered_source_subfolder in filtered_source_subfolders
        for source_file in filtered_source_subfolder.rglob(config_filename)
    ]

    destination_files = [
        destination_family_folder
        / filtered_source_subfolder.name
        / source_file.name
        for filtered_source_subfolder in filtered_source_subfolders
        for source_file in filtered_source_subfolder.rglob(config_filename)
    ]

    for source_file, destination_file in zip(source_files, destination_files):
        print(f"These are the to files to copy:")
        print(f"{source_file}    ->     {destination_file}")

        # Make necessary folders
        make_parent_folders(destination_files)
        copy_files(source_files, destination_files)




def main():
    parser = argparse.ArgumentParser(
        description="Copy config files."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default="S:/eBible/MT/experiments",
        help="Base folder to search for source config files.",
    )
    parser.add_argument(
        "--source_family",
        type=str,
        default="Niger-Congo",
        help="Language family for source config files.",
    )
    parser.add_argument(
        "--dest", type=Path, required=True, help="Destination folder 'base' to copy config files."
    )
    parser.add_argument(
        "dest_family", type=str, help="Langauge family for copied config files. Use ALL for all language families"
    )
    args = parser.parse_args()

    if  args.dest_family.lower() != "all" and args.dest_family not in language_families:
        print("These are the available language families:")
        pprint(language_families)
        parser.error("Please specify one of these language families.")

    # experiments_folder_str = "S:/eBible/MT/experiments"
    experiments_folder_str = args.source
    experiments_folder = Path(experiments_folder_str)
    source_family_folder = experiments_folder / args.source_family

    if args.dest_family.lower() == "all":
        for language_family in language_families:
            copy_one_series(source_family_folder, args.dest / language_family)
    else:
        copy_one_series(source_family_folder, args.dest / args.dest_family)

if __name__ == "__main__":
    main()
