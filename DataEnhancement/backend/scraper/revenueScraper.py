import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
import logging
from time import sleep
from random import uniform

logger = logging.getLogger(__name__)

def clean_company_name_variants(name):
    variants = []

    original = name.strip()
    variants.append(original)

    if "&" in original:
        variants.append(original.replace("&", "and"))

    if "-" in original:
        variants.append(original.replace("-", " "))

    no_special = re.sub(r"[^\w\s\-&]", "", original)
    if no_special != original:
        variants.append(no_special)

    normalized_space = " ".join(original.split())
    if normalized_space != original:
        variants.append(normalized_space)

    return list(dict.fromkeys(variants))

def get_company_revenue_from_growjo(company_name, depth=0):
    if not company_name or len(company_name.strip()) == 0:
        return {
            "company": company_name,
            "error": "Invalid company name"
        }

    base_url = "https://growjo.com/company/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }

    name_variants = clean_company_name_variants(company_name)
    logger.info(f"Searching revenue for {company_name} with variants: {name_variants}")

    for name_variant in name_variants:
        try:
            sleep(uniform(1, 2))  # Random delay between requests
            company_url = base_url + quote(name_variant)
            logger.info(f"Trying URL: {company_url}")

            res = requests.get(company_url, headers=headers, timeout=15)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            page_text = soup.get_text().lower()

            if (
                "page not found" in page_text or 
                "company not found" in page_text or 
                "rank not available" in page_text
            ):
                logger.info(f"No match found for variant: {name_variant}")
                continue

            # Look for revenue in multiple places
            revenue = "<$5M"  # Default value
            revenue_patterns = [
                r"estimated annual revenue[:\s]*([\$\d\.]+[KMB]?)",
                r"revenue[:\s]*([\$\d\.]+[KMB]?)",
                r"([\$\d\.]+[KMB]?)[\s]*annual revenue"
            ]

            # Try to find revenue in list items first
            for li in soup.find_all("li"):
                text = li.get_text(strip=True)
                if "revenue" in text.lower():
                    for pattern in revenue_patterns:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            revenue = match.group(1)
                            break
                    if revenue != "<$5M":
                        break

            # If not found in list items, try other elements
            if revenue == "<$5M":
                for pattern in revenue_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        revenue = matches[0]
                        break

            # Normalize revenue format
            revenue = revenue.upper().replace(" ", "")
            if not revenue.startswith("$"):
                revenue = "$" + revenue

            result = {
                "company": company_name,
                "matched_variant": name_variant,
                "estimated_revenue": revenue,
                "url": company_url,
                "source": "growjo"
            }

            logger.info(f"Found revenue for {company_name}: {result}")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"Timeout while fetching {company_url}")
            continue
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {company_url}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error for {company_url}: {str(e)}")
            continue

    # Fallback to default value
    logger.warning(f"No revenue found for {company_name}, using fallback value")
    return {
        "company": company_name,
        "source": "fallback",
        "estimated_revenue": "<$5M",
        "attempted_variants": name_variants
    }

# Example test
if __name__ == "__main__":
    result = get_company_revenue_from_growjo("Louis Dreyfus")
    print(result)
