#!/usr/bin/env python3
"""
Fix HTML Links in Control Panel and Applications Pages
Updates URLs to use consistent localhost addresses for working services
"""

import re
import os
from pathlib import Path

class HTMLLinkFixer:
    def __init__(self):
        # URL mappings for fixing
        self.url_fixes = {
            # Remove broken Google Font preconnect links that return 404
            r'<link rel="preconnect" href="https://fonts\.googleapis\.com">': '',
            r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>': '',
            
            # Fix Tailscale URLs to localhost for services that are actually running
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:3000': 'http://localhost:3000',
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:11001': 'http://localhost:11001',
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:7474': 'http://localhost:7474',
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:8501': 'http://localhost:8501',
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:8502': 'http://localhost:8502',
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:8505': 'http://localhost:8505',
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:11000': 'http://localhost:11000',
            
            # Fix broken API endpoints to working ones
            r'href="/v1/restaurant/network"': 'href="http://localhost:11030"',
            r'href="/vscode/login"': 'href="http://localhost:8080"',  # Common VS Code port
            r'href="/copilot/healthz"': 'href="http://localhost:3000/healthz"',
            r'href="/fortinet/"': 'href="http://localhost:11030"',
            
            # Remove broken links
            r'href="…"': 'href="#"',
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:11880': 'http://localhost:11880',  # OpenWebUI if running
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:11020': 'http://localhost:11020',  # Perplexica if running
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:11007': 'http://localhost:11007',  # Windmill if running
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:11434': 'http://localhost:11434',  # Ollama if running
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:6333/dashboard': 'http://localhost:6333/dashboard',  # Qdrant if running
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:11006': 'http://localhost:11006',  # Windmill container if running
            r'https://ubuntuaicodeserver-1\.tail5137b4\.ts\.net:57081': 'http://localhost:57081',  # Unknown service
        }
    
    def fix_file(self, file_path):
        """Fix links in a single HTML file"""
        print(f"🔧 Fixing links in: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes_made = 0
            
            # Apply all URL fixes
            for pattern, replacement in self.url_fixes.items():
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    matches = len(re.findall(pattern, content))
                    changes_made += matches
                    print(f"   ✅ Fixed {matches} instances of: {pattern[:50]}...")
                    content = new_content
            
            # Write back if changes were made
            if changes_made > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"   📝 Saved {changes_made} changes to {file_path}")
            else:
                print(f"   ✨ No changes needed for {file_path}")
                
        except Exception as e:
            print(f"   ❌ Error fixing {file_path}: {e}")
    
    def add_service_availability_check(self, file_path):
        """Add JavaScript to check service availability and update link status"""
        
        js_code = '''
<script>
// Service availability checker
async function checkServiceAvailability() {
    const services = [
        { port: 3000, name: 'Chat Copilot' },
        { port: 11001, name: 'AutoGen Studio' },
        { port: 7474, name: 'Neo4j' },
        { port: 8501, name: 'GenAI Stack Bot' },
        { port: 8502, name: 'GenAI Stack Loader' },
        { port: 11030, name: 'Network Voice Interface' },
        { port: 11002, name: 'Grafana' },
        { port: 11032, name: 'Restaurant Voice' },
        { port: 11040, name: 'Network Management Hub' },
        { port: 9000, name: 'AI Stack Gateway' },
    ];
    
    for (const service of services) {
        try {
            const response = await fetch(`http://localhost:${service.port}/`, { 
                method: 'HEAD',
                mode: 'no-cors',
                timeout: 2000 
            });
            // Mark service as available
            const links = document.querySelectorAll(`a[href*="${service.port}"]`);
            links.forEach(link => {
                link.style.borderLeft = '3px solid #10b981';
                link.title = `${service.name} - Available`;
            });
        } catch (error) {
            // Mark service as unavailable
            const links = document.querySelectorAll(`a[href*="${service.port}"]`);
            links.forEach(link => {
                link.style.borderLeft = '3px solid #ef4444';
                link.style.opacity = '0.6';
                link.title = `${service.name} - Not Available`;
            });
        }
    }
}

// Run check on page load
document.addEventListener('DOMContentLoaded', checkServiceAvailability);

// Add click handler to show service status
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.href.includes('localhost')) {
        const url = new URL(e.target.href);
        if (e.target.style.opacity === '0.6') {
            e.preventDefault();
            alert(`Service on port ${url.port} appears to be offline. Please start the service first.`);
        }
    }
});
</script>
'''
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add script before closing body tag if not already present
            if 'checkServiceAvailability' not in content:
                content = content.replace('</body>', f'{js_code}\n</body>')
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                print(f"   ⚡ Added service availability checker to {file_path}")
            else:
                print(f"   ✨ Service checker already present in {file_path}")
                
        except Exception as e:
            print(f"   ❌ Error adding service checker to {file_path}: {e}")

def main():
    print("🔗 HTML Link Fixer for AI Research Platform")
    print("=" * 50)
    
    # Files to fix
    files_to_fix = [
        '/home/keith/chat-copilot/webapp/public/control-panel.html',
        '/home/keith/chat-copilot/webapp/public/applications.html'
    ]
    
    fixer = HTMLLinkFixer()
    
    for file_path in files_to_fix:
        if Path(file_path).exists():
            fixer.fix_file(file_path)
            fixer.add_service_availability_check(file_path)
        else:
            print(f"❌ File not found: {file_path}")
    
    print("\n🎉 Link fixing complete!")
    print("✨ All HTML files now have:")
    print("   • Fixed URL mappings for working services") 
    print("   • Removed broken Google Font preconnect links")
    print("   • JavaScript service availability checking")
    print("   • Visual indicators for offline services")

if __name__ == "__main__":
    main()