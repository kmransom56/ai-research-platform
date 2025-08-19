#!/usr/bin/env python3
"""
HTML Link Tester for Control Panel and Applications Pages
Tests all links in the HTML files to verify they're accessible
"""

import requests
import re
import sys
import time
from urllib.parse import urlparse, urljoin
from pathlib import Path

class LinkTester:
    def __init__(self, timeout=5):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Link-Tester/1.0)'
        })
        
        # Results tracking
        self.results = {
            'working': [],
            'failed': [],
            'localhost': [],
            'local_files': []
        }
    
    def extract_links_from_file(self, file_path):
        """Extract all href links from an HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find all href attributes
            href_pattern = r'href="([^"]*)"'
            links = re.findall(href_pattern, content)
            
            return links
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return []
    
    def categorize_link(self, link):
        """Categorize the type of link"""
        if link.startswith('#'):
            return 'anchor'
        elif link.startswith('mailto:'):
            return 'email'
        elif link.startswith('tel:'):
            return 'phone'
        elif link.startswith('javascript:'):
            return 'javascript'
        elif '://localhost:' in link or link.startswith('http://localhost'):
            return 'localhost'
        elif link.startswith('http://') or link.startswith('https://'):
            return 'external'
        else:
            return 'local_file'
    
    def test_external_link(self, link):
        """Test an external HTTP/HTTPS link"""
        try:
            response = self.session.get(link, timeout=self.timeout, allow_redirects=True)
            status_code = response.status_code
            
            if 200 <= status_code < 400:
                return True, f"Status: {status_code}"
            else:
                return False, f"Status: {status_code}"
                
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except requests.exceptions.ConnectionError:
            return False, "Connection Error"
        except requests.exceptions.RequestException as e:
            return False, f"Request Error: {str(e)}"
        except Exception as e:
            return False, f"Unknown Error: {str(e)}"
    
    def test_localhost_link(self, link):
        """Test a localhost link"""
        try:
            # For localhost links, we'll do a quick connection test
            response = self.session.get(link, timeout=2, allow_redirects=True)
            status_code = response.status_code
            
            if 200 <= status_code < 400:
                return True, f"Status: {status_code}"
            else:
                return False, f"Status: {status_code}"
                
        except Exception as e:
            return False, f"Service not running: {str(e)}"
    
    def test_local_file(self, link, base_path):
        """Test if a local file exists"""
        try:
            if link.startswith('/'):
                # Absolute path from webapi/wwwroot
                file_path = Path('/home/keith/chat-copilot/webapi/wwwroot') / link.lstrip('/')
            else:
                # Relative path from the HTML file
                file_path = base_path.parent / link
            
            if file_path.exists():
                return True, "File exists"
            else:
                return False, "File not found"
                
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def test_all_links(self, file_path):
        """Test all links in a single HTML file"""
        print(f"\n🔍 Testing links in: {file_path}")
        print("=" * 60)
        
        links = self.extract_links_from_file(file_path)
        if not links:
            print("No links found in file")
            return
        
        base_path = Path(file_path)
        
        for link in links:
            link_type = self.categorize_link(link)
            
            # Skip anchor, email, phone, and javascript links
            if link_type in ['anchor', 'email', 'phone', 'javascript']:
                continue
            
            print(f"\n📋 Testing: {link}")
            print(f"   Type: {link_type}")
            
            if link_type == 'external':
                success, message = self.test_external_link(link)
            elif link_type == 'localhost':
                success, message = self.test_localhost_link(link)
            elif link_type == 'local_file':
                success, message = self.test_local_file(link, base_path)
            else:
                success, message = False, "Unknown link type"
            
            # Print result
            if success:
                print(f"   ✅ {message}")
                self.results['working'].append((link, message))
            else:
                print(f"   ❌ {message}")
                self.results['failed'].append((link, message))
            
            # Categorize by type for summary
            if link_type == 'localhost':
                self.results['localhost'].append((link, success, message))
            elif link_type == 'local_file':
                self.results['local_files'].append((link, success, message))
            
            # Small delay to be nice to servers
            time.sleep(0.1)
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n" + "=" * 60)
        print("📊 LINK TESTING SUMMARY")
        print("=" * 60)
        
        total_links = len(self.results['working']) + len(self.results['failed'])
        working_count = len(self.results['working'])
        failed_count = len(self.results['failed'])
        
        print(f"Total Links Tested: {total_links}")
        print(f"✅ Working: {working_count}")
        print(f"❌ Failed: {failed_count}")
        
        if failed_count > 0:
            print(f"\n💔 Failed Links:")
            for link, message in self.results['failed']:
                print(f"   • {link} - {message}")
        
        # Localhost summary
        localhost_failed = [item for item in self.results['localhost'] if not item[1]]
        if localhost_failed:
            print(f"\n🏠 Localhost Services Not Running:")
            for link, success, message in localhost_failed:
                print(f"   • {link} - {message}")
        
        # Local file issues
        file_failed = [item for item in self.results['local_files'] if not item[1]]
        if file_failed:
            print(f"\n📁 Missing Local Files:")
            for link, success, message in file_failed:
                print(f"   • {link} - {message}")
        
        print(f"\n🎯 Success Rate: {(working_count/total_links)*100:.1f}%" if total_links > 0 else "No links tested")

def main():
    print("🔗 HTML Link Tester for AI Research Platform")
    print("=" * 60)
    
    # Files to test
    files_to_test = [
        '/home/keith/chat-copilot/webapp/public/control-panel.html',
        '/home/keith/chat-copilot/webapp/public/applications.html'
    ]
    
    tester = LinkTester(timeout=10)
    
    for file_path in files_to_test:
        if Path(file_path).exists():
            tester.test_all_links(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    
    tester.print_summary()

if __name__ == "__main__":
    main()