import re
from decimal import Decimal
from urllib.parse import urljoin

from .helpers import save_image_url_to_file, url_to_tree

BOOK_FIELDS = [
    "title",
    "product_page_url",
    "product_description",
    "price_excluding_tax",
    "price_including_tax",
    "upc",
    "number_available",
    "img_url",
    "rating_review",
]

ONE_TO_FIVE_DICT_TO_INT = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}


def books_url_from_cat_url(cat_url):
    """ Yields book URLs from a category URL, follows `next` links """
    while cat_url:
        tree = url_to_tree(cat_url)
        books_links = tree.xpath("//article[@class='product_pod']/h3/a")
        for elem in books_links:
            yield urljoin(cat_url, elem.attrib["href"])

        next_link = tree.xpath("//ul[@class='pager']/li[@class='next']/a")
        if next_link:
            # Let's do it again
            cat_url = urljoin(cat_url, next_link[0].attrib["href"])
        else:
            # We are done
            cat_url = False


def books_from_cat_url(cat_url):
    for href in books_url_from_cat_url(cat_url):
        yield get_book_dict_from_url(href)


def get_td_text_from_th_in_book_tree(tree, th_text):
    """ Helper function: returns the text of the td next to the th in the book info table """
    xpath = f"//article[@class='product_page']/table//th[text()='{th_text}']/following-sibling::td"
    return tree.xpath(xpath)[0].text.strip()


def get_book_dict_from_url(book_url):
    """ This is where the parsing happens - and this is where cleanup should happen too :) """

    data = dict.fromkeys(BOOK_FIELDS, None)
    tree = url_to_tree(book_url)

    # Page URL
    data["product_page_url"] = book_url

    # Product desc: sometimes, it is missing
    product_desc_txt = ""

    desc_xpath = "//div[@id='product_description']/following-sibling::p"

    product_desc_elem = tree.xpath(desc_xpath)
    if product_desc_elem:
        product_desc_txt = product_desc_elem[0].text

    data["product_description"] = product_desc_txt

    # UPC code
    data["upc"] = get_td_text_from_th_in_book_tree(tree, "UPC")

    # Convert prices to Decimal
    rgxp_price = r"(\d+).(\d+)"
    p_no_tax = get_td_text_from_th_in_book_tree(tree, "Price (excl. tax)")
    p_elems = re.search(rgxp_price, p_no_tax).groups()
    data["price_excluding_tax"] = Decimal(f"{p_elems[0]}.{p_elems[1]}")

    p_with_tax = get_td_text_from_th_in_book_tree(tree, "Price (incl. tax)")
    p_elems = re.search(rgxp_price, p_no_tax).groups()
    data["price_including_tax"] = Decimal(f"{p_elems[0]}.{p_elems[1]}")

    # Parse the available number to int
    num_avail_label = get_td_text_from_th_in_book_tree(tree, "Availability")
    num_avail_text = re.search(r"(\d+) available", num_avail_label).groups()[0]
    data["number_available"] = int(num_avail_text)

    # Get the img and save it to disk
    img_url = tree.xpath("//div[contains(@class, 'thumbnail')]//img")[0].attrib["src"]
    data["img_url"] = urljoin(book_url, img_url)
    save_image_url_to_file(data["img_url"])

    # Title
    title_xpath = "//div[contains(@class, 'product_main')]/h1"
    data["title"] = tree.xpath(title_xpath)[0].text

    # Ugly conversion from word to int...
    rating_xpath = "//p[contains(@class, 'star-rating')]"
    rating_classes = tree.xpath(rating_xpath)[0].attrib["class"].split()
    rating_classes.remove("star-rating")
    rating_word = str.lower(rating_classes.pop())
    data["rating_review"] = ONE_TO_FIVE_DICT_TO_INT[rating_word]

    # Strip that shit
    for k, v in data.items():
        if type(v) is str:
            data[k] = v.strip()

    return data
