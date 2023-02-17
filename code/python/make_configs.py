import shutil
from pathlib import Path
from pprint import pprint
from typing import Dict

import yaml

testing = False
#testing = True

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

experiments_folder_str = "S:/eBible/MT/experiments"
experiments_folder = Path(experiments_folder_str)
test_destination_folder = Path("C:/Gutenberg/MT/experiments/")

source_language_family = "Niger-Congo"
source_family_folder = experiments_folder / source_language_family

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

subfolders_to_omit = ["Overall.Run"]

# Set the series to create:
# language_family = 'Afro-Asiatic'
queue = "langtech_40gb"
#queue = "idx_40gb"
language_family = language_families[5]
language_family_details = language_families_details[language_family]

test_destination_family_folder = test_destination_folder / language_family
destination_family_folder = experiments_folder / language_family

print(
    f"The source_folder is {source_family_folder}\nThe destination is   {destination_family_folder}"
)

source_subfolders = [folder for folder in source_family_folder.iterdir()]

filtered_source_subfolders = []
for source_subfolder in source_subfolders:
    for subfolder_to_omit in subfolders_to_omit:
        if subfolder_to_omit in source_subfolder.name:
            print(f"Omitting {source_subfolder}")
            continue
        else:
            

print(f"Found {len(source_subfolders)} source subfolders")
for source_subfolder in source_subfolders:
    print(source_subfolder)


experiments = []

print(f"Looking for files to copy.")
for source_subfolder in source_subfolders:
    for source_file in source_subfolder.rglob(config_filename):
        if source_file.is_file():
            

            dest_folder = destination_family_folder / source_subfolder.name
            destination_file = dest_folder / source_file.name

            test_folder = test_destination_family_folder / source_subfolder.name
            test_file = test_folder / source_file.name

            # Get the experiment details from the config.yml file.
            with open(source_file, "r") as configfile:
                config: Dict = yaml.safe_load(configfile)

            if testing:
                experiments.append(
                    {
                        "Source folder": source_subfolder,
                        "Source file": source_file,
                        "Destination file": test_file,
                        "Destination folder": test_folder,
                        "Config": config,
                        "Language family": language_family,
                    }
                )
            if not testing:
                experiments.append(
                    {
                        "Source folder": source_subfolder,
                        "Source file": source_file,
                        "Destination file": destination_file,
                        "Destination folder": dest_folder,
                        "Config": config,
                        "Language family": language_family,
                    }
                )

print(f"\nFound {len(experiments)} {config_filename} files.")
#pprint(experiments[0])

for experiment in experiments:

    config: dict = experiment["Config"]
    data_config: dict = config["data"]
    corpus_pairs = data_config["corpus_pairs"]
    #print(experiment["Destination file"])
    #pprint(corpus_pairs)
    #pprint(data_config["lang_codes"])
    #print()

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
        print(related_code, " : ", related_ws)
        config["data"]["lang_codes"][related_code] = related_ws

    # Make necessary folders.
    if not experiment["Destination folder"].is_dir():
        experiment["Destination folder"].mkdir(parents=True, exist_ok=True)
        print(f"Created destination folder: {dest_folder}")

    # print(destination_config_file.parent , type(destination_config_file.parent))
    new_config_file = experiment["Destination file"]
    with new_config_file.open("w", encoding="utf-8") as file:
        yaml.dump(config, file)
    
    print(experiment["Destination file"])
    pprint(corpus_pairs)
    pprint(data_config["lang_codes"])
    print()

for experiment in experiments:

    if testing:
        print(str(experiment["Destination file"])[len(str(test_destination_folder)) + 1 : -11])
    if not testing:
        command_folder = str(experiment["Destination file"])[len(str(experiments_folder_str)) + 1 : -11].replace("\\","/")
        print(f"poetry run python -m silnlp.nmt.experiment --save-checkpoints --mixed-precision --memory-growth --clearml-queue {queue} --mt-dir eBible/MT ", command_folder)
        #print(str(experiment["Destination file"])[len(str(experiments_folder_str)) + 1 : -11])
