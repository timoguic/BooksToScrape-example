from urllib.parse import urljoin

from .helpers import slugify, url_to_tree


def categories_url(root_url):
    """ Yields URLs for categories """
    tree = url_to_tree(root_url)
    cat_list = tree.xpath("//div[@class='side_categories']/ul//li/a")

    for elem in cat_list:
        if elem.text.strip().lower() == "books":
            continue

        yield slugify(elem.text), urljoin(root_url, elem.attrib["href"])
