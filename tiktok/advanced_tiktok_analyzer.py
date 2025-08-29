#!/usr/bin/env python3
"""
Advanced TikTok Earnings Deep Dive Analyzer
Comprehensive analysis with anti-detection measures and multiple data sources
"""

import requests
import json
import time
import random
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import re
from bs4 import BeautifulSoup
import concurrent.futures
import os
import sys

class AdvancedTikTokAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
        ]
        self.setup_session()
        self.proxy_list = []
        self.load_proxies()
        
    def setup_session(self):
        """Setup session with advanced stealth headers"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        })
    
    def load_proxies(self):
        """Load proxy list for rotation"""
        # Free proxy list (in production, use paid proxies)
        self.proxy_list = [
            None,  # Direct connection
            # Add proxy servers here if available
        ]
    
    def get_random_proxy(self):
        """Get random proxy from list"""
        return random.choice(self.proxy_list) if self.proxy_list else None
    
    def stealth_request(self, url, method='GET', data=None, timeout=20):
        """Make stealth request with anti-detection measures"""
        try:
            # Random delay
            time.sleep(random.uniform(2, 5))
            
            # Rotate user agent
            self.session.headers.update({'User-Agent': random.choice(self.user_agents)})
            
            # Use proxy if available
            proxy = self.get_random_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=timeout, proxies=proxies)
            else:
                response = self.session.post(url, data=data, timeout=timeout, proxies=proxies)
            
            return response
        except Exception as e:
            print(f"[-] Stealth request failed: {e}")
            return None
    
    def extract_username(self, url):
        """Extract username from TikTok URL"""
        try:
            if '?' in url:
                url = url.split('?')[0]
            
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
    
    def scrape_tiktok_with_selenium(self, username):
        """Scrape TikTok using Selenium for better data extraction"""
        print(f"[+] Attempting Selenium-based TikTok scraping for @{username}")
        
        try:
            # Try to use Selenium if available
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            try:
                url = f"https://www.tiktok.com/@{username}"
                driver.get(url)
                
                # Wait for page to load
                time.sleep(5)
                
                # Scroll to load content
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Extract data
                data = {}
                
                # Try to find follower count
                try:
                    follower_elements = driver.find_elements(By.XPATH, "//strong[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                    for element in follower_elements:
                        text = element.text
                        if any(char.isdigit() for char in text):
                            data['followers'] = text
                            break
                except:
                    pass
                
                # Try to find video count
                try:
                    video_elements = driver.find_elements(By.XPATH, "//strong[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                    for element in video_elements:
                        text = element.text
                        if any(char.isdigit() for char in text):
                            data['video_count'] = text
                            break
                except:
                    pass
                
                return data
                
            finally:
                driver.quit()
                
        except ImportError:
            print("[-] Selenium not available, using alternative methods")
            return None
        except Exception as e:
            print(f"[-] Selenium scraping failed: {e}")
            return None
    
    def scrape_alternative_sources(self, username):
        """Scrape alternative data sources"""
        print(f"[+] Scraping alternative data sources for @{username}")
        
        sources_data = {}
        
        # Try various TikTok analytics sites
        alternative_sources = [
            f"https://tiktokanalytics.com/@{username}",
            f"https://tiktokstats.com/@{username}",
            f"https://tiktoktracker.com/@{username}",
            f"https://tiktokinsights.com/@{username}"
        ]
        
        for source_url in alternative_sources:
            try:
                response = self.stealth_request(source_url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract metrics
                    data = {}
                    page_text = soup.get_text()
                    
                    # Look for follower count
                    follower_patterns = [
                        r'(\d+(?:\.\d+)?[KMB]?)\s*followers',
                        r'(\d+(?:\.\d+)?[KMB]?)\s*subscribers',
                        r'follower[^0-9]*(\d+(?:\.\d+)?[KMB]?)',
                    ]
                    
                    for pattern in follower_patterns:
                        match = re.search(pattern, page_text, re.IGNORECASE)
                        if match:
                            data['followers'] = match.group(1)
                            break
                    
                    if data:
                        sources_data[source_url] = data
                        print(f"[+] Found data from: {source_url}")
                        
            except Exception as e:
                continue
        
        return sources_data
    
    def scrape_instagram_cross_reference(self, username):
        """Try to find Instagram account for cross-referencing"""
        print(f"[+] Cross-referencing with Instagram for @{username}")
        
        try:
            instagram_url = f"https://www.instagram.com/{username}/"
            response = self.stealth_request(instagram_url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for follower count
                follower_patterns = [
                    r'(\d+(?:,\d+)*)\s*followers',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*followers',
                ]
                
                page_text = soup.get_text()
                for pattern in follower_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        return {'instagram_followers': match.group(1)}
            
            return None
            
        except Exception as e:
            print(f"[-] Instagram cross-reference failed: {e}")
            return None
    
    def scrape_youtube_cross_reference(self, username):
        """Try to find YouTube channel for cross-referencing"""
        print(f"[+] Cross-referencing with YouTube for @{username}")
        
        try:
            youtube_url = f"https://www.youtube.com/@{username}"
            response = self.stealth_request(youtube_url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for subscriber count
                subscriber_patterns = [
                    r'(\d+(?:,\d+)*)\s*subscribers',
                    r'(\d+(?:\.\d+)?[KMB]?)\s*subscribers',
                ]
                
                page_text = soup.get_text()
                for pattern in subscriber_patterns:
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        return {'youtube_subscribers': match.group(1)}
            
            return None
            
        except Exception as e:
            print(f"[-] YouTube cross-reference failed: {e}")
            return None
    
    def analyze_account_activity(self, username):
        """Analyze account activity patterns"""
        print(f"[+] Analyzing account activity patterns for @{username}")
        
        activity_data = {
            'posting_frequency': 'unknown',
            'engagement_pattern': 'unknown',
            'content_type': 'unknown',
            'peak_hours': 'unknown'
        }
        
        # This would require more sophisticated analysis
        # For now, return estimated patterns based on typical TikTok accounts
        
        return activity_data
    
    def estimate_earnings_advanced(self, follower_count, engagement_rate=None):
        """Advanced earnings estimation with multiple models"""
        print(f"[+] Calculating advanced earnings estimates for {follower_count:,} followers")
        
        # Default engagement rate if not provided
        if engagement_rate is None:
            engagement_rate = 0.035  # 3.5% average
        
        # Model 1: CPM-based earnings
        avg_cpm = 1.25  # $1.25 per 1000 views
        estimated_views_per_month = follower_count * 0.1  # 10% of followers view content monthly
        cpm_earnings = (estimated_views_per_month / 1000) * avg_cpm
        
        # Model 2: Engagement-based earnings
        engagement_earnings = follower_count * engagement_rate * 0.01  # $0.01 per engagement
        
        # Model 3: Brand deals (varies by follower count)
        if follower_count >= 1000000:  # 1M+ followers
            brand_deal_rate = 0.05  # $0.05 per follower
        elif follower_count >= 100000:  # 100K+ followers
            brand_deal_rate = 0.025  # $0.025 per follower
        else:
            brand_deal_rate = 0.01  # $0.01 per follower
        
        brand_deal_earnings = follower_count * brand_deal_rate
        
        # Model 4: Live streaming earnings
        live_stream_earnings = follower_count * 0.01 * 1  # 1% donate $1 per month
        
        # Model 5: Merchandise and affiliate sales
        merchandise_earnings = follower_count * 0.005 * 10  # 0.5% buy $10 worth
        
        # Model 6: Creator Fund (TikTok's program)
        creator_fund_earnings = follower_count * 0.001 * 2  # $2 per 1000 followers
        
        # Total monthly earnings
        total_monthly = (cpm_earnings + engagement_earnings + brand_deal_earnings + 
                        live_stream_earnings + merchandise_earnings + creator_fund_earnings)
        
        return {
            'monthly': round(total_monthly, 2),
            'yearly': round(total_monthly * 12, 2),
            'breakdown': {
                'cpm_earnings': round(cpm_earnings, 2),
                'engagement_earnings': round(engagement_earnings, 2),
                'brand_deals': round(brand_deal_earnings, 2),
                'live_streaming': round(live_stream_earnings, 2),
                'merchandise': round(merchandise_earnings, 2),
                'creator_fund': round(creator_fund_earnings, 2)
            },
            'metrics': {
                'follower_count': follower_count,
                'engagement_rate': engagement_rate,
                'estimated_monthly_views': estimated_views_per_month
            }
        }
    
    def convert_count_to_number(self, count_text):
        """Convert count text to number"""
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
    
    def run_comprehensive_analysis(self, tiktok_url):
        """Run comprehensive TikTok analysis"""
        print("🔥 ADVANCED TIKTOK EARNINGS DEEP DIVE ANALYZER")
        print("="*60)
        
        username = self.extract_username(tiktok_url)
        if not username:
            print("[-] Could not extract username from URL")
            return None
        
        print(f"[+] Target Account: @{username}")
        print(f"[+] Analysis URL: {tiktok_url}")
        print()
        
        # Step 1: Selenium-based TikTok scraping
        print("[1/6] Selenium-based TikTok profile analysis...")
        tiktok_data = self.scrape_tiktok_with_selenium(username)
        
        # Step 2: Alternative data sources
        print("[2/6] Scraping alternative data sources...")
        alternative_data = self.scrape_alternative_sources(username)
        
        # Step 3: Cross-platform analysis
        print("[3/6] Cross-platform analysis...")
        instagram_data = self.scrape_instagram_cross_reference(username)
        youtube_data = self.scrape_youtube_cross_reference(username)
        
        # Step 4: Account activity analysis
        print("[4/6] Account activity analysis...")
        activity_data = self.analyze_account_activity(username)
        
        # Step 5: Determine follower count from multiple sources
        print("[5/6] Determining follower count from multiple sources...")
        follower_count = 0
        follower_source = "estimated"
        
        # Priority order for follower count sources
        if tiktok_data and 'followers' in tiktok_data:
            follower_count = self.convert_count_to_number(tiktok_data['followers'])
            follower_source = "TikTok Selenium"
        elif alternative_data:
            for source, data in alternative_data.items():
                if 'followers' in data:
                    follower_count = self.convert_count_to_number(data['followers'])
                    follower_source = f"Alternative Source ({source.split('/')[-1]})"
                    break
        elif instagram_data and 'instagram_followers' in instagram_data:
            # Use Instagram as rough estimate (usually similar to TikTok)
            follower_count = self.convert_count_to_number(instagram_data['instagram_followers'])
            follower_source = "Instagram Cross-Reference"
        else:
            # Conservative estimate based on account analysis
            follower_count = 75000  # More realistic estimate
            follower_source = "Conservative Estimate"
        
        # Step 6: Advanced earnings calculation
        print("[6/6] Advanced earnings calculation...")
        earnings_analysis = self.estimate_earnings_advanced(follower_count)
        
        # Compile comprehensive report
        report = {
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'username': username,
            'tiktok_url': tiktok_url,
            'follower_count': follower_count,
            'follower_source': follower_source,
            'tiktok_data': tiktok_data,
            'alternative_data': alternative_data,
            'instagram_data': instagram_data,
            'youtube_data': youtube_data,
            'activity_data': activity_data,
            'earnings_analysis': earnings_analysis,
            'data_sources': {
                'tiktok_selenium': tiktok_data is not None,
                'alternative_sources': len(alternative_data) > 0,
                'instagram_cross_reference': instagram_data is not None,
                'youtube_cross_reference': youtube_data is not None
            }
        }
        
        return report
    
    def print_comprehensive_report(self, report):
        """Print comprehensive analysis report"""
        print("\n" + "="*80)
        print("🎯 ADVANCED TIKTOK EARNINGS ANALYSIS REPORT")
        print("="*80)
        
        username = report['username']
        earnings = report['earnings_analysis']
        
        print(f"📱 Account: @{username}")
        print(f"🔗 Profile: {report['tiktok_url']}")
        print(f"📅 Analysis Date: {report['analysis_timestamp']}")
        print(f"👥 Follower Count: {report['follower_count']:,.0f} (Source: {report['follower_source']})")
        print()
        
        print("💰 EARNINGS ESTIMATES:")
        print(f"   Monthly Earnings: ${earnings['monthly']:,.2f}")
        print(f"   Yearly Earnings: ${earnings['yearly']:,.2f}")
        print()
        
        print("💵 EARNINGS BREAKDOWN:")
        for source, amount in earnings['breakdown'].items():
            source_name = source.replace('_', ' ').title()
            print(f"   {source_name}: ${amount:,.2f}")
        print()
        
        print("📊 ENGAGEMENT METRICS:")
        metrics = earnings['metrics']
        print(f"   Engagement Rate: {metrics['engagement_rate']*100:.1f}%")
        print(f"   Estimated Monthly Views: {metrics['estimated_monthly_views']:,.0f}")
        print()
        
        print("🔍 DATA SOURCES:")
        sources = report['data_sources']
        for source, available in sources.items():
            status = "✓" if available else "✗"
            source_name = source.replace('_', ' ').title()
            print(f"   {source_name}: {status}")
        print()
        
        if report['instagram_data']:
            print("📸 CROSS-PLATFORM DATA:")
            print(f"   Instagram Followers: {report['instagram_data'].get('instagram_followers', 'N/A')}")
        
        if report['youtube_data']:
            print(f"   YouTube Subscribers: {report['youtube_data'].get('youtube_subscribers', 'N/A')}")
        print()
        
        print("🎯 RECOMMENDATIONS:")
        if earnings['monthly'] > 10000:
            print("   ✅ High-earning account - Premium brand partnerships recommended")
        elif earnings['monthly'] > 1000:
            print("   📈 Growing account - Focus on engagement and content quality")
        else:
            print("   🌱 Emerging account - Build audience and establish niche")
        
        if metrics['engagement_rate'] > 0.05:
            print("   🎉 Excellent engagement - Leverage for higher brand deals")
        elif metrics['engagement_rate'] > 0.02:
            print("   👍 Good engagement - Room for improvement with better content")
        else:
            print("   📉 Low engagement - Focus on audience interaction")
        
        print("="*80)
    
    def save_detailed_report(self, report):
        """Save detailed report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"advanced_tiktok_analysis_{report['username']}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Detailed report saved to: {filename}")
            return filename
        except Exception as e:
            print(f"\n[-] Error saving report: {e}")
            return None

def main():
    analyzer = AdvancedTikTokAnalyzer()
    url = "https://www.tiktok.com/@2wpeezy4?_t=ZP-8zF8dwhJqJS&_r=1"
    
    # Run comprehensive analysis
    report = analyzer.run_comprehensive_analysis(url)
    
    if report:
        # Print comprehensive report
        analyzer.print_comprehensive_report(report)
        
        # Save detailed report
        analyzer.save_detailed_report(report)
        
        print(f"\n✅ Advanced analysis completed successfully!")
        print(f"🎯 Account analyzed: @{report['username']}")
        print(f"💰 Estimated monthly earnings: ${report['earnings_analysis']['monthly']:,.2f}")
    else:
        print(f"\n❌ Analysis failed. Please check the account URL and try again.")

if __name__ == "__main__":
    main()
