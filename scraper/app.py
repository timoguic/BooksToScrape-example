from csv import DictWriter
from pathlib import Path

from .books import BOOK_FIELDS, books_from_cat_url
from .categories import categories_url
from .config import OUTPUT_DIR, ROOT_URL
from .helpers import create_folder_or_raise


def scrape_all(root_url=None, output_dir=None):
    if not root_url:
        root_url = ROOT_URL

    if not output_dir:
        output_dir = OUTPUT_DIR

    output_path = create_folder_or_raise(output_dir)

    for cat_slug, cat in categories_url(ROOT_URL):
        filepath = output_path / f"{cat_slug}.csv"
        with open(filepath, "w", newline="", encoding="utf-8") as fp:
            writer = DictWriter(fp, fieldnames=BOOK_FIELDS)
            writer.writeheader()

            for book_dict in books_from_cat_url(cat):
                writer.writerow(book_dict)
