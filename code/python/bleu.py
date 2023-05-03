import csv
import hashlib
import json
import os
import pickle
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import corpus_bleu

matplotlib.use("Qt5Agg")
cache_file = "bleu_score_cache.pkl"
tsv_output_file = "bleu_scores.tsv"

def save_tokenized_file(filepath, tokenized_text):
    tokenized_path = filepath.parent / "tokenized"
    if not tokenized_path.is_file():
        tokenized_path.mkdir(parents=True, exist_ok=True)
        tokenized_filepath = tokenized_path / (filepath.stem + ".tokenized")
        with tokenized_filepath.open("w", encoding="utf-8") as f:
            json.dump(tokenized_text, f)


def load_tokenized_file(filepath):
    tokenized_path = filepath.parent / "tokenized"
    tokenized_filepath = tokenized_path / (filepath.stem + ".tokenized")
    with tokenized_filepath.open("r", encoding="utf-8") as f:
        tokenized_text = json.load(f)
    return tokenized_text


def tokenize_and_save_files(filepaths):
    for filepath in filepaths:
        tokenized_path = filepath.parent / "tokenized"
        tokenized_filepath = tokenized_path / (filepath.stem + ".tokenized")
        if not tokenized_filepath.exists():
            tokenized_text = read_and_tokenize_file(filepath)
            save_tokenized_file(filepath, tokenized_text)


def read_and_tokenize_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        lines = file.readlines()
        tokenized_lines = [word_tokenize(line.lower().strip()) for line in lines]
    return tokenized_lines


def calculate_bleu_score(args):
    ref_tokenized_texts, hyp_tokenized_texts, non_empty_line_indices = args
    return corpus_bleu(
        [[ref_tokenized_texts[index]] for index in non_empty_line_indices],
        [hyp_tokenized_texts[index] for index in non_empty_line_indices],
    )


def compare_files_bleu_multiprocessing(filepaths, cache_file=cache_file):
    num_files = len(filepaths)
    bleu_matrix = np.zeros((num_files, num_files))

    filehashes = [file_hash(filepath) for filepath in filepaths]

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            bleu_score_cache = pickle.load(f)
    else:
        bleu_score_cache = {}

    with Pool() as pool:
        for i in range(num_files):
            tokenized_texts_i = load_tokenized_file(filepaths[i])
            for j in range(num_files):
                if i != j:
                    tokenized_texts_j = load_tokenized_file(filepaths[j])
                    non_empty_line_indices = [
                        index
                        for index, line in enumerate(tokenized_texts_i)
                        if line and tokenized_texts_j[index]
                    ]

                    if non_empty_line_indices:
                        cache_key = get_cache_key(filehashes[i], filehashes[j])
                        if cache_key in bleu_score_cache:
                            bleu_matrix[i, j] = bleu_score_cache[cache_key]
                        else:
                            args = (
                                tokenized_texts_i,
                                tokenized_texts_j,
                                non_empty_line_indices,
                            )
                            bleu_score = pool.apply_async(
                                calculate_bleu_score, args
                            ).get()
                            bleu_matrix[i, j] = bleu_score
                            bleu_score_cache[cache_key] = bleu_score

    with open(cache_file, "wb") as f:
        pickle.dump(bleu_score_cache, f)

    return bleu_matrix


def file_hash(filepath):
    BUF_SIZE = 65536
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


def get_cache_key(filehash_i, filehash_j):
    return f"{filehash_i}-{filehash_j}"


def load_bleu_score_cache(cache_file):
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            bleu_score_cache = pickle.load(f)
    else:
        bleu_score_cache = {}
    return bleu_score_cache


def compare_files_bleu(filepaths, cache_file=cache_file):
    num_files = len(filepaths)
    bleu_matrix = np.zeros((num_files, num_files))

    filehashes = [file_hash(filepath) for filepath in filepaths]

    bleu_score_cache = load_bleu_score_cache(cache_file)

    # Add the filenames key to the cache if it doesn't exist
    if "filenames" not in bleu_score_cache:
        bleu_score_cache["filenames"] = []

    # Update the cache with new filenames
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        if filename not in bleu_score_cache["filenames"]:
            bleu_score_cache["filenames"].append(filename)

    with ProcessPoolExecutor(max_workers=20) as executor:
        for i in range(num_files):
            tokenized_texts_i = load_tokenized_file(filepaths[i])
            for j in range(i + 1, num_files):
                if i != j:
                    tokenized_texts_j = load_tokenized_file(filepaths[j])
                    non_empty_line_indices = [
                        index
                        for index, line in enumerate(tokenized_texts_i)
                        if line and tokenized_texts_j[index]
                    ]

                    if non_empty_line_indices:
                        cache_key = get_cache_key(filehashes[i], filehashes[j])
                        if cache_key in bleu_score_cache:
                            bleu_matrix[i, j] = bleu_score_cache[cache_key]
                        else:
                            bleu_score = executor.submit(
                                calculate_bleu_score,
                                (
                                    tokenized_texts_i,
                                    tokenized_texts_j,
                                    non_empty_line_indices,
                                ),
                            ).result()
                            bleu_matrix[i, j] = bleu_score
                            bleu_score_cache[cache_key] = bleu_score
                else:
                    bleu_score = 1.0
                    bleu_matrix[i, j] = bleu_score
                    bleu_score_cache[cache_key] = bleu_score

    with open(cache_file, "wb") as f:
        pickle.dump(bleu_score_cache, f)

    return bleu_matrix



def compare_files_bleu_original(filepaths, cache_file=cache_file):
    num_files = len(filepaths)
    bleu_matrix = np.zeros((num_files, num_files))

    filehashes = [file_hash(filepath) for filepath in filepaths]

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            bleu_score_cache = pickle.load(f)
    else:
        bleu_score_cache = {}


    for i in range(num_files):
        tokenized_texts_i = load_tokenized_file(filepaths[i])
        for j in range(num_files):
            if i != j:
                tokenized_texts_j = load_tokenized_file(filepaths[j])
                non_empty_line_indices = [
                    index
                    for index, line in enumerate(tokenized_texts_i)
                    if line and tokenized_texts_j[index]
                ]

                if non_empty_line_indices:
                    cache_key = get_cache_key(filehashes[i], filehashes[j])
                    if cache_key in bleu_score_cache:
                        bleu_matrix[i, j] = bleu_score_cache[cache_key]
                    else:
                        bleu_score = corpus_bleu(
                            [[tokenized_texts_i[index]] for index in non_empty_line_indices],
                            [tokenized_texts_j[index] for index in non_empty_line_indices],
                        )
                        bleu_matrix[i, j] = bleu_score
                        bleu_score_cache[cache_key] = bleu_score

    with open(cache_file, "wb") as f:
        pickle.dump(bleu_score_cache, f)

    return bleu_matrix



def plot_heatmap(matrix, labels, title):
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        matrix,
        annot=False,
        vmin=0.0,
        vmax=1.0,
        fmt=".2f",
        cmap="YlGnBu",
        xticklabels=labels,
        yticklabels=labels,
    )
    plt.title(title)
    plt.xlabel("Reference Texts")
    plt.ylabel("Candidate Texts")
    plt.show()


def save_cached_scores_to_tsv(cache_file=cache_file , tsv_output_file=tsv_output_file):

    # Load the cached_scores
    cached_scores = load_bleu_score_cache(cache_file)
    filenames = cached_scores.get("filenames", [])

    # Prepare the output data
    output_data = [[""] + filenames]
    for i, filename_i in enumerate(filenames):
        row = [filename_i]
        for j, filename_j in enumerate(filenames):
            if i == j:
                row.append("1.0")
            else:
                key = get_cache_key(filename_i, filename_j)
                score = cached_scores.get(key, None)
                if score is not None:
                    row.append(str(score))
                else:
                    row.append("")
        output_data.append(row)

    # Save the output data to a TSV file
    with open(tsv_output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerows(output_data)

    print(f"Saved BLEU scores to {tsv_output_file}")
    return


if __name__ == "__main__":

    # List of text file paths to compare
    text_files = [
        "F:/GitHub/BibleNLP/ebible-experiments/Inferred_scripture/aka-aka.txt",
        "F:/GitHub/BibleNLP/ebible-experiments/Inferred_scripture/als-alsSHQ.txt",
        "F:/GitHub/BibleNLP/ebible-experiments/Inferred_scripture/arb-arb-vd.txt",
    ]

    input_folder = Path("F:/GitHub/BibleNLP/ebible-experiments/Inferred_scripture")
    text_files = [file for file in input_folder.glob("*.txt")]


    # Tokenize all the files once, and then there's no need to do that each time.
    #tokenize_and_save_files(text_files)
    
    # Tokenize all the english Bibles for comparison
    #input_folder = Path("F:/GitHub/BibleNLP/ebible-experiments/Inferred_scripture/eng")
    #text_files = [file for file in input_folder.glob("*.txt")]
    #tokenize_and_save_files(text_files)
    #exit()

    #print(f"Found {len(text_files)} text files in folder {input_folder}.")
    #exit()
    # start_time_original = time.time()
    # bleu_matrix_original = compare_files_bleu_original(text_files)
    # end_time_original = time.time()
    # time_taken_original = end_time_original - start_time_original

    # Measure the running time of the parallelized compare_files_bleu function using concurrent.futures
    start_time_parallel = time.time()
    bleu_matrix_parallel = compare_files_bleu(text_files)
    end_time_parallel = time.time()
    time_taken_parallel = end_time_parallel - start_time_parallel

    # Measure the running time of the parallelized compare_files_bleu function using multiprocessing
    # start_time_multiprocessing = time.time()
    # bleu_matrix_multiprocessing = compare_files_bleu_multiprocessing(text_files)
    # end_time_multiprocessing = time.time()
    # time_taken_multiprocessing = end_time_multiprocessing - start_time_multiprocessing

    #print(f"Time taken by original function: {time_taken_original:.2f} seconds")
    print(
        f"Time taken by parallelized function (concurrent.futures): {time_taken_parallel:.2f} seconds"
    )
   # print(
    #    f"Time taken by parallelized function (multiprocessing): {time_taken_multiprocessing:.2f} seconds"
    #)
    
    save_cached_scores_to_tsv()
    
    # Print the BLEU score matrix
    #print("BLEU Score Matrix:")
    #print(bleu_matrix_multiprocessing)

    # Display the BLEU score matrix as a heatmap
    labels = [os.path.basename(file) for file in text_files]
    plot_heatmap(bleu_matrix_parallel, labels, "BLEU Score Heatmap")
