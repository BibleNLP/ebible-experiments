""" Find all the config files and effective config files
in a folder. Save certain details for comparison."""

import shutil
from pathlib import Path
from pprint import pprint
from typing import Dict

import yaml


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

# ["NewToOld.GEN_RUT_JON", "Overall.Run", "PartialNT.Scenario",""NewToOld", "RelatedLanguage.PartialNT.Scenario", "SourceText.Greek.Scenario",]
# Specify parts of foldernames plain strings, not regexes
# subfolders_to_include = ["Overall.Run"]
#subfolders_to_include = ["Overall.Run", "_2", "Greek","Clone", "GEN_RUT_JON" , "NewToOld",]
#subfolders_to_include = ["RelatedLanguage.PartialNT.Scenario"]

config_filename = "config.yml"
greek_source = "grc-grcsbl"

experiments_folder_str = "S:/eBible/MT/experiments"
experiments_folder = Path(experiments_folder_str)

family_folders = [experiments_folder / language_family for language_family in language_families]

#pprint(source_files)
#print(f"There are {len(source_files)} config files found.")


#filtered_source_subfolders = [source_subfolder for source_subfolder in source_subfolders if not is_excluded(source_subfolder.name, excludes=subfolders_to_include)]
#included_source_subfolders = [source_subfolder for source_subfolder in source_subfolders if is_included(source_subfolder.name, includes=subfolders_to_include)]

# Choose included or filtered folders
#source_subfolders = filtered_source_subfolders
#source_subfolders = included_source_subfolders

#language_families_to_omit = []
#language_families_to_omit.append(source_language_family)
#language_families = [language_family for language_family in language_families if not is_excluded(language_family, language_families_to_omit)]
      
experiments = []
for family_folder in family_folders:
    series_folders = [folder for folder in family_folder.iterdir()]
    for series_folder in series_folders:
        config_file = series_folder / "config.yml"
        if not config_file.is_file():
            continue

        effect_configs = [effect_config for effect_config in series_folder.glob("effective-config*.yml")][0]
        scores = [score_file for score_file in  series_folder.glob("scores*.csv")]
        print(config_file, effect_configs, scores)
        
        with open(source_file, "r") as configfile:
            config: Dict = yaml.safe_load(configfile)

        exp_family, exp_series = str(source_file.parent)[len(experiments_folder_str)+1:].split('\\')

        experiment = {
                    "Source file": source_file,
                    "Experiment family": exp_family,
                    "Experiment series": exp_series,
                    }


        data_config: dict = config["data"]
        corpus_pairs = data_config["corpus_pairs"]
        experiment["src1"] = corpus_pairs[0]["src"]
        experiment["trg1"] = corpus_pairs[0]["trg"]
        if len(corpus_pairs) == 2:
            experiment["src2"] = corpus_pairs[1]["src"]
            experiment["trg2"] = corpus_pairs[1]["trg"]
        experiment["lang_codes"] = data_config["lang_codes"]

        experiments.append(experiment)

        print(f"\nFound {len(experiments)} {config_filename} files.")
        pprint(experiments[0])
