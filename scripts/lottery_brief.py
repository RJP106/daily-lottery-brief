#!/usr/bin/env python3
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import sys

EMAIL_ADDRESS = "robertjamespollock1986@gmail.com"
EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT = "robertjamespollock1986@gmail.com"

def search_news(query):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        url = f"https://html.duckduckgo.com/?q={query}&t=h_&ia=web"
        response = requests.get(url, headers=headers, timeout=10)
        results = []
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for result in soup.find_all('div', class_='result'):
                title_elem = result.find('a', class_='result__url')
                snippet_elem = result.find('a', class_='result__snippet')
                if title_elem and snippet_elem:
                    results.append({
                        'title': title_elem.text.strip(),
                        'snippet': snippet_elem.text.strip(),
                        'url': title_elem.get('href', '#')
                    })
        return results[:5]
    except Exception as e:
        print(f"Warning: {e}", file=sys.stderr)
        return []

def generate_brief():
    brief_date = datetime.now().strftime("%A, %B %d, %Y")
    search_topics = {
        "Global Lottery News": "global lottery news today",
        "Irish Gambling Law & Regulation": "Irish gambling law news regulation 2024 2025",
        "FDJ & European Operators": "FDJ lottery news Europe financial",
        "Regulatory & GRAI": "GRAI gambling regulation Ireland lottery",
        "Competitive Threats": "prize draw competitions bookmakers lottery betting",
        "Jackpot & Market Data": "lottery jackpot trends Europe markets"
    }
    
    brief_html = f"""<html><head><style>
body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
.header {{ background: #1a3a52; color: white; padding: 20px; border-radius: 5px; }}
.section {{ margin: 20px 0; border-left: 4px solid #1a3a52; padding-left: 15px; }}
.section h2 {{ color: #1a3a52; margin-top: 0; }}
.article {{ margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 3px; }}
.article-title {{ font-weight: bold; color: #0066cc; }}
.article-snippet {{ font-size: 0.9em; color: #666; margin: 5px 0; }}
</style></head><body>
<div class="header"><h1>🎰 Daily Lottery News Brief</h1><p>{brief_date}</p></div>"""
    
    for section_title, search_query in search_topics.items():
        results = search_news(search_query)
        brief_html += f'<div class="section"><h2>{section_title}</h2>'
        if results:
            for article in results:
                brief_html += f'<div class="article"><div class="article-title">{article["title"]}</div><div class="article-snippet">{article["snippet"]}</div></div>'
        else:
            brief_html += "<p><em>No recent news found.</em></p>"
        brief_html += "</div>"
    
    brief_html += '</body></html>'
    return brief_html

def send_email(html_content):
    try:
        if not EMAIL_PASSWORD:
            print("Error: GMAIL_APP_PASSWORD not set", file=sys.stderr)
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎰 Daily Lottery News Brief - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECIPIENT
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT, msg.as_string())
        print("Email sent!")
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    brief = generate_brief()
    send_email(brief)
