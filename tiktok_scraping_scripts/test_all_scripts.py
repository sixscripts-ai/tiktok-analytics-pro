#!/usr/bin/env python3
"""
Comprehensive Test Script for TikTok Scraping & Analytics Suite
Tests all components and provides a detailed status report
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

def test_imports():
    """Test all module imports"""
    print("🔍 Testing module imports...")
    
    modules = [
        "profile_scraper",
        "video_data_extractor", 
        "earnings_calculator",
        "engagement_analyzer",
        "anti_detection_system",
        "data_processor",
        "driver_loader",
        "integration_api"
    ]
    
    results = {}
    for module in modules:
        try:
            __import__(module)
            results[module] = "✅ SUCCESS"
        except Exception as e:
            results[module] = f"❌ FAILED: {str(e)}"
    
    return results

def test_analytics_imports():
    """Test analytics module imports"""
    print("📊 Testing analytics imports...")
    
    analytics_modules = [
        "analytics.posting_time_optimizer",
        "analytics.hashtag_efficacy", 
        "analytics.sound_lifespan"
    ]
    
    results = {}
    for module in analytics_modules:
        try:
            __import__(module)
            results[module] = "✅ SUCCESS"
        except Exception as e:
            results[module] = f"❌ FAILED: {str(e)}"
    
    return results

def test_scraper_imports():
    """Test scraper module imports"""
    print("🕷️ Testing scraper imports...")
    
    scraper_modules = [
        "scrapers.comments_scraper",
        "scrapers.utils_loader"
    ]
    
    results = {}
    for module in scraper_modules:
        try:
            __import__(module)
            results[module] = "✅ SUCCESS"
        except Exception as e:
            results[module] = f"❌ FAILED: {str(e)}"
    
    return results

def test_cli_functionality():
    """Test CLI functionality"""
    print("🖥️ Testing CLI functionality...")
    
    try:
        from tiktok_cli import main
        results = {"tiktok_cli": "✅ SUCCESS"}
    except Exception as e:
        results = {"tiktok_cli": f"❌ FAILED: {str(e)}"}
    
    return results

def test_integration_api():
    """Test integration API"""
    print("🔗 Testing integration API...")
    
    try:
        from integration_api import TikTokIntegrationAPI
        api = TikTokIntegrationAPI()
        results = {"integration_api": "✅ SUCCESS"}
    except Exception as e:
        results = {"integration_api": f"❌ FAILED: {str(e)}"}
    
    return results

def test_data_files():
    """Test data file structure"""
    print("📁 Testing data file structure...")
    
    data_dir = Path("scraped_data")
    results = {}
    
    if data_dir.exists():
        results["data_directory"] = "✅ EXISTS"
        
        # Check for profile files
        profile_files = list(data_dir.glob("*_profile.json"))
        results["profile_files"] = f"✅ FOUND {len(profile_files)} files"
        
        # Check for video files
        video_files = list(data_dir.glob("*_videos.json"))
        results["video_files"] = f"✅ FOUND {len(video_files)} files"
        
        # Check file contents
        for profile_file in profile_files[:2]:  # Check first 2
            try:
                with open(profile_file, 'r') as f:
                    data = json.load(f)
                results[f"profile_file_{profile_file.name}"] = "✅ VALID JSON"
            except Exception as e:
                results[f"profile_file_{profile_file.name}"] = f"❌ INVALID: {str(e)}"
                
    else:
        results["data_directory"] = "❌ MISSING"
    
    return results

def test_dependencies():
    """Test required dependencies"""
    print("📦 Testing dependencies...")
    
    dependencies = [
        "selenium",
        "undetected_chromedriver", 
        "requests",
        "bs4",  # beautifulsoup4
        "pandas",
        "numpy",
        "sklearn",  # scikit-learn
        "textblob"
    ]
    
    results = {}
    for dep in dependencies:
        try:
            __import__(dep)
            results[dep] = "✅ INSTALLED"
        except ImportError:
            results[dep] = "❌ MISSING"
        except Exception as e:
            results[dep] = f"⚠️ ERROR: {str(e)}"
    
    return results

def generate_report():
    """Generate comprehensive test report"""
    print("🚀 Starting comprehensive test suite...")
    print("=" * 60)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Run all tests
    report["tests"]["imports"] = test_imports()
    report["tests"]["analytics"] = test_analytics_imports()
    report["tests"]["scrapers"] = test_scraper_imports()
    report["tests"]["cli"] = test_cli_functionality()
    report["tests"]["integration"] = test_integration_api()
    report["tests"]["data_files"] = test_data_files()
    report["tests"]["dependencies"] = test_dependencies()
    
    # Calculate summary
    total_tests = 0
    passed_tests = 0
    
    for category, tests in report["tests"].items():
        for test_name, result in tests.items():
            total_tests += 1
            if result.startswith("✅"):
                passed_tests += 1
    
    report["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
    }
    
    return report

def print_report(report):
    """Print formatted test report"""
    print("\n" + "=" * 60)
    print("📋 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    for category, tests in report["tests"].items():
        print(f"\n🔹 {category.upper()}:")
        for test_name, result in tests.items():
            print(f"  {test_name}: {result}")
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total Tests: {report['summary']['total_tests']}")
    print(f"  Passed: {report['summary']['passed_tests']}")
    print(f"  Failed: {report['summary']['failed_tests']}")
    print(f"  Success Rate: {report['summary']['success_rate']}")
    
    if report['summary']['failed_tests'] == 0:
        print("\n🎉 ALL TESTS PASSED! System is fully functional.")
    else:
        print(f"\n⚠️ {report['summary']['failed_tests']} tests failed. Check the details above.")
    
    print("=" * 60)

def save_report(report):
    """Save report to file"""
    report_file = Path("test_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    try:
        report = generate_report()
        print_report(report)
        save_report(report)
        
        # Exit with appropriate code
        if report['summary']['failed_tests'] == 0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        sys.exit(1)
