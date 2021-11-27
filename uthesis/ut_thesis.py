import io
import mimetypes
import time
from collections import namedtuple

import requests
from fake_useragent import UserAgent
from PIL import Image


def fetch_page_data(url):
    headers = {"user_agent": UserAgent().chrome}
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
    next_url = url.replace(current_str, next_str)
    return next_url


def fetch_all_pages(url, max_tries=10):
    all_pages = []
    error_counter = 0

    while error_counter < max_tries:
        page_data = fetch_page_data(url=url)
        if page_data.extension is not None:
            image = Image.open(io.BytesIO(page_data.content))
            all_pages.append(image)
            error_counter = 0
            print(url)
            print(f"Page {len(all_pages)} is done")
        else:
            error_counter += 1
            print(url)
            print(f"Retrying page {len(all_pages)} ...")
        url = find_next_url(url)
        time.sleep(10)

    return all_pages


def save_pdf(all_pages, pdf_path):
    all_pages[0].save(pdf_path, save_all=True, append_images=all_pages[1:])
