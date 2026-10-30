import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib3
import os
from datetime import datetime
from urllib.parse import urljoin

# disable SSL warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:

    url = "https://www.bible.com/verse-of-the-day"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        verify=False
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # =====================================================
    # TARGET DIV TEXT
    # =====================================================

    container = soup.find(
        "div",
        class_="border rounded-1 border-l-large border-black mbe-3 mbs-2 plb-1 pli-1 pis-2 dark:border-white"
    )

    # =====================================================
    # TARGET IMAGE DIV
    # =====================================================

    image_div = soup.find(
        "div",
        class_="h-auto w-full flex-none"
    )

    # =====================================================
    # PROCESS TEXT
    # =====================================================

    if container:

        div_text = container.get_text(separator=" ", strip=True)

        today = datetime.now().strftime("%Y-%m-%d")

        new_data = pd.DataFrame([{
            "Date": today,
            "Verse": div_text
        }])

        excel_file = "bible_verse_history.xlsx"
        txt_file = "bible_verse_history.txt"

        # =========================
        # EXCEL
        # =========================

        if os.path.exists(excel_file):

            old_data = pd.read_excel(excel_file)

            final_data = pd.concat(
                [old_data, new_data],
                ignore_index=True
            )

        else:
            final_data = new_data

        final_data.to_excel(excel_file, index=False)

        # =========================
        # TXT
        # =========================

        with open(txt_file, "a", encoding="utf-8") as f:
            f.write(f"{today} | {div_text}\n")

        print("Text berhasil ditambahkan")

    else:
        print("Target div text not found")

    # =====================================================
    # DOWNLOAD IMAGE
    # =====================================================

    if image_div:

        img_tag = image_div.find("img")

        if img_tag and img_tag.get("src"):

            img_url = img_tag.get("src")

            # jika relative URL
            img_url = urljoin(url, img_url)

            print("Image URL:", img_url)

            # folder image
            image_folder = "downloaded_images"

            if not os.path.exists(image_folder):
                os.makedirs(image_folder)

            # nama file berdasarkan tanggal
            image_filename = os.path.join(
                image_folder,
                f"verse_{today}.jpg"
            )

            # download image
            img_response = requests.get(
                img_url,
                headers=headers,
                verify=False
            )

            with open(image_filename, "wb") as f:
                f.write(img_response.content)

            print(f"Image downloaded: {image_filename}")

        else:
            print("IMG tag not found")

    else:
        print("Target image div not found")

except Exception as e:
    print("ERROR:")
    print(e)

#input("Press Enter to exit...")