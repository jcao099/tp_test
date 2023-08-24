from typing import List
# https://github.com/google/python-fire/blob/master/docs/guide.md
from fire import Fire
from transcripts.io import files_to_textchunks
from transcripts.infer_products import infer_products, infer_youtube


def products(files: List[str]):
    texts = files_to_textchunks(files)
    return infer_products(texts=texts)


def youtube(files: List[str]):
    texts = files_to_textchunks(files)
    return infer_youtube(texts=texts)


def main():
    return Fire({"products": products, "youtube": youtube})
