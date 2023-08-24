from pathlib import Path
from typing import Iterable, Iterator, List, Union

from fastapi import UploadFile

from transcripts.custom_types import TextChunk


def files_to_textchunks(
    files: Iterable[UploadFile] | Iterable[Path] | Iterable[str],
) -> Iterator[TextChunk]:
    raise NotImplementedError()
