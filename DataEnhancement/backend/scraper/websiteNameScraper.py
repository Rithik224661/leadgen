import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urlparse
import logging
from time import sleep
from random import uniform

logger = logging.getLogger(__name__)

def normalize_url(url):
    if not url:
        return ""
    parsed = urlparse(url)
    return parsed.netloc.lower().replace("www.", "").strip("/")

def find_company_website(company_name):
    if not company_name or len(company_name.strip()) == 0:
        return None

    search_engines = [
        {
            'url': 'https://www.google.com/search',
            'params': {'q': f"{company_name} official website"},
            'selector': 'div.g div.yuRUbf > a',
            'domain': 'google.com'
        },
        {
            'url': 'https://search.brave.com/search',
            'params': {'q': f"{company_name} official website"},
            'selector': 'a[href^="http"]',
            'domain': 'brave.com'
        }
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    company_terms = company_name.lower().split()

    for engine in search_engines:
        try:
            logger.info(f"Trying {engine['domain']} for {company_name}")
            sleep(uniform(1, 2))  # Random delay between requests

            response = requests.get(
                engine['url'],
                params=engine['params'],
                headers=headers,
                timeout=10
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            result_links = soup.select(engine['selector'])

            for link in result_links[:5]:  # Check only top 5 results
                href = link.get('href', '').lower()
                if not href or any(x in href for x in ['wikipedia.org', 'linkedin.com', 'facebook.com', 'twitter.com']):
                    continue

                # Clean the URL
                href = href.split('?')[0].strip('/')
                if not href.startswith('http'):
                    continue

                # Score the URL based on company name match
                score = sum(1 for term in company_terms if term in href)
                if score >= len(company_terms) * 0.5:  # At least 50% of company name terms should match
                    return href

        except requests.RequestException as e:
            logger.error(f"Error searching {engine['domain']} for {company_name}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error searching {engine['domain']} for {company_name}: {str(e)}")
            continue

    return None
