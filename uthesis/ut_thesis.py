import io
import mimetypes
import random
import time
from collections import namedtuple

import requests
from fake_useragent import UserAgent
from PIL import Image


def ut_thesis_first_page_url(thesis_id):
    parent_dir = "https://utdlib.ut.ac.ir/DigitalFiles/PdfPage/"
    first_page_dir = "?pn=1&pc="
    url = parent_dir + str(thesis_id) + first_page_dir
    return url


def fetch_page_data(thesis_id, url=None):
    headers = {"user_agent": UserAgent().chrome}
    if url is not None:
        response = requests.get(url=url, headers=headers)
    else:
        url = ut_thesis_first_page_url(thesis_id)
        response = requests.get(url=url, headers=headers)
    content = response.content
    extension = mimetypes.guess_extension(response.headers["content-type"])
    PageData = namedtuple("PageData", ["response", "content", "extension"])
    page_data = PageData(response, content, extension)
    return page_data


def find_next_url(url):
    pn_index_start = url.find("?pn=") + 4
    pn_index_finish = url.find("&pc=")
    current_str = url[pn_index_start:pn_index_finish]
    next_str = str(int(url[pn_index_start:pn_index_finish]) + 1)
    next_url = url[:pn_index_start] + f"{next_str}" + url[pn_index_finish:]
    return next_url


def fetch_all_pages(
    thesis_id, url=None, max_tries=10, random_sleep_time=True, custom_sleep_time=10
):
    all_pages = []
    error_counter = 0

    while error_counter < max_tries:
        if url is not None:
            page_data = fetch_page_data(url=url)
        else:
            page_data = fetch_page_data(thesis_id=thesis_id)
        if page_data.extension is not None:
            image = Image.open(io.BytesIO(page_data.content))
            all_pages.append(image)
            error_counter = 0
            url = find_next_url(url)
            print(url)
            print(f"Page {len(all_pages)} is done")
        else:
            error_counter += 1
            print(url)
            print(f"Retrying page {len(all_pages)} ...")

        if random_sleep_time:
            time.sleep(random.randint(1, 10))
        else:
            time.sleep(custom_sleep_time)

    return all_pages


def save_pdf(all_pages, pdf_path):
    all_pages[0].save(pdf_path, save_all=True, append_images=all_pages[1:])
