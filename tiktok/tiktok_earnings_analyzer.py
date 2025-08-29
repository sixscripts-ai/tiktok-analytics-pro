#!/usr/bin/env python3
"""
TikTok Earnings Deep Dive Analyzer
Comprehensive analysis tool for TikTok account earnings and engagement metrics
"""

import json
import time
import random
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import concurrent.futures
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import os
import sys

from tiktok_scraping_scripts.network.session_manager import (
    create_session,
    rotate_user_agent,
)

class TikTokEarningsAnalyzer:
    def __init__(self):
        self.session = create_session()
        self.earnings_data = {}
        self.engagement_data = {}
        self.video_data = []
    
    def get_random_delay(self):
        """Get random delay to avoid detection"""
        return random.uniform(1, 3)
    
    def setup_selenium_driver(self):
        """Setup undetected Chrome driver for TikTok scraping"""
        try:
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = uc.Chrome(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Error setting up Selenium driver: {e}")
            return None
    
    def extract_username_from_url(self, url):
        """Extract username from TikTok URL"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            for i, part in enumerate(path_parts):
                if part == '@' and i + 1 < len(path_parts):
                    return path_parts[i + 1]
            return None
        except:
            return None
    
    def scrape_tiktok_profile_selenium(self, username):
        """Scrape TikTok profile using Selenium for better data extraction"""
        print(f"[+] Starting Selenium-based TikTok profile scraping for @{username}")
        
        driver = self.setup_selenium_driver()
        if not driver:
            print("[-] Failed to setup Selenium driver")
            return None
        
        try:
            # Navigate to profile
            profile_url = f"https://www.tiktok.com/@{username}"
            print(f"[*] Navigating to: {profile_url}")
            driver.get(profile_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Scroll to load more content
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Extract profile information
            profile_data = {}
            
            try:
                # Get follower count
                follower_elements = driver.find_elements(By.XPATH, "//strong[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                for element in follower_elements:
                    text = element.text
                    if any(char.isdigit() for char in text):
                        profile_data['followers'] = text
                        break
                
                # Get following count
                following_elements = driver.find_elements(By.XPATH, "//strong[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                for element in following_elements:
                    text = element.text
                    if any(char.isdigit() for char in text):
                        profile_data['following'] = text
                        break
                
                # Get like count
                like_elements = driver.find_elements(By.XPATH, "//strong[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                for element in like_elements:
                    text = element.text
                    if any(char.isdigit() for char in text):
                        profile_data['likes'] = text
                        break
                
                # Get bio/description
                try:
                    bio_element = driver.find_element(By.XPATH, "//h2[contains(@class, 'tiktok')]")
                    profile_data['bio'] = bio_element.text
                except:
                    pass
                
                # Get video count
                try:
                    video_count_elements = driver.find_elements(By.XPATH, "//strong[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                    for element in video_count_elements:
                        text = element.text
                        if any(char.isdigit() for char in text):
                            profile_data['video_count'] = text
                            break
                except:
                    pass
                
            except Exception as e:
                print(f"[-] Error extracting profile data: {e}")
            
            # Extract video information
            videos = []
            try:
                video_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'video-feed')]//div[contains(@class, 'video-card')]")
                
                for video_element in video_elements[:10]:  # Get first 10 videos
                    try:
                        video_data = {}
                        
                        # Get video views
                        view_elements = video_element.find_elements(By.XPATH, ".//span[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                        for element in view_elements:
                            text = element.text
                            if any(char.isdigit() for char in text):
                                video_data['views'] = text
                                break
                        
                        # Get video likes
                        like_elements = video_element.find_elements(By.XPATH, ".//span[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                        for element in like_elements:
                            text = element.text
                            if any(char.isdigit() for char in text):
                                video_data['likes'] = text
                                break
                        
                        # Get video comments
                        comment_elements = video_element.find_elements(By.XPATH, ".//span[contains(text(), 'K') or contains(text(), 'M') or contains(text(), 'B')]")
                        for element in comment_elements:
                            text = element.text
                            if any(char.isdigit() for char in text):
                                video_data['comments'] = text
                                break
                        
                        if video_data:
                            videos.append(video_data)
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"[-] Error extracting video data: {e}")
            
            profile_data['videos'] = videos
            
            return profile_data
            
        except Exception as e:
            print(f"[-] Error during Selenium scraping: {e}")
            return None
        finally:
            driver.quit()
    
    def scrape_tiktok_api_data(self, username):
        """Attempt to scrape TikTok API data"""
        print(f"[+] Attempting TikTok API data extraction for @{username}")
        
        api_endpoints = [
            f"https://www.tiktok.com/api/user/detail/?uniqueId={username}",
            f"https://www.tiktok.com/api/user/list/?count=30&minCursor=0&maxCursor=0&sourceType=1&itemId=1&insertedUserID=&userID=&language=en&verifyFp=&_signature=",
            f"https://www.tiktok.com/api/user/videos/?count=30&minCursor=0&maxCursor=0&sourceType=1&itemId=1&insertedUserID=&userID=&language=en&verifyFp=&_signature="
        ]
        
        api_data = {}
        
        for endpoint in api_endpoints:
            try:
                time.sleep(self.get_random_delay())

                rotate_user_agent(self.session)
                headers = {
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': f'https://www.tiktok.com/@{username}',
                    'Origin': 'https://www.tiktok.com',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin'
                }

                response = self.session.get(endpoint, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        api_data[endpoint] = data
                        print(f"[+] Successfully extracted data from: {endpoint}")
                    except:
                        print(f"[-] Failed to parse JSON from: {endpoint}")
                else:
                    print(f"[-] API request failed for {endpoint}: {response.status_code}")
                    
            except Exception as e:
                print(f"[-] Error accessing API endpoint {endpoint}: {e}")
        
        return api_data
    
    def scrape_socialblade_data(self, username):
        """Scrape SocialBlade data for TikTok earnings estimates"""
        print(f"[+] Scraping SocialBlade data for @{username}")
        
        try:
            socialblade_url = f"https://socialblade.com/tiktok/user/{username}/monthly"
            
            rotate_user_agent(self.session)
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://socialblade.com/'
            }

            response = self.session.get(socialblade_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                socialblade_data = {}
                
                # Extract earnings estimates
                earnings_elements = soup.find_all('div', class_='YouTubeUserTopHeader')
                for element in earnings_elements:
                    text = element.get_text()
                    if '$' in text and any(word in text.lower() for word in ['monthly', 'yearly', 'estimated']):
                        socialblade_data['earnings_estimate'] = text.strip()
                
                # Extract subscriber/follower data
                follower_elements = soup.find_all('span', class_='YouTubeUserTopHeader')
                for element in follower_elements:
                    text = element.get_text()
                    if any(char.isdigit() for char in text):
                        socialblade_data['followers'] = text.strip()
                
                # Extract video count
                video_elements = soup.find_all('span', class_='YouTubeUserTopHeader')
                for element in video_elements:
                    text = element.get_text()
                    if any(char.isdigit() for char in text):
                        socialblade_data['video_count'] = text.strip()
                
                return socialblade_data
            else:
                print(f"[-] SocialBlade request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[-] Error scraping SocialBlade: {e}")
            return None
    
    def scrape_tiktokmetrics_data(self, username):
        """Scrape TikTokMetrics data for additional insights"""
        print(f"[+] Scraping TikTokMetrics data for @{username}")
        
        try:
            metrics_url = f"https://tiktokmetrics.com/@{username}"
            
            rotate_user_agent(self.session)
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9'
            }

            response = self.session.get(metrics_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                metrics_data = {}
                
                # Extract various metrics
                metric_elements = soup.find_all(['div', 'span'], class_=['metric', 'stat', 'number'])
                for element in metric_elements:
                    text = element.get_text().strip()
                    if text and any(char.isdigit() for char in text):
                        if 'followers' in text.lower() or 'subscribers' in text.lower():
                            metrics_data['followers'] = text
                        elif 'views' in text.lower():
                            metrics_data['total_views'] = text
                        elif 'likes' in text.lower():
                            metrics_data['total_likes'] = text
                        elif 'comments' in text.lower():
                            metrics_data['total_comments'] = text
                        elif 'videos' in text.lower():
                            metrics_data['video_count'] = text
                
                return metrics_data
            else:
                print(f"[-] TikTokMetrics request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[-] Error scraping TikTokMetrics: {e}")
            return None
    
    def calculate_earnings_estimates(self, profile_data, socialblade_data, metrics_data):
        """Calculate comprehensive earnings estimates"""
        print("[+] Calculating earnings estimates...")
        
        earnings_analysis = {}
        
        # Extract follower count
        follower_count = 0
        follower_text = ""
        
        if profile_data and 'followers' in profile_data:
            follower_text = profile_data['followers']
        elif socialblade_data and 'followers' in socialblade_data:
            follower_text = socialblade_data['followers']
        elif metrics_data and 'followers' in metrics_data:
            follower_text = metrics_data['followers']
        
        # Convert follower count to number
        if follower_text:
            follower_count = self.convert_count_to_number(follower_text)
        
        earnings_analysis['follower_count'] = follower_count
        earnings_analysis['follower_text'] = follower_text
        
        # Calculate estimated earnings based on different models
        
        # Model 1: CPM-based earnings (Cost Per Mille)
        # Average CPM for TikTok: $0.50 - $2.00
        avg_cpm = 1.25  # $1.25 per 1000 views
        estimated_views_per_month = follower_count * 0.1  # Assume 10% of followers view content monthly
        cpm_earnings = (estimated_views_per_month / 1000) * avg_cpm
        
        # Model 2: Engagement-based earnings
        # Average engagement rate: 2-5%
        avg_engagement_rate = 0.035  # 3.5%
        engagement_earnings = follower_count * avg_engagement_rate * 0.01  # $0.01 per engagement
        
        # Model 3: Brand deals and sponsorships
        # Average brand deal value: $0.01 - $0.05 per follower
        avg_brand_deal_rate = 0.025  # $0.025 per follower
        brand_deal_earnings = follower_count * avg_brand_deal_rate
        
        # Model 4: Live streaming and gifts
        # Assume 1% of followers donate $1 per month
        live_stream_earnings = follower_count * 0.01 * 1
        
        # Model 5: Merchandise and affiliate sales
        # Assume 0.5% of followers buy $10 worth of merchandise per month
        merchandise_earnings = follower_count * 0.005 * 10
        
        # Total estimated monthly earnings
        total_monthly_earnings = cpm_earnings + engagement_earnings + brand_deal_earnings + live_stream_earnings + merchandise_earnings
        
        earnings_analysis.update({
            'cpm_earnings_monthly': round(cpm_earnings, 2),
            'engagement_earnings_monthly': round(engagement_earnings, 2),
            'brand_deal_earnings_monthly': round(brand_deal_earnings, 2),
            'live_stream_earnings_monthly': round(live_stream_earnings, 2),
            'merchandise_earnings_monthly': round(merchandise_earnings, 2),
            'total_monthly_earnings': round(total_monthly_earnings, 2),
            'total_yearly_earnings': round(total_monthly_earnings * 12, 2)
        })
        
        # Earnings breakdown by percentage
        if total_monthly_earnings > 0:
            earnings_analysis['earnings_breakdown'] = {
                'cpm_percentage': round((cpm_earnings / total_monthly_earnings) * 100, 1),
                'engagement_percentage': round((engagement_earnings / total_monthly_earnings) * 100, 1),
                'brand_deals_percentage': round((brand_deal_earnings / total_monthly_earnings) * 100, 1),
                'live_stream_percentage': round((live_stream_earnings / total_monthly_earnings) * 100, 1),
                'merchandise_percentage': round((merchandise_earnings / total_monthly_earnings) * 100, 1)
            }
        
        return earnings_analysis
    
    def convert_count_to_number(self, count_text):
        """Convert count text (e.g., '1.2M', '500K') to number"""
        try:
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
    
    def analyze_engagement_metrics(self, profile_data, metrics_data):
        """Analyze engagement metrics and patterns"""
        print("[+] Analyzing engagement metrics...")
        
        engagement_analysis = {}
        
        # Calculate engagement rate
        if profile_data and 'followers' in profile_data and 'likes' in profile_data:
            follower_count = self.convert_count_to_number(profile_data['followers'])
            like_count = self.convert_count_to_number(profile_data['likes'])
            
            if follower_count > 0:
                engagement_rate = (like_count / follower_count) * 100
                engagement_analysis['engagement_rate'] = round(engagement_rate, 2)
        
        # Analyze video performance
        if profile_data and 'videos' in profile_data:
            videos = profile_data['videos']
            if videos:
                total_views = 0
                total_likes = 0
                total_comments = 0
                
                for video in videos:
                    if 'views' in video:
                        total_views += self.convert_count_to_number(video['views'])
                    if 'likes' in video:
                        total_likes += self.convert_count_to_number(video['likes'])
                    if 'comments' in video:
                        total_comments += self.convert_count_to_number(video['comments'])
                
                engagement_analysis.update({
                    'total_video_views': total_views,
                    'total_video_likes': total_likes,
                    'total_video_comments': total_comments,
                    'avg_views_per_video': round(total_views / len(videos), 2) if videos else 0,
                    'avg_likes_per_video': round(total_likes / len(videos), 2) if videos else 0,
                    'avg_comments_per_video': round(total_comments / len(videos), 2) if videos else 0
                })
        
        return engagement_analysis
    
    def generate_comprehensive_report(self, username, profile_data, socialblade_data, metrics_data, earnings_analysis, engagement_analysis):
        """Generate comprehensive analysis report"""
        print("[+] Generating comprehensive analysis report...")
        
        report = {
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'username': username,
            'profile_url': f"https://www.tiktok.com/@{username}",
            'profile_data': profile_data,
            'socialblade_data': socialblade_data,
            'metrics_data': metrics_data,
            'earnings_analysis': earnings_analysis,
            'engagement_analysis': engagement_analysis,
            'summary': {}
        }
        
        # Generate summary
        summary = {}
        
        if earnings_analysis:
            summary['estimated_monthly_earnings'] = earnings_analysis.get('total_monthly_earnings', 0)
            summary['estimated_yearly_earnings'] = earnings_analysis.get('total_yearly_earnings', 0)
            summary['follower_count'] = earnings_analysis.get('follower_count', 0)
        
        if engagement_analysis:
            summary['engagement_rate'] = engagement_analysis.get('engagement_rate', 0)
            summary['avg_views_per_video'] = engagement_analysis.get('avg_views_per_video', 0)
        
        report['summary'] = summary
        
        return report
    
    def save_report(self, report, username):
        """Save analysis report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"tiktok_earnings_analysis_{username}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"[+] Report saved to: {filename}")
            return filename
        except Exception as e:
            print(f"[-] Error saving report: {e}")
            return None
    
    def print_summary(self, report):
        """Print analysis summary"""
        print("\n" + "="*80)
        print("🎯 TIKTOK EARNINGS DEEP DIVE ANALYSIS SUMMARY")
        print("="*80)
        
        username = report['username']
        summary = report['summary']
        earnings = report['earnings_analysis']
        
        print(f"📱 Account: @{username}")
        print(f"🔗 Profile: {report['profile_url']}")
        print(f"📅 Analysis Date: {report['analysis_timestamp']}")
        print()
        
        print("💰 EARNINGS ESTIMATES:")
        print(f"   Monthly Earnings: ${summary.get('estimated_monthly_earnings', 0):,.2f}")
        print(f"   Yearly Earnings: ${summary.get('estimated_yearly_earnings', 0):,.2f}")
        print()
        
        print("📊 ENGAGEMENT METRICS:")
        print(f"   Followers: {summary.get('follower_count', 0):,.0f}")
        print(f"   Engagement Rate: {summary.get('engagement_rate', 0):.2f}%")
        print(f"   Avg Views per Video: {summary.get('avg_views_per_video', 0):,.0f}")
        print()
        
        if earnings and 'earnings_breakdown' in earnings:
            breakdown = earnings['earnings_breakdown']
            print("💵 EARNINGS BREAKDOWN:")
            print(f"   CPM/Ad Revenue: {breakdown.get('cpm_percentage', 0):.1f}%")
            print(f"   Engagement Revenue: {breakdown.get('engagement_percentage', 0):.1f}%")
            print(f"   Brand Deals: {breakdown.get('brand_deals_percentage', 0):.1f}%")
            print(f"   Live Streaming: {breakdown.get('live_stream_percentage', 0):.1f}%")
            print(f"   Merchandise: {breakdown.get('merchandise_percentage', 0):.1f}%")
            print()
        
        print("🎯 RECOMMENDATIONS:")
        if summary.get('estimated_monthly_earnings', 0) > 10000:
            print("   ✅ High-earning account - Consider premium brand partnerships")
        elif summary.get('estimated_monthly_earnings', 0) > 1000:
            print("   📈 Growing account - Focus on engagement and content quality")
        else:
            print("   🌱 Emerging account - Build audience and establish niche")
        
        if summary.get('engagement_rate', 0) > 5:
            print("   🎉 Excellent engagement - Leverage for higher brand deals")
        elif summary.get('engagement_rate', 0) > 2:
            print("   👍 Good engagement - Room for improvement with better content")
        else:
            print("   📉 Low engagement - Focus on audience interaction")
        
        print("="*80)
    
    def run_comprehensive_analysis(self, tiktok_url):
        """Run comprehensive TikTok earnings analysis"""
        print("🔥 TIKTOK EARNINGS DEEP DIVE ANALYZER")
        print("="*50)
        
        # Extract username from URL
        username = self.extract_username_from_url(tiktok_url)
        if not username:
            print("[-] Could not extract username from URL")
            return None
        
        print(f"[+] Analyzing TikTok account: @{username}")
        print(f"[+] URL: {tiktok_url}")
        print()
        
        # Step 1: Scrape TikTok profile using Selenium
        print("[1/5] Scraping TikTok profile data...")
        profile_data = self.scrape_tiktok_profile_selenium(username)
        
        # Step 2: Scrape SocialBlade data
        print("[2/5] Scraping SocialBlade earnings data...")
        socialblade_data = self.scrape_socialblade_data(username)
        
        # Step 3: Scrape TikTokMetrics data
        print("[3/5] Scraping TikTokMetrics data...")
        metrics_data = self.scrape_tiktokmetrics_data(username)
        
        # Step 4: Calculate earnings estimates
        print("[4/5] Calculating earnings estimates...")
        earnings_analysis = self.calculate_earnings_estimates(profile_data, socialblade_data, metrics_data)
        
        # Step 5: Analyze engagement metrics
        print("[5/5] Analyzing engagement metrics...")
        engagement_analysis = self.analyze_engagement_metrics(profile_data, metrics_data)
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report(
            username, profile_data, socialblade_data, metrics_data, 
            earnings_analysis, engagement_analysis
        )
        
        # Save report
        report_file = self.save_report(report, username)
        
        # Print summary
        self.print_summary(report)
        
        return report

def main():
    """Main function to run the TikTok earnings analyzer"""
    analyzer = TikTokEarningsAnalyzer()
    
    # TikTok account URL to analyze
    tiktok_url = "https://www.tiktok.com/@2wpeezy4?_t=ZP-8zF8dwhJqJS&_r=1"
    
    # Run comprehensive analysis
    report = analyzer.run_comprehensive_analysis(tiktok_url)
    
    if report:
        print(f"\n✅ Analysis completed successfully!")
        print(f"📄 Detailed report saved to JSON file")
        print(f"🎯 Account analyzed: @{report['username']}")
    else:
        print(f"\n❌ Analysis failed. Please check the account URL and try again.")

if __name__ == "__main__":
    main()
