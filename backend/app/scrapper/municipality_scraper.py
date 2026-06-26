from playwright.sync_api import sync_playwright
import pandas as pd
import time


BASE_URL = "https://mofaga.gov.np"

urls = []

# Municipality + Rural Municipality pages
for i in range(1, 8):
    urls.append({
        "type": "Municipality",
        "url": f"{BASE_URL}/local-contact/mun-prov-{i}"
    })

    urls.append({
        "type": "Rural Municipality",
        "url": f"{BASE_URL}/local-contact/village-mun-prov-{i}"
    })


def get_max_page(page):
    pages = []

    for a in page.query_selector_all("a"):
        txt = a.inner_text().strip()

        if txt.isdigit():
            pages.append(int(txt))

    if pages:
        return max(pages)

    return 1


def scrape_page_rows(page, local_type):
    results = []

    rows = page.query_selector_all("table tbody tr")

    for row in rows:
        cols = row.query_selector_all("td")

        if len(cols) < 7:
            continue

        try:
            province = cols[1].inner_text().strip()
            municipality = cols[2].inner_text().strip()
            district = cols[3].inner_text().strip()

            link = row.query_selector("a")
            website = link.get_attribute("href") if link else ""

            email = cols[5].inner_text().strip()
            phone = cols[6].inner_text().strip()

            results.append({
                "province": province,
                "district": district,
                "municipality": municipality,
                "type": local_type,
                "website": website,
                "email": email,
                "phone": phone
            })

        except Exception as e:
            print("Row error:", e)

    return results


def run():
    all_results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        for item in urls:

            print("\n" + "=" * 60)
            print("Scraping:", item["url"])

            page.goto(item["url"], wait_until="networkidle")
            page.wait_for_timeout(5000)

            max_page = get_max_page(page)

            print("Pages found:", max_page)

            # Page 1
            all_results.extend(
                scrape_page_rows(page, item["type"])
            )

            # Remaining pages
            for page_num in range(2, max_page + 1):

                try:
                    print(f"Page {page_num}")

                    page.get_by_text(
                        str(page_num),
                        exact=True
                    ).click()

                    page.wait_for_timeout(3000)

                    all_results.extend(
                        scrape_page_rows(page, item["type"])
                    )

                except Exception as e:
                    print(
                        f"Pagination error page {page_num}:",
                        e
                    )

        browser.close()

    df = pd.DataFrame(all_results)

    df = df.drop_duplicates()

    print("\nTOTAL RECORDS:", len(df))

    df.to_csv(
        r"C:\Users\shiri\scraper_ai_system\backend\app\automations",
        index=False,
        encoding="utf-8-sig"
    )

    print("Saved -> nepal_local_governments.csv")


if __name__ == "__main__":
    run()