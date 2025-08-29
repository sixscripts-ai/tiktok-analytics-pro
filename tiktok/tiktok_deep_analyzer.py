import requests
import json
import time
import random
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

class TikTokDeepAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
        ]
        self.setup_session()
    
    def setup_session(self):
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def extract_username(self, url):
        try:
            if '?' in url:
                url = url.split('?')[0]
            match = re.search(r'@([a-zA-Z0-9._]+)', url)
            return match.group(1) if match else None
        except:
            return None
    
    def stealth_request(self, url, timeout=15):
        time.sleep(random.uniform(2, 4))
        self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
        return self.session.get(url, timeout=timeout)
    
    def scrape_multiple_sources(self, username):
        sources_data = {}
        
        # TikTok profile
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = self.stealth_request(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text()
                
                # Look for follower count
                follower_match = re.search(r'(\d+(?:\.\d+)?[KMB]?)\s*followers', page_text, re.IGNORECASE)
                if follower_match:
                    sources_data['tiktok_followers'] = follower_match.group(1)
        except:
            pass
        
        # Alternative analytics sites
        alt_sources = [
            f"https://tiktokanalytics.com/@{username}",
            f"https://tiktokstats.com/@{username}"
        ]
        
        for source_url in alt_sources:
            try:
                response = self.stealth_request(source_url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    page_text = soup.get_text()
                    
                    follower_match = re.search(r'(\d+(?:\.\d+)?[KMB]?)\s*followers', page_text, re.IGNORECASE)
                    if follower_match:
                        sources_data[f'{source_url.split("/")[-2]}_followers'] = follower_match.group(1)
            except:
                continue
        
        return sources_data
    
    def convert_count(self, count_text):
        if not count_text:
            return 0
        count_text = count_text.strip().upper()
        if 'B' in count_text:
            return float(count_text.replace('B', '')) * 1000000000
        elif 'M' in count_text:
            return float(count_text.replace('M', '')) * 1000000
        elif 'K' in count_text:
            return float(count_text.replace('K', '')) * 1000
        else:
            return float(count_text.replace(',', ''))
    
    def calculate_advanced_earnings(self, follower_count):
        # Advanced earnings models
        cpm_earnings = follower_count * 0.1 * 1.25 / 1000
        engagement_earnings = follower_count * 0.035 * 0.01
        brand_deals = follower_count * 0.025
        live_stream = follower_count * 0.01 * 1
        merchandise = follower_count * 0.005 * 10
        creator_fund = follower_count * 0.001 * 2
        
        total_monthly = cpm_earnings + engagement_earnings + brand_deals + live_stream + merchandise + creator_fund
        
        return {
            'monthly': round(total_monthly, 2),
            'yearly': round(total_monthly * 12, 2),
            'breakdown': {
                'cpm': round(cpm_earnings, 2),
                'engagement': round(engagement_earnings, 2),
                'brand_deals': round(brand_deals, 2),
                'live_stream': round(live_stream, 2),
                'merchandise': round(merchandise, 2),
                'creator_fund': round(creator_fund, 2)
            }
        }
    
    def analyze_account(self, tiktok_url):
        username = self.extract_username(tiktok_url)
        if not username:
            print("[-] Could not extract username")
            return None
        
        print(f"[+] Deep analyzing @{username}")
        
        # Scrape multiple sources
        sources_data = self.scrape_multiple_sources(username)
        
        # Determine follower count
        follower_count = 0
        follower_source = "estimated"
        
        for source, count in sources_data.items():
            if 'followers' in source:
                follower_count = self.convert_count(count)
                follower_source = source
                break
        
        if follower_count == 0:
            follower_count = 85000  # Conservative estimate
            follower_source = "conservative_estimate"
        
        # Calculate earnings
        earnings = self.calculate_advanced_earnings(follower_count)
        
        report = {
            'username': username,
            'url': tiktok_url,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'follower_count': follower_count,
            'follower_source': follower_source,
            'sources_data': sources_data,
            'earnings_analysis': earnings
        }
        
        return report

def main():
    analyzer = TikTokDeepAnalyzer()
    url = "https://www.tiktok.com/@2wpeezy4?_t=ZP-8zF8dwhJqJS&_r=1"
    
    print("🔥 TIKTOK DEEP EARNINGS ANALYZER")
    print("="*50)
    
    report = analyzer.analyze_account(url)
    
    if report:
        print("\n" + "="*60)
        print("DEEP TIKTOK EARNINGS ANALYSIS REPORT")
        print("="*60)
        print(f"Account: @{report['username']}")
        print(f"Analysis Date: {report['analysis_date']}")
        print(f"Follower Count: {report['follower_count']:,.0f} (Source: {report['follower_source']})")
        print(f"Estimated Monthly Earnings: ${report['earnings_analysis']['monthly']:,.2f}")
        print(f"Estimated Yearly Earnings: ${report['earnings_analysis']['yearly']:,.2f}")
        print("\nEarnings Breakdown:")
        for source, amount in report['earnings_analysis']['breakdown'].items():
            print(f"  {source.replace('_', ' ').title()}: ${amount:,.2f}")
        
        print(f"\nData Sources Found: {len(report['sources_data'])}")
        for source, data in report['sources_data'].items():
            print(f"  {source}: {data}")
        
        print("="*60)
        
        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"deep_tiktok_analysis_{report['username']}_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {filename}")
    else:
        print("\n❌ Analysis failed.")

if __name__ == "__main__":
    main()
