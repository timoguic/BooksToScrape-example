import io
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

import lxml.etree
import requests

from .config import OUTPUT_DIR


def create_folder_or_raise(dirname):
    dirpath = Path(dirname)
    if not dirpath.exists():
        dirpath.mkdir(exist_ok=True)
    elif not dirpath.is_dir():
        raise FileExistsError("{dirpath} exists and is not a directory!")

    return dirpath


def slugify(txt):
    """ Creates a slug from a string """
    return re.sub(r"[\W_]+", "-", txt.strip().lower())


def url_to_tree(url):
    """ Parse an URL into a LXML tree """
    req = requests.get(url)
    tree = lxml.etree.parse(
        io.BytesIO(req.content), lxml.etree.HTMLParser(encoding="utf-8")
    )

    return tree


def save_image_url_to_file(img_url):
    """ Gets the image at the given URL, and save it to the `images` folder """
    img_path = create_folder_or_raise(Path(OUTPUT_DIR) / "images")

    req = requests.get(img_url, stream=True)
    img_file = Path(urlparse(img_url).path).name

    with open(img_path / img_file, "wb") as fp:
        shutil.copyfileobj(req.raw, fp)
