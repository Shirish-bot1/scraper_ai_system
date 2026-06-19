
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin
# import re
# import csv

# HEADERS = {
#     "User-Agent": "Mozilla/5.0"
# }


# def clean(text):
#     return re.sub(r"\s+", " ", text).strip()


# def get_soup(url):
#     r = requests.get(url, headers=HEADERS, timeout=60)
#     r.raise_for_status()
#     return BeautifulSoup(r.text, "html.parser")


# def find_janapratinidhi_page(base_url):
#     soup = get_soup(base_url)

#     keywords = [
#         "जनप्रतिनिधि",
#         "elected officials",
#         "elected-officials",
#         "mayor",
#         "deputy mayor",
#         "अध्यक्ष",
#         "उपाध्यक्ष"
#     ]

#     for a in soup.find_all("a", href=True):
#         text = clean(a.get_text()).lower()
#         href = a.get("href", "")

#         for key in keywords:
#             if key.lower() in text or key.lower() in href.lower():
#                 return urljoin(base_url, href)

#     return None


# def extract_official_data(url):
#     soup = get_soup(url)

#     result = {
#         "province": "",
#         "municipality_name": "",
#         "head_name": "",
#         "head_phone": "",
#         "head_email": "",
#         "deputy_name": "",
#         "deputy_phone": "",
#         "deputy_email": "",
#     }

#     text = soup.get_text("\n", strip=True)
#     lines = [clean(x) for x in text.split("\n") if clean(x)]
     
#     title = clean(soup.title.get_text()) if soup.title else ""

#     search_text = title + "\n" + text

#     municipality_patterns = [
#     r"([^\n]+ नगरपालिका)",
#     r"([^\n]+ गाउँपालिका)",
#     r"([^\n]+ Municipality)",
#     r"([^\n]+ Rural Municipality)"
#     ]

#     for pattern in municipality_patterns:
#         match = re.search(pattern, search_text, re.IGNORECASE)

#         if match:
#            result["municipality_name"] = clean(match.group(1))
#            break
#     province_keywords = [
#     "कोशी प्रदेश",
#     "मधेश प्रदेश",
#     "बागमती प्रदेश",
#     "गण्डकी प्रदेश",
#     "लुम्बिनी प्रदेश",
#     "कर्णाली प्रदेश",
#     "सुदूरपश्चिम प्रदेश",
#     "Koshi Province",
#     "Madhesh Province",
#     "Bagmati Province",
#     "Gandaki Province",
#     "Lumbini Province",
#     "Karnali Province",
#     "Sudurpashchim Province"
#     ]

#     for province in province_keywords:
#         if province.lower() in search_text.lower():
#            result["province"] = province
#            break

#     head_keywords = [
#         "mayor",
#         "नगर प्रमुख",
#         "नगरप्रमुख",
#         "अध्यक्ष"
#     ]

#     deputy_keywords = [
#         "deputy mayor",
#         "उप प्रमुख",
#         "उप– प्रमुख",
#         "उपप्रमुख",
#         "उपाध्यक्ष"
#     ]

#     for i, line in enumerate(lines):

#         line_lower = line.lower()

#         # Mayor / Chairperson
#         if any(k.lower() in line_lower for k in head_keywords):

#             if i > 0 and not result["head_name"]:
#                 result["head_name"] = lines[i - 1]

#             for j in range(i, min(i + 10, len(lines))):
#                 phone = re.search(r"(98\d{8}|97\d{8})", lines[j])

#                 if phone:
#                     result["head_phone"] = phone.group()
#                     break

#         # Deputy Mayor / Vice Chairperson
#         if any(k.lower() in line_lower for k in deputy_keywords):

#             if i > 0 and not result["deputy_name"]:
#                 result["deputy_name"] = lines[i - 1]

#             for j in range(i, min(i + 10, len(lines))):
#                 phone = re.search(r"(98\d{8}|97\d{8})", lines[j])

#                 if phone:
#                     result["deputy_phone"] = phone.group()
#                     break

#     # Extract emails
#     emails = re.findall(
#         r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
#         text
#     )

#     if emails:
#         result["head_email"] = emails[0]

#         if len(emails) > 1:
#             result["deputy_email"] = emails[1]
#         else:
#             result["deputy_email"] = emails[0]

#     return result


# def scrape_municipality(base_url):
#     print("Checking homepage...")

#     data = extract_official_data(base_url)

#     if data["head_name"] and data["deputy_name"]:
#         return data

#     print("Not found on homepage. Searching Janapratinidhi page...")

#     jp_url = find_janapratinidhi_page(base_url)

#     if jp_url:
#         print("Found:", jp_url)
#         return extract_official_data(jp_url)

#     return data
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import urllib3

# Suppress warnings from bypassing SSL verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def get_soup(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60, verify=False)
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser")
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < retries - 1:
                time.sleep(5)
            else:
                raise
        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                time.sleep(5)
            else:
                raise

def find_janapratinidhi_page(base_url):
    soup = get_soup(base_url)
    keywords = ["जनप्रतिनिधि", "elected officials", "elected-officials", "mayor", "deputy mayor", "अध्यक्ष", "उपाध्यक्ष"]
    for a in soup.find_all("a", href=True):
        text = clean(a.get_text()).lower()
        href = a.get("href", "")
        for key in keywords:
            if key.lower() in text or key.lower() in href.lower():
                return urljoin(base_url, href)
    return None

def extract_official_data(url):
    soup = get_soup(url)
    result = {
        "province": "", "municipality_name": "", "head_name": "", "head_phone": "",
        "head_email": "", "deputy_name": "", "deputy_phone": "", "deputy_email": "",
    }
    text = soup.get_text("\n", strip=True)
    lines = [clean(x) for x in text.split("\n") if clean(x)]
    title = clean(soup.title.get_text()) if soup.title else ""
    search_text = title + "\n" + text

    municipality_patterns = [r"([^\n]+ नगरपालिका)", r"([^\n]+ गाउँपालिका)", r"([^\n]+ Municipality)", r"([^\n]+ Rural Municipality)"]
    for pattern in municipality_patterns:
        match = re.search(pattern, search_text, re.IGNORECASE)
        if match:
           result["municipality_name"] = clean(match.group(1))
           break

    province_keywords = ["कोशी प्रदेश", "मधेश प्रदेश", "बागमती प्रदेश", "गण्डकी प्रदेश", "लुम्बिनी प्रदेश", "कर्णाली प्रदेश", "सुदूरपश्चिम प्रदेश", "Koshi Province", "Madhesh Province", "Bagmati Province", "Gandaki Province", "Lumbini Province", "Karnali Province", "Sudurpashchim Province"]
    for province in province_keywords:
        if province.lower() in search_text.lower():
           result["province"] = province
           break

    head_keywords = ["mayor", "नगर प्रमुख", "नगरप्रमुख", "अध्यक्ष"]
    deputy_keywords = ["deputy mayor", "उप प्रमुख", "उप– प्रमुख", "उप-प्रमुख", "उपप्रमुख", "उपाध्यक्ष"]

    def is_valid_name(s):
        if not s or '@' in s or re.search(r'\d', s) or len(s) > 40: return False
        return True

    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(k in line_lower for k in head_keywords) and not result["head_name"]:
            if i + 1 < len(lines) and is_valid_name(lines[i + 1]): result["head_name"] = lines[i + 1]
            elif i > 0 and is_valid_name(lines[i - 1]): result["head_name"] = lines[i - 1]
            for j in range(i, min(i + 10, len(lines))):
                if not result["head_phone"]:
                    phone = re.search(r"(98\d{8}|97\d{8})", lines[j])
                    if phone: result["head_phone"] = phone.group()
                if not result["head_email"]:
                    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", lines[j])
                    if email: result["head_email"] = email.group()

        if any(k in line_lower for k in deputy_keywords) and not result["deputy_name"]:
            if i + 1 < len(lines) and is_valid_name(lines[i + 1]): result["deputy_name"] = lines[i + 1]
            elif i > 0 and is_valid_name(lines[i - 1]): result["deputy_name"] = lines[i - 1]
            for j in range(i, min(i + 10, len(lines))):
                if not result["deputy_phone"]:
                    phone = re.search(r"(98\d{8}|97\d{8})", lines[j])
                    if phone: result["deputy_phone"] = phone.group()
                if not result["deputy_email"]:
                    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", lines[j])
                    if email: result["deputy_email"] = email.group()
    return result

def scrape_municipality(base_url):
    try:
        data = extract_official_data(base_url)
    except Exception:
        return {"province": "", "municipality_name": "", "head_name": "", "head_phone": "", "head_email": "", "deputy_name": "", "deputy_phone": "", "deputy_email": ""}

    if data["head_name"] and data["deputy_name"]:
        return data

    try:
        jp_url = find_janapratinidhi_page(base_url)
        if jp_url:
            return extract_official_data(jp_url)
    except Exception:
        pass

    return data