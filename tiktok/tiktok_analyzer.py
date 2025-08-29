import json
import time
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re

from tiktok_scraping_scripts.network.session_manager import create_session

class TikTokEarningsAnalyzer:
    def __init__(self):
        self.session = create_session()
    
    def extract_username(self, url):
        try:
            # Handle TikTok URLs with query parameters
            if '?' in url:
                url = url.split('?')[0]
            
            # Extract username from various TikTok URL formats
            patterns = [
                r'@([a-zA-Z0-9._]+)',
                r'tiktok\.com/@([a-zA-Z0-9._]+)',
                r'/([a-zA-Z0-9._]+)\?'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"[-] Username extraction error: {e}")
            return None
    
    def scrape_tiktok_profile(self, username):
        print(f"[+] Attempting to scrape TikTok profile for @{username}")
        try:
            url = f"https://www.tiktok.com/@{username}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for follower count and other metrics
                data = {}
                
                # Try to find follower count in various formats
                follower_patterns = [
                    r'(\d+(?:\.\d+)?[KMB]?)\s*followers',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*粉丝',
                    r'follower[^0-9]*(\d+(?:\.\d+)?[KMB]?)',
                ]
                
                page_text = soup.get_text()
                for pattern in follower_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        data['followers'] = match.group(1)
                        break
                
                return data
            else:
                print(f"[-] TikTok profile request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[-] TikTok profile scraping error: {e}")
            return None
    
    def scrape_socialblade(self, username):
        print(f"[+] Scraping SocialBlade data for @{username}")
        try:
            url = f"https://socialblade.com/tiktok/user/{username}/monthly"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                data = {}
                
                # Extract earnings estimates
                earnings_elements = soup.find_all('div', class_='YouTubeUserTopHeader')
                for element in earnings_elements:
                    text = element.get_text()
                    if '$' in text:
                        data['earnings_estimate'] = text.strip()
                
                # Look for follower count
                follower_elements = soup.find_all('span', class_='YouTubeUserTopHeader')
                for element in follower_elements:
                    text = element.get_text()
                    if any(char.isdigit() for char in text) and any(unit in text.upper() for unit in ['K', 'M', 'B']):
                        data['followers'] = text.strip()
                        break
                
                return data
            else:
                print(f"[-] SocialBlade request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[-] SocialBlade error: {e}")
            return None
    
    def scrape_tiktokmetrics(self, username):
        print(f"[+] Scraping TikTokMetrics data for @{username}")
        try:
            url = f"https://tiktokmetrics.com/@{username}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                data = {}
                
                # Extract metrics
                metric_elements = soup.find_all(['div', 'span'], class_=['metric', 'stat', 'number'])
                for element in metric_elements:
                    text = element.get_text().strip()
                    if text and any(char.isdigit() for char in text):
                        if 'followers' in text.lower() or 'subscribers' in text.lower():
                            data['followers'] = text
                        elif 'views' in text.lower():
                            data['total_views'] = text
                        elif 'likes' in text.lower():
                            data['total_likes'] = text
                
                return data
            else:
                print(f"[-] TikTokMetrics request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[-] TikTokMetrics error: {e}")
            return None
    
    def convert_count_to_number(self, count_text):
        """Convert count text (e.g., '1.2M', '500K') to number"""
        try:
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
        except:
            return 0
    
    def calculate_earnings(self, follower_count):
        # TikTok earnings estimation models
        cpm_earnings = follower_count * 0.1 * 1.25 / 1000  # CPM model
        engagement_earnings = follower_count * 0.035 * 0.01  # Engagement model
        brand_deals = follower_count * 0.025  # Brand deals
        live_stream = follower_count * 0.01 * 1  # Live streaming
        merchandise = follower_count * 0.005 * 10  # Merchandise
        
        total_monthly = cpm_earnings + engagement_earnings + brand_deals + live_stream + merchandise
        
        return {
            'monthly': round(total_monthly, 2),
            'yearly': round(total_monthly * 12, 2),
            'breakdown': {
                'cpm': round(cpm_earnings, 2),
                'engagement': round(engagement_earnings, 2),
                'brand_deals': round(brand_deals, 2),
                'live_stream': round(live_stream, 2),
                'merchandise': round(merchandise, 2)
            }
        }
    
    def analyze_account(self, tiktok_url):
        username = self.extract_username(tiktok_url)
        if not username:
            print("[-] Could not extract username from URL")
            print(f"[-] URL: {tiktok_url}")
            return None
        
        print(f"[+] Analyzing @{username}")
        print(f"[+] URL: {tiktok_url}")
        
        # Scrape multiple sources
        tiktok_data = self.scrape_tiktok_profile(username)
        socialblade_data = self.scrape_socialblade(username)
        metrics_data = self.scrape_tiktokmetrics(username)
        
        # Determine follower count from various sources
        follower_count = 0
        follower_source = "estimated"
        
        if socialblade_data and 'followers' in socialblade_data:
            follower_count = self.convert_count_to_number(socialblade_data['followers'])
            follower_source = "SocialBlade"
        elif metrics_data and 'followers' in metrics_data:
            follower_count = self.convert_count_to_number(metrics_data['followers'])
            follower_source = "TikTokMetrics"
        elif tiktok_data and 'followers' in tiktok_data:
            follower_count = self.convert_count_to_number(tiktok_data['followers'])
            follower_source = "TikTok Profile"
        else:
            # Fallback to estimated followers based on account analysis
            follower_count = 50000  # Conservative estimate
            follower_source = "estimated"
        
        # Calculate earnings
        earnings = self.calculate_earnings(follower_count)
        
        report = {
            'username': username,
            'url': tiktok_url,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'follower_count': follower_count,
            'follower_source': follower_source,
            'tiktok_data': tiktok_data,
            'socialblade_data': socialblade_data,
            'metrics_data': metrics_data,
            'earnings_estimate': earnings
        }
        
        return report

def main():
    analyzer = TikTokEarningsAnalyzer()
    url = "https://www.tiktok.com/@2wpeezy4?_t=ZP-8zF8dwhJqJS&_r=1"
    
    print("🔥 TIKTOK EARNINGS DEEP DIVE ANALYZER")
    print("="*50)
    
    report = analyzer.analyze_account(url)
    
    if report:
        print("\n" + "="*60)
        print("TIKTOK EARNINGS ANALYSIS REPORT")
        print("="*60)
        print(f"Account: @{report['username']}")
        print(f"Analysis Date: {report['analysis_date']}")
        print(f"Follower Count: {report['follower_count']:,.0f} (Source: {report['follower_source']})")
        print(f"Estimated Monthly Earnings: ${report['earnings_estimate']['monthly']:,.2f}")
        print(f"Estimated Yearly Earnings: ${report['earnings_estimate']['yearly']:,.2f}")
        print("\nEarnings Breakdown:")
        for source, amount in report['earnings_estimate']['breakdown'].items():
            print(f"  {source.replace('_', ' ').title()}: ${amount:,.2f}")
        
        if report['socialblade_data'] and 'earnings_estimate' in report['socialblade_data']:
            print(f"\nSocialBlade Estimate: {report['socialblade_data']['earnings_estimate']}")
        
        print("\nData Sources:")
        print(f"  TikTok Profile: {'✓' if report['tiktok_data'] else '✗'}")
        print(f"  SocialBlade: {'✓' if report['socialblade_data'] else '✗'}")
        print(f"  TikTokMetrics: {'✓' if report['metrics_data'] else '✗'}")
        
        print("="*60)
        
        # Save report to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"tiktok_analysis_{report['username']}_{timestamp}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to: {filename}")
        except Exception as e:
            print(f"\n[-] Error saving report: {e}")
    else:
        print("\n❌ Analysis failed. Please check the account URL and try again.")

if __name__ == "__main__":
    main()
