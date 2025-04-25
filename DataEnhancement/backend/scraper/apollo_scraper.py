import requests
import os
import logging
from time import sleep
from random import uniform
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
if not APOLLO_API_KEY:
    logger.warning("APOLLO_API_KEY not found in environment variables")

def extract_domain(url):
    """Extract domain from URL."""
    if not url:
        return None
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        domain = domain.lower().replace('www.', '')
        return domain
    except Exception as e:
        logger.error(f"Error extracting domain from {url}: {str(e)}")
        return None

def enrich_single_company(url_or_domain):
    """Call Apollo API to enrich company data."""
    if not APOLLO_API_KEY:
        return {"error": "Apollo API key not configured"}

    if not url_or_domain:
        return {"error": "No URL or domain provided"}

    # Extract domain if a URL was provided
    domain = extract_domain(url_or_domain) if url_or_domain.startswith('http') else url_or_domain
    if not domain:
        return {"error": f"Could not extract domain from {url_or_domain}"}

    url = "https://api.apollo.io/api/v1/organizations/enrich"
    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "X-Api-Key": APOLLO_API_KEY
    }
    params = {"domain": domain}
    
    try:
        logger.info(f"Enriching data for domain: {domain}")
        sleep(uniform(1, 2))  # Random delay between requests

        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if not data.get("organization"):
            logger.warning(f"No organization data found for {domain}")
            return {
                "domain": domain,
                "error": "No organization data found",
                "source": "apollo"
            }

        org = data["organization"]
        result = {
            "domain": domain,
            "name": org.get("name", ""),
            "website_url": org.get("website_url", ""),
            "linkedin_url": org.get("linkedin_url", ""),
            "founded_year": org.get("founded_year", ""),
            "annual_revenue_printed": org.get("annual_revenue_printed", ""),
            "employees_count": org.get("employees_count", ""),
            "industry": org.get("industry", ""),
            "location": org.get("location", ""),
            "source": "apollo"
        }

        # Clean up empty values
        result = {k: v for k, v in result.items() if v not in ["", None]}
        logger.info(f"Successfully enriched data for {domain}")
        return result

    except requests.exceptions.Timeout:
        logger.error(f"Timeout while enriching {domain}")
        return {"domain": domain, "error": "Request timed out", "source": "apollo"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error for {domain}: {str(e)}")
        return {"domain": domain, "error": str(e), "source": "apollo"}
    except Exception as e:
        logger.error(f"Unexpected error for {domain}: {str(e)}")
        return {"domain": domain, "error": str(e), "source": "apollo"}