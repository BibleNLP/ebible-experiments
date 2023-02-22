#!/usr/bin/python
import argparse
from collections import deque
import csv
import datetime as dt
#from natsort import natsorted
from operator import itemgetter
from pathlib import Path
from pprint import pprint
import re
import time
import yaml

csv.register_dialect("default")


def find_last_in_file(in_file, pattern, last_n=1):

    lastmatches = deque(maxlen=last_n)

    with open(in_file, "r", encoding="utf-8") as in_file:
        for line in in_file:
            match = re.match(pattern, line)
            if match:
                lastmatches.append(match)

    return lastmatches


def find_first_in_file(in_file, pattern, first_n=1):

    matches = []

    with open(in_file, "r", encoding="utf-8") as in_file:
        for line in in_file:
            match = re.match(pattern, line)
            if match:
                matches.append(match)
                if len(matches) >= first_n:
                    return matches

    return matches


def helper_function(infile, pattern, first_n=1):

    pattern = re.compile(pattern)
    result = find_first_in_file(infile, pattern, first_n)

    if result:
        return result[0].group(1)
    else:
        return None


def get_data_from_process_log(experiment, data):
    """Useful data from preprocess log:
    trainer_interface.cc(458) LOG(INFO) all chars count=2067370
    trainer_interface.cc(479) LOG(INFO) Alphabet size=80
    trainer_interface.cc(480) LOG(INFO) Final character coverage=1
    trainer_interface.cc(512) LOG(INFO) Done! preprocessed 12899 sentences.
    unigram_model_trainer.cc(134) LOG(INFO) Making suffix array...
    unigram_model_trainer.cc(138) LOG(INFO) Extracting frequent sub strings...
    unigram_model_trainer.cc(189) LOG(INFO) Initialized 22602 seed sentencepieces
    trainer_interface.cc(518) LOG(INFO) Tokenizing input sentences with whitespace: 12899
    trainer_interface.cc(528) LOG(INFO) Done! 14756
    unigram_model_trainer.cc(484) LOG(INFO) Using 14756 sentences for EM training

    Near the end:
    INFO:tensorflow:Initialized source input layer:
    INFO:tensorflow: - vocabulary size: 4752
    INFO:tensorflow: - special tokens: BOS=no, EOS=no
    INFO:tensorflow:Initialized target input layer:
    INFO:tensorflow: - vocabulary size: 32000
    INFO:tensorflow: - special tokens: BOS=yes, EOS=yes

    """
    # Get data from the process log if it exists
    preprocess_log = experiment["folder"] / "preprocess.log"

    if preprocess_log.is_file() and preprocess_log.exists():

        re_tokens = re.compile(".*?num_tokens/piece=(\d*\.\d*)")
        tokens_per_pieces = find_last_in_file(preprocess_log, re_tokens, 1)
        for tokens_per_piece in tokens_per_pieces:
            print(tokens_per_piece[0])
        exit()

        if tokens_per_piece:
            experiment["tokens per piece"] = tokens_per_piece[0].group(1)
        else:
            experiment["tokens per piece"] = "Not found"

        for var, pattern in data.items():
            experiment[var] = helper_function(preprocess_log, pattern)

    return experiment


def get_data_from_log(experiment, log, patterns):

    # Get data from a log file.
    # Open log file, and search for the named groups in the patterns.
    # Add the data found to the experiment with the name as the key.

    if log.is_file() and log.exists():
        # print(f"Searching in {log}")
        for pattern in patterns:
            with open(log, "r", encoding="utf-8") as log_file:
                for line in log_file:
                    match = re.match(pattern, line)
                    if match:
                        for named_group, data in match.groupdict().items():
                            experiment[named_group] = data

    return experiment


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
        "score best": 0,
        "score last": 0,
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
            return None, None
        # print(f"These are the details in config file {experiment['config']} ")
        # for k,v in config['data'].items():
        #    print(f"{k}: {v}")
        # exit()

        if not "data" in config:
            # This probably isn't a config.yml file for one of our experiments.
            # experiment["experiment"] = "Invalid - no data section"
            return None, None

    #    pairs = config["data"]["corpus_pairs"]
    #    for i, pair in enumerate(pairs):
    #        print(pair)
    #        experiment[f"corpus_pair_{i}"] = pair

    for value in [
        "parent",
        "parent_use_best",
        "parent_use_vocab",
        "src_vocab_size",
        "trg_vocab_size",
        "src_casing",
        "trg_casing",
        "mirror",
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

            experiment[f"src {pair_count}"] = corpus_pair["src"]
            experiment[f"trg {pair_count}"] = corpus_pair["trg"]

            if type(corpus_pair["src"]) == type(list()) or type(
                corpus_pair["trg"]
            ) == type(list()):
                return None, None
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

    # Add the terms settings to the experiment.
    # Typical terms are {'categories': 'PN', 'dictionary': False, 'include_glosses': True, 'train': False}
    # Any of keys that already exist in the experiment dict will be overwritten.

    if "terms" in fieldnames and "terms" in config["data"]:
        experiment.update(config["data"]["terms"])
        # print(f"Terms are {terms}\n and is of type: {type(terms)}")

    param_values = [
        value
        for value in [
            "coverage_penalty",
            "word_dropout",
            "guided_alignment_type",
            "guided_alignment_weight",
        ]
        if value in fieldnames
    ]

    if "params" in config:
        for value in param_values:
            if value in config["params"]:
                experiment[value] = config["params"][value]
            else:
                experiment[value] = None
    return experiment, pair_count


def write_csv(outfile, row_data, column_headers, mode="w"):
    """Write the data to a csv file."""

    with open(outfile, mode, encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, restval="", extrasaction="ignore", fieldnames=column_headers
        )
        writer.writeheader()
        writer.writerows(row_data)

    return None


def show_progress(i, filecount, timestarted):

    ratio_done = i / filecount
    time_taken = time.time() - timestarted  # seconds
    rate = i / time_taken  # files per second
    if i == filecount:
        print(f"Read {filecount} files in {time_taken:.0f} seconds.")
    else:
        print(f"Read {i} files.\nElapsed time is {time_taken:.0f} seconds.")
        print(f"Estimated time remaining: {(filecount - i) / rate:.0f} seconds.")
    return None

"""
'src 1',
'trg 1',
'src 2'
'trg 2',
'Best steps',
'Best BLEU ALL',
'Best CHRF3 ALL',
'Best WER ALL',
'Best TER ALL',
'Best spBLEU ALL',
'Last steps',
'Last BLEU ALL',
'Last CHRF3 ALL',
'Last WER ALL',
'Last TER ALL',
'Last spBLEU ALL', 
"""

def get_fieldnames():

    # This is the full list of possible fieldnames and their column headings in display order.
    all_fieldnames = {
        "series": "Series",
        "folder": "Folder",
        "experiment": "Experiment",
        "complete": "Complete",
        "parent": "Parent",
        'src 1': "Source 1",
        'trg 1': "Target 1",
        'src 2': "Source 2",
        'trg 2': "Target 2",
        'Best steps': 'Best steps',
        'Best BLEU ALL':'Best BLEU ALL',
        'Best CHRF3 ALL':'Best CHRF3 ALL',
        'Best WER ALL':'Best WER ALL',
        'Best TER ALL':'Best TER ALL',
        'Best spBLEU ALL':'Best spBLEU ALL',
        'Last steps':'Last steps',
        'Last BLEU ALL':'Last BLEU ALL',
        'Last CHRF3 ALL':'Last CHRF3 ALL',
        'Last WER ALL':'Last WER ALL',
        'Last TER ALL':'Last TER ALL',
        'Last spBLEU ALL':'Last spBLEU ALL', 
        "git_commit": "Git commit",
        "train_size": "Train size",
        "val_size": "Val size",
        "test_size": "Test size",
        # Typical terms are {'categories': 'PN', 'dictionary': False, 'include_glosses': True, 'train': False}
        "categories": "Term cats",
        "dictionary": "Create dict",
        "include_glosses": "include_glosses",
        "train": "Train terms",
        "dict_size": "Dictionary",
        "terms_train": "Terms",
        "all_chars_count": "All Chars",
        "alphabet_size": "Alphabet",
        "vocabulary_size": "Parent Vocab",
        "src_casing": "Source case",
        "trg_casing": "Target case",
        "mirror": "Mirror",
        "src_vocab_size": "Source vocab",
        "tokens_per_piece": "Tokens per piece",
        "trg_vocab_size": "Target vocab",
        "coverage_penalty": "Coverage",
        "word_dropout": "Dropout",
        "guided_alignment_type": "GA type",
        "guided_alignment_weight": "GA weight",
        "Alignment": "Alignment",
        "step": "Last Train Steps",
        "loss": "Loss last step",
        "perplexity": "Perplexity last step",
        "bleu": "Bleu train last step",
        "config_file": "Config file",
    }

    # These are the ones to omit from this report.
    omit = [
        "folder",
        "git_commit",
        "train_size",
        "val_size",
        "test_size",
        "categories",
        "dictionary",
        "include_glosses",
        "train",
        "dict_size",
        "terms_train",
        "all_chars_count",
        "alphabet_size",
        "vocabulary_size",
        "src_casing",
        "trg_casing",
        "mirror",
        "src_vocab_size",
        "tokens_per_piece",
        "trg_vocab_size",
        "coverage_penalty",
        "word_dropout",
        "guided_alignment_type",
        "guided_alignment_weight",
        "Alignment",
        "step",
        "loss",
        "perplexity",
        "bleu",
        "config_file",
        "parent_use_best",
        "parent_use_vocab",
        'src_casing'
    ]

    return all_fieldnames, omit


def main() -> None:

    now = dt.datetime.now()
    timestarted = time.time()

    parser = argparse.ArgumentParser(
        description="Find and summarize SILNLP experiment scores. If both -c and -i are set all experiments are reported."
    )
    parser.add_argument(
        "folders",
        nargs="+",
        help="One or more folders to search recursively for scores. The summary file is stored in a subfolder named results in the first folder.",
    )
    
    parser.add_argument("--output", type=Path, help="folder for summary csv file.")

    parser.add_argument(
        "-c",
        "-complete_only",
        action="store_true",
        help="Only report experiments which are complete and have a score file.",
    )
    parser.add_argument(
        "-i",
        "-incomplete_only",
        action="store_true",
        help="Only report experiments which are incomplete and do not have a score file.",
    )
    parser.add_argument(
        "-m",
        "-many-to-many",
        action="store_true",
        help="Include experiments which are many to many.  Not yet implemented.",
    )

    args = parser.parse_args()
    if args.c and args.i:
        args.c = False
        args.i = False

    try:
        experiment_paths = [Path(exp_path).resolve() for exp_path in args.folders]
    except OSError:

        print(
            f"Could be an S3 bucket. Maybe use copy_with_dir.py to copy the data to a local drive."
        )
        exit()

    exp_root_len = 0
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = experiment_paths[0] / "results"

    output_path.mkdir(parents=False, exist_ok=True)

    scores_filename_prefix = r"scores-"
    ext = r".csv"

    re_steps = re.compile("scores-(\d*.000)\.csv")

    scores_file_pattern = "**/" + scores_filename_prefix + "*" + ext
    preprocess_log_pattern = "preprocess.log"
    train_log_pattern = "train.log"

    output_filename = f"scores_summary_{now.year}_{now.month}_{now.day}_{now.hour:02}h{now.minute:02}.csv"
    simple_output_filename = f"scores_summary.csv"
    output_file = output_path / output_filename
    missing_files = output_path / "missing_files.txt"

    experiments = []
    files_missing = []
    effective_config_count = 0
    max_pairs = 0

    experiment_configs = []

    for experiment_path in experiment_paths:
        for config in experiment_path.rglob("config.yml"):
            if config.is_file():
                experiment_configs.append(config)

    total_configs = len(experiment_configs)

    # Remove duplicate paths (which can easily occur since multilple paths may be given in the arguments.
    experiment_configs = list(dict.fromkeys(experiment_configs))
    print(
        f"Found {total_configs} configs initially, {len(experiment_configs)} are left after deduplication."
    )

    all_fieldnames, omit = get_fieldnames()
    included_fieldnames = {fieldname  for fieldname in all_fieldnames if fieldname not in omit}
    column_headers = [column_header for fieldname, column_header in all_fieldnames.items() if fieldname not in omit]

    for experiment_config in experiment_configs:
        experiment_folder = experiment_config.parent
        effective_configs = list(experiment_folder.glob("effective-config-*.yml"))

        if effective_configs:
            effective_config_count += 1
            experiment, no_pairs = get_config_data(effective_configs[0], included_fieldnames)

        else:  # Use the config.yml file
            experiment, no_pairs = get_config_data(experiment_config, included_fieldnames)

        if not experiment:
            continue

        max_pairs = max(max_pairs, no_pairs)

        # Get data from the process log if it exists
        preprocess_log = experiment["folder"] / "preprocess.log"
        if preprocess_log.is_file():

            preprocess_patterns_1 = {
                "Git commit": ".*?INFO - Git commit: (.*)",
                "All chars count": ".*?LOG\(INFO\) all chars count=(.*)",
                "Alphabet size": ".*?LOG\(INFO\) Alphabet size=(.*)",
                "Vocabulary size": ".*?INFO:tensorflow: - vocabulary size: (.*)",
                "Alignment": ".*?INFO - Generating train alignments using (.*)",
                "Train size": ".*?INFO - train size: (\d*?), val size: \d*?, test size: \d*?, dict size: \d*?, terms train size: \d*?",
                "Val size": ".*?INFO - train size: \d*?, val size: (\d*?), test size: \d*?, dict size: \d*?, terms train size: \d*?",
                "Test size": ".*?INFO - train size: \d*?, val size: \d*?, test size: (\d*?), dict size: \d*?, terms train size: \d*?",
                "Dict size": ".*?INFO - train size: \d*?, val size: \d*?, test size: \d*?, dict size: (\d*?), terms train size: \d*?",
                "Terms train size": ".*?INFO - train size: \d*?, val size: \d*?, test size: \d*?, dict size: \d*?, terms train size: (\d*)",
            }

            preprocess_patterns_2 = [
                ".*?INFO - Git commit: (?P<git_commit>.*)",
                ".*?LOG\(INFO\) all chars count=(?P<all_chars_count>.*)",
                ".*?LOG\(INFO\) Alphabet size=(?P<alphabet_size>.*)",
                ".*?INFO:tensorflow: - vocabulary size: (?P<vocabulary_size>.*)",
                ".*?INFO - Generating train alignments using (?P<alignment>.*)",
                ".*?INFO - train size: (?P<train_size>\d*?), val size: (?P<val_size>\d*?), test size: (?P<test_size>\d*?), dict size: (?P<dict_size>\d*?), terms train size: (?P<terms_train>\d*)",
                ".*?num_tokens/piece=(?P<tokens_per_piece>\d*\.\d*)",
            ]
            # Tokens per piece pattern relies of the code finding all references and storing only the last.

            preprocess_patterns = [re.compile(regex) for regex in preprocess_patterns_2]
            experiment = get_data_from_log(
                experiment, preprocess_log, preprocess_patterns
            )

        training_log = experiment["folder"] / "train.log"

        if training_log.is_file():
            training_patterns = [
                re.compile(
                    ".*?Evaluation result for step (?P<step>\d+): loss = (?P<loss>\d+.\d+) ; perplexity = (?P<perplexity>\d+.\d+) ; bleu = (?P<bleu>\d+.\d+)"
                )
            ]
            experiment = get_data_from_log(experiment, training_log, training_patterns)

        score_files = list(experiment["folder"].glob(scores_file_pattern))

        best_and_last = [int(m.group(1)) for score_file in score_files if (m := re_steps.match(score_file.name))]
        if len(best_and_last) >= 1:
            best_steps = min(best_and_last)
            last_steps = max(best_and_last)
        else:
            experiment["complete"] = False

        if len(score_files) > 0:
            experiment["complete"] = True
            # Arrange scores with the factors that make the greatest difference first.
            # i.e. The scorer can give any score, some might be in the range 0-1, or 0-100
            # The length of training (ie. steps) has an impact.
            # I expect the impact from the book to be the smallest impact usually, if the scoring is over the whole book.
            # So {scorer: {experiment: {steps : {book: score}, steps: {book: score}} }}

            scores = {}
            for score_file in score_files:
                m = re_steps.match(score_file.name)
                if m:
                    steps = int(m.group(1))
                    
                    if score_file.is_file() and score_file.exists():
                        with open(score_file, "r", encoding="utf-8") as csvfile:
                            csvreader = csv.DictReader(csvfile, delimiter=",")
                            for i, row in enumerate(csvreader,1):
                                #print(i,row)

                                if row["book"] == "ALL":
                                    if row["scorer"] == "BLEU":
                                        try:
                                            score, _ = row["score"].split("/", 1)   
                                        except ValueError:
                                            print(f"Can't read the BLEU score on row {i} of file {score_file}")
                                            exit()
                                    else:
                                        score = row["score"]

                                    if steps == best_steps:
                                        experiment["Best steps"] = steps
                                        experiment[f"Best {row['scorer']} {row['book']}"] = score
                                    
                                    elif steps == last_steps:
                                        experiment["Last steps"] = steps
                                        experiment[f"Last {row['scorer']} {row['book']}"] = score
                    else:
                        continue

            # if len(scores) > 0:

            #     best_steps = min(scores.keys())
            #     last_steps = max(scores.keys())
            #     print(scores)
            #     experiment["complete"] = True
            #     if "steps best" in included_fieldnames:
            #         experiment["steps best"] = best_steps
            #     if "score best" in included_fieldnames or "score max" in included_fieldnames:
            #         experiment["score best"] = scores[best_steps]["score"]
            #     if "steps last" in included_fieldnames:
            #         experiment["steps last"] = last_steps
            #     if "score last" in included_fieldnames or "score max" in included_fieldnames:
            #         experiment["score last"] = scores[last_steps]["score"]

            #     # print(best_steps, scores[best_steps] , last_steps, scores[last_steps])
            #     if "score max" in included_fieldnames:
            #         experiment["score max"] = max(
            #             experiment["score best"], experiment["score last"]
            #         )

        experiments.append(experiment)

        # If experiments without scores are being reported add them
        # This is useful for finding out the tokens/piece value of a series
        # Where only the preprocessing has been done.

    complete_experiments = [experiment for experiment in experiments if experiment["complete"]]
    incomplete_experiments = [
            experiment for experiment in experiments if not experiment["complete"]
        ]
    
    if args.c:
        write_csv(output_file, complete_experiments, column_headers=column_headers)
        print(f"Wrote results only for the {len(complete_experiments)} experiments with scores to {output_file}")
        print(f"There are {len(incomplete_experiments)} experiments without scores.")

    elif args.i:
        write_csv(output_file, incomplete_experiments, column_headers=column_headers)
        print(f"Wrote results only for the {len(incomplete_experiments)} experiments without scores to {output_file}")
        print(f"There are {len(complete_experiments)} experiments with scores.")

    else:
        write_csv(output_file, experiments, column_headers=column_headers)
        print(f"Report includes all experiments. {len(complete_experiments)} experiments have scores and {len(incomplete_experiments)} do not.")
        

    #print(f"This is the first experiment data:\n{experiments[0]}")

    # print(f"The column headers for the csv file are: {output_fields}")
    #print(f"These are the included_fieldnames\n{column_headers}")

if __name__ == "__main__":
    main()
# Example commandline
# python ~/scripts/summarize_scores_config_steps.py /home/david/gutenberg/MT/experiements/BT-English/Gela_AE
