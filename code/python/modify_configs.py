""" Take a folder of experiments as templates and create modifed copies
in order to run similar experiments with data from different languages."""
import argparse
import shutil
from pathlib import Path
from pprint import pprint
from typing import Dict

import yaml

language_families_details = {
    "Afro-Asiatic": {
        "1st_pair": {"src": "hau-hausa", "trg": "daa-daaNT"},
        "2nd_pair": {"src": "hau-hausa", "trg": "fuh-fuhbkf"},
        "lang_codes": {"hau": "hau_Latn", "daa": "daa_Latn"},
        "related_lang_code": {"fuh": "fuh_Latn"},
    },
    "Austronesian": {
        "1st_pair": {"src": "ksd-ksd", "trg": "kqw-kqw"},
        "2nd_pair": {"src": "ksd-ksd", "trg": "rai-rai"},
        "lang_codes": {"ksd": "ksd_Latn", "kqw": "kqw_Latn"},
        "related_lang_code": {"rai": "rai_Latn"},
    },
    "Dravidian": {
        "1st_pair": {"src": "tam-tam2017", "trg": "mal-mal"},
        "2nd_pair": {"src": "tam-tam2017", "trg": "kan-kan2017"},
        "lang_codes": {"tam": "tam_Taml", "mal": "mal_Mlym"},
        "related_lang_code": {"kah": "kah_Knda"},
    },
    "Indo-European": {
        "1st_pair": {"src": "hin-hin2017", "trg": "pan-pan"},
        "2nd_pair": {"src": "hin-hin2017", "trg": "guj-guj2017"},
        "lang_codes": {"hin": "hin_Deva", "pan": "pan_Gurm"},
        "related_lang_code": {"guj": "guj_Gujr"},
    },
    "Niger-Congo": {
        "1st_pair": {"src": "hau-hausa", "trg": "daa-daaNT"},
        "2nd_pair": {"src": "hau-hausa", "trg": "fuh-fuhbkf"},
        "lang_codes": {"hau": "hau_Latn", "daa": "daa_Latn"},
        "related_lang_code": {"fuh": "fuh_Latn"},
    },
    "Otomanguean": {
        "1st_pair": {"src": "spa-sparvg", "trg": "zat-zatNTps"},
        "2nd_pair": {"src": "spa-sparvg", "trg": "zad-zadNT"},
        "lang_codes": {"spa": "spa_Latn", "zat": "zat_Latn"},
        "related_lang_code": {"zad": "zad_Latn"},
    },
    "Sino-Tibetan": {
        "1st_pair": {"src": "npi-npiulb", "trg": "taj-taj"},
        "2nd_pair": {"src": "npi-npiulb", "trg": "lif-lifNT"},
        "lang_codes": {"npi": "npi_Deva", "taj": "taj_Deva"},
        "related_lang_code": {"lif": "lif_Deva"},
    },
    "Trans-NewGuinea": {
        "1st_pair": {"src": "tpi-tpiOTNT", "trg": "yut-yut"},
        "2nd_pair": {"src": "tpi-tpiOTNT", "trg": "nca-nca"},
        "lang_codes": {"tpi": "tpi_Latn", "yut": "yut_Latn"},
        "related_lang_code": {"nca": "nca_Latn"},
    },
}

config_filename = "config.yml"
greek_source = "grc-grcsbl"

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
    "NewToOld",
    "SourceText.Greek.Scenario",
]

queue = "langtech_40gb"
# queue = "idx_40gb"


# TODO
# Split the logic into three parts:
# 1) Copy configs from one location to antother with filtering.
# 2) Modify configs in place.
# 3) Print the commands required to train experiments.


def choose_yes_no(prompt: str) -> bool:

    choice: str = " "
    while choice not in ["n", "y"]:
        choice: str = input(prompt + "  Enter y or n ").strip()[0].lower()
    if choice == "y":
        return True
    elif choice == "n":
        return False


def print_command(
    config_file, experiments_folder_str, test_only=False, queue="langtech_40gb"
):

    command_folder = str(config_file)[
        len(str(experiments_folder_str)) + 1 : -11
    ].replace("\\", "/")

    if test_only:
        print(
            f"poetry run python -m silnlp.nmt.experiment --save-checkpoints --mixed-precision --memory-growth --clearml-queue {queue} --score-by-book --test --mt-dir eBible/MT ",
            command_folder,
        )
    else:
        print(
            f"poetry run python -m silnlp.nmt.experiment --save-checkpoints --mixed-precision --memory-growth --clearml-queue {queue} --score-by-book --mt-dir eBible/MT ",
            command_folder,
        )
        # print(str(experiment["Destination file"])[len(str(experiments_folder_str)) + 1 : -11])


def print_commands(
    config_files, experiments_folder_str, test_only=False, queue="langtech_40gb"
):
    for config_file in config_files:
        print_command(
            config_file, experiments_folder_str, test_only=test_only, queue=queue
        )


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
        print(source_file, source_file)


def modify_config(config_file, language_family_details, greek_source):

    # Get the experiment details from the config.yml file.
    with open(config_file, "r") as file:
        config: Dict = yaml.safe_load(file)

    data_config: dict = config["data"]
    corpus_pairs = data_config["corpus_pairs"]
    print(file)
    pprint(corpus_pairs)
    pprint(data_config["lang_codes"])
    print()

    if not config["data"]["corpus_pairs"][0]["src"] == greek_source:
        config["data"]["corpus_pairs"][0]["src"] = language_family_details["1st_pair"][
            "src"
        ]

    config["data"]["corpus_pairs"][0]["trg"] = language_family_details["1st_pair"][
        "trg"
    ]
    config["data"]["lang_codes"] = language_family_details["lang_codes"]
    if len(corpus_pairs) == 2:
        if not config["data"]["corpus_pairs"][1]["src"] == greek_source:
            config["data"]["corpus_pairs"][1]["src"] = language_family_details[
                "2nd_pair"
            ]["src"]

        config["data"]["corpus_pairs"][1]["trg"] = language_family_details["2nd_pair"][
            "trg"
        ]

        related_code = list(language_family_details["related_lang_code"].keys())[0]
        related_ws = language_family_details["related_lang_code"][related_code]
        # print(related_code, " : ", related_ws)
        config["data"]["lang_codes"][related_code] = related_ws

    # with config_file.open("w", encoding="utf-8") as file:
    #    yaml.dump(config, file)

    print(f"Wrote config file to {file}")
    pprint(corpus_pairs)
    pprint(data_config["lang_codes"])
    print()
    return config

def main():
    parser = argparse.ArgumentParser(
        description="Process config files, copy, modify, create silnlp commmandlines."
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
        "--dest", type=Path, help="Destination folder 'base' to copy config files."
    )
    parser.add_argument(
        "--dest_family", type=str, help="Langauge family for copied config files. Use ALL for all language families"
    )
    parser.add_argument(
        "--modify",
        action="store_true",
        default=False,
        help="Modify the source files in place.",
    )
    parser.add_argument(
        "--add_test",
        action="store_true",
        default=False,         
        help="Include --test and --score-by-book in the silnlp commands.",
    )
    parser.add_argument(
        "--queue",
        type=str,
        default="langtech_40gb",
        help="ClearML queue for the silnlp commands.",
    )
    args = parser.parse_args()

    if args.source and args.modify:
        parser.error(
            "To modify config files, specify only the destination folder and destination family."
        )

    if args.dest_family not in language_families:
        print("These are the available language families:")
        pprint(language_families)
        parser.error("Please specify one of these language families.")

    else:
        # experiments_folder_str = "S:/eBible/MT/experiments"
        experiments_folder_str = args.source
        experiments_folder = Path(experiments_folder_str)
        # source_language_family = "Niger-Congo"
        source_language_family = args.source_family
        source_family_folder = experiments_folder / source_language_family

        language_family = args.dest_family
        language_family_details = language_families_details[language_family]
        destination_family_folder = experiments_folder / language_family
        source_subfolders = [folder for folder in source_family_folder.iterdir()]
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

    if args.source and args.dest:
        for source_file, destination_file in zip(source_files, destination_files):
            print(f"These are the to files to copy:")
            print(f"{source_file}    ->     {destination_file}")

            choose_yes_no("Continue with copy?")

            # Make necessary folders
            make_parent_folders(destination_files)
            copy_files(source_files, destination_files)

    elif args.modify and args.dest and args.dest_family:
        for config_file in destination_files:
            modify_config(config_file, language_family_details, greek_source)


    print_commands(
        destination_files, experiments_folder_str, test_only=args.add_test, queue=args.queue
    )


if __name__ == "__main__":
    main()
