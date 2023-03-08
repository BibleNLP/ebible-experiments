""" Take a folder of experiments as templates and create modifed copies
in order to run similar experiments with data from different languages."""

import shutil
from pathlib import Path
from pprint import pprint
from typing import Dict

import yaml

def print_command(experiment, base_folder_str, test_only=False, queue="langtech_40gb"):

    command_folder = str(experiment["Destination file"])[len(str(base_folder_str)) + 1 : -11].replace("\\","/")
    if test_only:
        print(f"poetry run python -m silnlp.nmt.experiment --save-checkpoints --mixed-precision --memory-growth --clearml-queue {queue} --score-by-book --test --mt-dir eBible/MT ", command_folder)
    else:
        print(f"poetry run python -m silnlp.nmt.experiment --save-checkpoints --mixed-precision --memory-growth --clearml-queue {queue} --score-by-book --mt-dir eBible/MT ", command_folder)
        #print(str(experiment["Destination file"])[len(str(base_folder_str)) + 1 : -11])


def print_commands(experiments, base_folder_str, test_only=False, queue="langtech_40gb"):
    for experiment in experiments:
        print_command(experiment, base_folder_str, test_only=test_only, queue=queue)


def is_excluded(source, excludes):

    for exclude in excludes:
        if exclude in source:
            return True
        
    return False

def is_included(source, includes):

    for include in includes:
        if include in source:
            return True
    return False


# DON'T CHANGE THESE - SEE BELOW
do_copy = False
test_only = False
testing = False

# COMMENT or UNCOMMENT THESE
# Whether or not to copy the files
do_copy = True

# Whether to copy them to the testing folder or the live folder
testing = True

# Whether to add --test to the command line
#test_only = True

# Choose which ClearML queue to use
#queue = "langtech_40gb"
queue = "idx_40gb"


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
        "1st_pair": {"src": "swh-swhonen", "trg": "cwe-cwe"},
        "2nd_pair": {"src": "swh-swhonen", "trg": "vid-vid"},
        "lang_codes": {"swh": "swh_Latn", "cwe": "cwe_Latn"},
        "related_lang_code": {"vid": "vid_Latn"},
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
    "Tagalog": {
        "1st_pair": {"src": "ilo-iloulb", "trg": "tgl-tglulb"},
        "2nd_pair": {"src": "ilo-iloulb", "trg": "ceb-cebulb"},
        "lang_codes": {"ilo": "ilo_Latn", "tgl": "tgl_Latn"},
        "related_lang_code": {"ceb": "ceb_Latn"},
    },
}

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

#Specify the language families to make configs for.
language_family_configs_to_create = [
    #"Afro-Asiatic",
    #"Austronesian",
    #"Dravidian",
    #"Niger-Congo",
    #"Indo-European",
    #"Otomanguean",
    #"Sino-Tibetan",
    #"Trans-NewGuinea",
    "Tagalog",
]


# These parts of foldernames represent the various kinds of experiments
# that we've run.
# ["NewToOld.GEN_RUT_JON", "Overall.Run", "PartialNT.Scenario",""NewToOld", "RelatedLanguage.PartialNT.Scenario", "SourceText.Greek.Scenario",]
# Specify parts of foldernames plain strings, not regexes
# subfolders_to_include = ["Overall.Run"]
subfolders_to_include = ["Overall.Run1",]# "_2", "Greek","Clone", "GEN_RUT_JON" , "NewToOld",]
#subfolders_to_include = ["PeekAhead"]
subfolders_to_exclude = ["FastAlign", "NMT", "3.3"]

# Set the series to create:
# language_family = 'Afro-Asiatic'

config_filename = "config.yml"
greek_source = "grc-grcsbl"

experiments_folder_str = "S:/eBible/MT/experiments"
experiments_folder = Path(experiments_folder_str)
test_destination_folder = Path("F:/GitHub/BibleNLP/ebible-experiments/MT/experiments")

source_language_family = "Niger-Congo"
source_family_folder = experiments_folder / source_language_family
source_subfolders = [folder for folder in source_family_folder.iterdir()]

if subfolders_to_include:
    print(f"Searching for subfolders to include matching: {subfolders_to_include}")
    source_subfolders = [source_subfolder for source_subfolder in source_subfolders if is_included(source_subfolder.name, includes=subfolders_to_include)]

    if subfolders_to_exclude:
        print(f"Excluding subfolders that match: {subfolders_to_exclude}")
        source_subfolders = [source_subfolder for source_subfolder in source_subfolders if not is_excluded(source_subfolder.name, excludes=subfolders_to_exclude)]

elif subfolders_to_exclude:
    print(f"Excluding subfolders that match: {subfolders_to_exclude}")
    source_subfolders = [source_subfolder for source_subfolder in source_subfolders if not is_excluded(source_subfolder.name, excludes=subfolders_to_exclude)]

print(f"These folders will be used as templates:")
pprint(source_subfolders)


experiments = []
for language_family in language_family_configs_to_create:
    language_family_details = language_families_details[language_family]

    test_destination_family_folder = test_destination_folder / language_family
    destination_family_folder = experiments_folder / language_family   

    for source_subfolder in source_subfolders:
        for source_file in source_subfolder.rglob(config_filename):
            if source_file.is_file():
                
                if not testing:
                    dest_folder = destination_family_folder / source_subfolder.name
                elif testing:
                    dest_folder = test_destination_family_folder / source_subfolder.name
                else:
                    print("Can't determine whether testing is True or False: testing={testing}")
                    exit()                
                
                #print(dest_folder)
                #continue
                destination_file = dest_folder / source_file.name


                # Get the experiment details from the config.yml file.
                with open(source_file, "r") as configfile:
                    config: Dict = yaml.safe_load(configfile)

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

#print(f"\nThere are {len(experiments)} {config_filename} files to create.")
#pprint([experiment["Destination folder"] for experiment in experiments])

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
        #print(f"This related language code {related_code} has this writing system code: {related_ws}")

        config["data"]["lang_codes"][related_code] = related_ws

    if do_copy :
        # Make necessary folders.
        if not experiment["Destination folder"].is_dir():
            experiment["Destination folder"].mkdir(parents=True, exist_ok=True)
            print(f"Created destination folder: {experiment['Destination folder']}")

        # print(destination_config_file.parent , type(destination_config_file.parent))
        new_config_file = experiment["Destination file"]
        with new_config_file.open("w", encoding="utf-8") as file:
            yaml.dump(config, file)
    
        print(f"Wrote out modified config file to : {experiment['Destination file']}")
        pprint(corpus_pairs)
        pprint(data_config["lang_codes"])
        print()
    else:

        print(f"Dry run so nothing written. Would write out modified config file to : {experiment['Destination file']}")
        pprint(corpus_pairs)
        pprint(data_config["lang_codes"])
        print()
        

if not testing:
    print_commands(experiments, experiments_folder_str, test_only=test_only, queue=queue)
else :
    print_commands(experiments, test_destination_folder, test_only=test_only, queue=queue)
