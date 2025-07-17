"""Real estate data agent for Bangkok condominiums.

This script scrapes data from two public Thai real estate websites
(LivingInsider and PropertyHub) to collect condominium listings in
Bangkok. It then aggregates the information to produce a basic summary
report. The report can be sent via email on a schedule.

The scraping logic is intentionally lightweight because both sites may
change frequently. Adjust the CSS selectors as necessary.
"""

import json
import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup


@dataclass
class Listing:
    title: str
    price: float
    location: str
    url: str


def scrape_livinginsider() -> List[Listing]:
    """Scrape condominium listings from LivingInsider."""
    listings: List[Listing] = []
    base_url = "https://www.livinginsider.com/mystock.php?action=1"
    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
    except Exception as exc:
        print(f"Error fetching LivingInsider: {exc}")
        return listings

    soup = BeautifulSoup(response.text, "html.parser")
    for item in soup.select(".flex-col"):  # Example selector
        title = item.get_text(strip=True)
        price = 0.0
        location = "Bangkok"
        link = item.find("a")
        url = link["href"] if link else base_url
        listings.append(Listing(title=title, price=price, location=location, url=url))
    return listings


def scrape_propertyhub() -> List[Listing]:
    """Scrape condominium listings from PropertyHub."""
    listings: List[Listing] = []
    base_url = "https://propertyhub.in.th/"
    try:
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
    except Exception as exc:
        print(f"Error fetching PropertyHub: {exc}")
        return listings

    soup = BeautifulSoup(response.text, "html.parser")
    for item in soup.select(".post-item"):  # Example selector
        title_tag = item.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else ""
        price = 0.0
        location = "Bangkok"
        link = item.find("a")
        url = link["href"] if link else base_url
        listings.append(Listing(title=title, price=price, location=location, url=url))
    return listings


def analyze_listings(listings: List[Listing]) -> str:
    """Create a simple report from the listings."""
    if not listings:
        return "No data available."

    df = pd.DataFrame([l.__dict__ for l in listings])
    count = len(df)
    avg_price = df["price"].mean()
    locations = df["location"].value_counts().to_dict()

    report_lines = [
        f"Total listings scraped: {count}",
        f"Average price: {avg_price:,.2f}",
        "Listings by location:",
    ]
    for loc, num in locations.items():
        report_lines.append(f"  {loc}: {num}")
    return "\n".join(report_lines)


def send_email(report: str, config_path: str = "config.json") -> None:
    """Send the report via email using SMTP."""
    try:
        with open(config_path) as f:
            cfg = json.load(f)
    except FileNotFoundError:
        print("Email configuration not found.")
        return

    msg = MIMEText(report)
    msg["Subject"] = "Weekly Bangkok Condominium Report"
    msg["From"] = cfg["from"]
    msg["To"] = cfg["to"]

    try:
        with smtplib.SMTP(cfg["smtp_server"], cfg.get("smtp_port", 587)) as server:
            server.starttls()
            server.login(cfg["username"], cfg["password"])
            server.send_message(msg)
    except Exception as exc:
        print(f"Failed to send email: {exc}")


def main() -> None:
    li_listings = scrape_livinginsider()
    ph_listings = scrape_propertyhub()
    all_listings = li_listings + ph_listings
    report = analyze_listings(all_listings)
    print(report)
    send_email(report)


if __name__ == "__main__":
    main()
