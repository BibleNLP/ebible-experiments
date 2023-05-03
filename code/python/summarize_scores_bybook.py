#!/usr/bin/python
import argparse
from collections import deque
import csv
import datetime as dt

# from natsort import natsorted
from operator import itemgetter
from pathlib import Path
from pprint import pprint
import re
from typing import Dict
import yaml

scorers = [
    "BLEU",
    "spBLEU",
    "CHRF3",
    "WER",
    "TER",
]

# To Do: Add code to collect the by book scores
# To Do: Remove code for reading preprocessing and training logs.
NT_book_codes = [
    "MAT",
    "MRK",
    "LUK",
    "JHN",
    "ACT",
    "ROM",
    "1CO",
    "2CO",
    "GAL",
    "EPH",
    "PHP",
    "COL",
    "1TH",
    "2TH",
    "1TI",
    "2TI",
    "TIT",
    "PHM",
    "HEB",
    "JAS",
    "1PE",
    "2PE",
    "1JN",
    "2JN",
    "3JN",
    "JUD",
    "REV",
]
OT_book_codes = [
    "GEN",
    "EXO",
    "LEV",
    "NUM",
    "DEU",
    "JOS",
    "JDG",
    "RUT",
    "1SA",
    "2SA",
    "1KI",
    "2KI",
    "1CH",
    "2CH",
    "EZR",
    "NEH",
    "EST",
    "JOB",
    "PSA",
    "PRO",
    "ECC",
    "SNG",
    "ISA",
    "JER",
    "LAM",
    "EZK",
    "DAN",
    "HOS",
    "JOL",
    "AMO",
    "OBA",
    "JON",
    "MIC",
    "NAM",
    "HAB",
    "ZEP",
    "HAG",
    "ZEC",
    "MAL",
]

all_fieldnames = {
    "Alignment": "Alignment",
    "ALL": "ALL",
    "all_chars_count": "All Chars",
    "alphabet_size": "Alphabet",
    "Best steps": "Best steps",
    "bleu": "Bleu train last step",
    "categories": "Term cats",
    "complete": "Complete",
    "config_file": "Config file",
    "coverage_penalty": "Coverage",
    "dict_size": "Dictionary",
    "dictionary": "Create dict",
    "experiment": "Experiment",
    "folder": "Folder",
    "git_commit": "Git commit",
    "guided_alignment_type": "GA type",
    "guided_alignment_weight": "GA weight",
    "include_glosses": "include_glosses",
    "label_smoothing_factor": "Label Smoothing",
    "Last steps": "Last steps",
    "loss": "Loss last step",
    "mirror": "Mirror",
    "parent": "Parent",
    "perplexity": "Perplexity last step",
    "scorer": "Metric",
    "series": "Language Family",
    "Source": "Source",
    "src 1": "Source text 1",
    "src 2": "Source text 2",
    "src_casing": "Source case",
    "src_vocab_size": "Source vocab",
    "step": "Last Train Steps",
    "Target": "Target",
    "terms_train": "Terms",
    "test_size": "Test size",
    "tokens_per_piece": "Tokens per piece",
    "train_size": "Train size",
    "train": "Train terms",
    "trg 1": "Target text 1",
    "trg 2": "Target text 2",
    "trg_casing": "Target case",
    "trg_vocab_size": "Target vocab",
    "val_size": "Val size",
    "vocabulary_size": "Parent Vocab",
    "word_dropout": "Dropout",
    "wwarmup_steps": "Warmup Steps",
}

# Set the final column header names and order
column_headers = [
    "Language Family",
    "Source",
    "Target",
    "Experiment",
    "Train size",
    "Test Size",
    "Val size",
    "Metric",
    "ALL",
]

for OT_book_code in OT_book_codes:
    column_headers.append(OT_book_code)

for NT_book_code in NT_book_codes:
    column_headers.append(NT_book_code)

by_book_columns = {
    "series": "Language Family",
    "Source": "Source",
    "Target": "Target",
    "experiment": "Experiment",
    "train_size": "Train size",
    "test_size": "Test Size",
    "val_size": "Val size",
    "scorer": "Metric",
    "ALL": "Overall",
}
    
for OT_book_code in OT_book_codes:
    by_book_columns[OT_book_code] = OT_book_code

for NT_book_code in NT_book_codes:
    by_book_columns[NT_book_code] = NT_book_code
    
    
csv.register_dialect("default")


def get_config_data(config_file, fieldnames):
    # It is best to pass an effective config file to this function as it will gather
    # more data about the experiment. Passing a config.yml file will collect only
    # the explicit settings and not the defaults that were used.
    #    print(f"Reading {config_file}")

    experiment = {
        "config_file": str(config_file),
        "experiment": config_file.parent.name,
        "folder": config_file.parent,
        "series": config_file.parent.parent.name,
        "complete": False,
    }

    if "git_commit" in fieldnames:
        git_commit = re.match("effective-config-(.*).yml", config_file.name)
        if git_commit:
            # print(f"Found git_commit : {git_commit, git_commit[0], git_commit[1]}")
            experiment["git_commit"] = git_commit[1]

    # print(f"Searching in {config_file}")

    with open(config_file, "r") as conf:
        try:
            config = yaml.load(conf, Loader=yaml.SafeLoader)
        except:
            return None

        if not "data" in config:
            # This probably isn't a config.yml file for one of our experiments.
            experiment["experiment"] = "Invalid - no data section"
            return None

    for value in [
        "parent",
    ]:
        if value in fieldnames and value in config["data"]:
            experiment[value] = config["data"][value]
        else:
            experiment[value] = None

    # The NLLB models use 'model' instead of 'parent'
    if "model" in config:
        experiment["parent"] = config["model"]

    if config["data"]["corpus_pairs"]:
        # print(f"In config file {config_file}: data/corpus_pairs is:")
        # print(config["data"]["corpus_pairs"], type(config["data"]["corpus_pairs"]))
        for pair_count, corpus_pair in enumerate(config["data"]["corpus_pairs"], 1):
            for text in ['src', 'trg']:
                try :
                    experiment[f"{text} {pair_count}"] = corpus_pair[text]
                except KeyError:
                    print(f"Couldn't find data/corpus_pair/{text} key in {config_file}")
                    exit()
            
                experiment[f"trg {pair_count}"] = corpus_pair["trg"]
            if type(corpus_pair["src"]) == type(list()) or type(
                corpus_pair["trg"]
            ) == type(list()):
                return None
                print(
                    f"Config file {config_file} has a list of corpus_pairs:\n{corpus_pair}"
                )
                print(corpus_pair["src"], type(corpus_pair["src"]))

            elif (
                type(corpus_pair["src"]) == type("string")
                and type(corpus_pair["trg"]) == type("string")
                and pair_count == 1
            ):
                experiment["Source"] = corpus_pair["src"][
                    : (corpus_pair["src"]).find("-")
                ]
                experiment["Target"] = corpus_pair["trg"][
                    : (corpus_pair["trg"]).find("-")
                ]

        # print(f"There are {max_pairs} pairs.")
    else:
        # print(f"Omitting experiment:\n{experiment}\nNo corpus_pair was found.")
        return None

    # Add the terms settings to the experiment.
    # Typical terms are {'categories': 'PN', 'dictionary': False, 'include_glosses': True, 'train': False}
    # Any of keys that already exist in the experiment dict will be overwritten.

    if "terms" in fieldnames and "terms" in config["data"]:
        experiment.update(config["data"]["terms"])
        # print(f"Terms are {terms}\n and is of type: {type(terms)}")

    param_values = [
        value
        for value in [
            "label_smoothing_factor",
            "wwarmup_steps",
        ]
        if value in fieldnames
    ]

    if "params" in config:
        for value in param_values:
            if value in config["params"]:
                experiment[value] = config["params"][value]
            else:
                experiment[value] = None
    
    return experiment


def count_lines(file):
    with open(file, 'r') as f:
        return len(f.readlines())
   

def get_set_sizes(experiment):

    # Add code to get the length of the Train, validation and test sets.
    exp_sets = ["test", "val", "train"]
    for exp_set in exp_sets:
        exp_set_file = experiment["folder"] / f"{exp_set}.vref.txt"
        if exp_set_file.is_file():
            set_length = count_lines(exp_set_file)
            experiment[f"{exp_set}_size"] = set_length
        else:
            experiment[f"{exp_set}_size"] = 0

    return experiment
    

def translate_experiment_names(experiment):
    
    replacements = {'Scenario1' : ' Train: MRK',
    'Scenario2' : ' Train: MAT-ACT',
    'Scenario3' : ' Train: NT (-ROM,REV)',
    }

    for search, replace in replacements.items():
        if search in experiment['experiment']:
            experiment['experiment'] = experiment['experiment'].replace(search,replace)
    
    return experiment


def flatten_experiments(experiments, scorers):
    # Each scorer in scores fills a row.
    # The row must be created even if there are no scores for that scorer.

    results = []
    for experiment in experiments:
        if "scores" in experiment:
            scores = experiment.pop("scores")
            #print(scores)
        else :
            scores = dict.fromkeys(scorers, dict())
            #print(scores)
            
        #print(scores)
        for scorer in scorers:
            result_row = experiment.copy()
            result_row["scorer"] = scorer
            for (book, score) in scores[scorer].items():
                result_row[book] = score
            results.append(result_row)
        #pprint(results)
        #exit()
    return results


def write_csv(outfile, row_data, column_headers, mode="w"):
    """Write the data to a csv file."""

    with open(outfile, mode, encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, restval="", extrasaction="ignore", fieldnames=column_headers
        )
        writer.writeheader()
        writer.writerows(row_data)
        writer.writerow({"Language Family": "Written by F:/GitHub/BibleNLP/ebible-experiments/code/python/summarize_scores.py"})
    return None


def get_scores(experiment, scores_file):

    # Get the scores details for the experiment

    # Use this format {experiment:... "scores": {scorer: {book: score}, {book: score} , {scorer: {book:score}}}  }
    # {experiment_details:... "scores":  {"BLEU": {"ALL": score,"GEN", score, ,,,} {"CHRF": {"ALL": score}}
    scores = {}

    with open(scores_file, "r", encoding="utf-8") as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=",")
        for i, row in enumerate(csvreader, 1):

            if row["scorer"] == "BLEU":
                try:
                    score, _ = row["score"].split("/", 1)
                except ValueError:
                    print(f"Can't read the BLEU score on row {i} of file {scores_file}")
                    exit()
            else:
                score = row["score"]

            scorer = row["scorer"]
            book = row["book"]

            if not scorer in scores:
                scores[scorer] = {book: score}
            else:
                scores[scorer][book] = score

    experiment["scores"] = scores
    return experiment


def get_config_files(folders):
    
    experiment_configs = []

    for folder in folders:
        for config in Path(folder).rglob("config.yml"):
            if config.is_file():
                experiment_configs.append(config)

    # Remove duplicate paths (which can easily occur since duplicate or nested folders may be given in the arguments.
    experiment_configs = list(set(experiment_configs))
    return experiment_configs


def get_experiments_config_data(experiment_configs, all_fieldnames)-> list:

    experiments = []
    
    for experiment_config in experiment_configs:
        effective_configs = list(experiment_config.parent.glob("effective-config-*.yml"))

        if effective_configs:
            experiment = get_config_data(
                effective_configs[0], all_fieldnames.keys()
            )
            
            experiment = get_set_sizes(experiment=experiment)

        else:  # Use the config.yml file
            experiment = get_config_data(
                experiment_config, all_fieldnames.keys()
            )
            experiment = get_set_sizes(experiment=experiment)

        if not experiment:
            continue
        else:
            experiment["folder"] = experiment_config.parent

        
        experiments.append(experiment)

    return experiments


def get_scores_data(experiments):
    
    scores_filename_prefix = r"scores-"
    ext = r".csv"
    re_steps = re.compile("scores-(\d*.000)\.csv")
    scores_file_pattern = "**/" + scores_filename_prefix + "*" + ext
    scores_read = 0

    #experiments_with_scores = []
    #print(experiments[0]["folder"], type(experiments[0]["folder"]), type(experiments[0]))

    for experiment in experiments:
        #print(list(experiment["folder"].glob(scores_file_pattern)), type(list(experiment["folder"].glob(scores_file_pattern))))
        
        score_files = list(experiment["folder"].glob(scores_file_pattern))

        best_and_last = [
            int(m.group(1))
            for score_file in score_files
            if (m := re_steps.match(score_file.name))
        ]

        if len(best_and_last) >= 1:
            experiment["Best steps"] = min(best_and_last)
            experiment["Last steps"] = max(best_and_last)
        else:
            experiment["complete"] = False

        if len(score_files) > 0:
            best_scores_file = (
                experiment["folder"] / f"scores-{experiment['Best steps']}.csv"
            )
            # print(f"Best scores file is {best_scores_file}")
            if not best_scores_file.is_file() and best_scores_file.exists():
                print(f"Can't find best scores file {best_scores_file}")
                exit()
            else:
                experiment = get_scores(experiment, best_scores_file)
                experiment["complete"] = True
                scores_read += 1

    #experiments_with_scores.append(experiment)

    return experiments, scores_read

def main() -> None:

    now = dt.datetime.now()

    parser = argparse.ArgumentParser(
        description="Find and summarize SILNLP experiment scores. If both -c and -i are set all experiments are reported."
    )
    parser.add_argument(
        "folders",
        nargs="+",
        help="One or more folders to search recursively for scores. The summary file is stored in a subfolder named results in the first folder.",
    )

    parser.add_argument("--output", type=Path, default=Path("F:/GitHub/BibleNLP/ebible-experiments/results") ,help="folder for summary csv file.")
    args = parser.parse_args()

    try:
        experiment_paths = [Path(exp_path).resolve() for exp_path in args.folders]
    except OSError:

        print(
            f"Could be an S3 bucket. Maybe use copy_eperiments.py to copy the data to a local drive."
        )
        exit()


    if args.output:
        output_path = Path(args.output)
    else:
        output_path = experiment_paths[0] / "results"
    output_path.mkdir(parents=False, exist_ok=True)
    output_filename = f"by_book_scores_summary_{now.year}_{now.month}_{now.day}_{now.hour:02}h{now.minute:02}.csv"
    output_file = output_path / output_filename
    
    #print(f"There are {len(args.folders)} top level folders.")
    config_files = get_config_files(args.folders)
    print(f"Found {len(config_files)} config files.")
    #print(config_files[0])

    # Filter config files.
    config_files = [config_file for config_file in config_files if not "FastAlign" in config_file.parent.name]
    print(f"Found {len(config_files)} ignoring FastAlign")

    experiments = get_experiments_config_data(config_files, all_fieldnames)
    print(f"Read {len(experiments)} experiment config files.")
    #print(experiments[0])

    experiments, with_scores = get_scores_data(experiments)
    
    #print(experiments[0])


    #print(all_fieldnames)
    #print()
    #pprint(experiments[5:10])
#    exit()
        
    results = flatten_experiments(experiments, scorers=scorers)
        
    # Add information about the training data
    #experiments = [translate_experiment_names(experiment) for experiment in experiments]

    # If most of the data is missing from the output it is probably
    # because the fieldnames have not been translated into the column names.
    #print(f"Prior to translating keys")
    #pprint(results[0])
    #exit()

    tr_results = []
    for result in results:
        tr_results.append({by_book_columns[k]: v  for k, v in result.items() if k in by_book_columns})

    #print(f"\nAfter translating keys")
    #pprint(tr_results[0])
    #print(f"\nThese are the output columns:")
    #pprint(list(by_book_columns.values()))
    #exit()
    
    write_csv(output_file, tr_results, column_headers=list(by_book_columns.values()))
    
    print(f"There are {len(experiments)} and {len(scorers)} metrics. There should be {len(experiments) * len(scorers)} rows of results.")
    print(f"There are {len(results)} rows of results.")
    print(f"Read {with_scores} scores files. There should be {with_scores * len(scorers)} rows with scores.")
    print(f"Report written to {output_file}  Includes {len(tr_results)} rows." )
    # print(f"This is the first experiment data:\n{experiments[0]}")
    # print(f"The column headers for the csv file are: {output_fields}")

if __name__ == "__main__":
    main()
# Example commandline
# python ~/scripts/summarize_scores_config_steps.py /home/david/gutenberg/MT/experiements/BT-English/Gela_AE
