#!/usr/bin/env python3
"""
Port Configuration Validator for AI Research Platform
Prevents configuration drift by validating and fixing port assignments
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple


class PortConfigValidator:
    """Validates and enforces port configuration standards"""

    def __init__(self):
        # Use environment variable or detect current directory
        platform_root = os.environ.get('PLATFORM_ROOT')
        if platform_root:
            self.platform_dir = Path(platform_root)
        else:
            # Auto-detect platform directory
            current_dir = Path.cwd()
            # Look for key files to identify platform root
            key_files = ['CLAUDE.md', 'CopilotChat.sln', 'webapi', 'webapp']
            
            # Check current directory and parents
            for potential_root in [current_dir] + list(current_dir.parents):
                if all((potential_root / key_file).exists() for key_file in key_files[:2]):
                    self.platform_dir = potential_root
                    break
            else:
                # Fallback to current directory
                self.platform_dir = current_dir
        self.standard_ports = {
            "chat_copilot_backend": 11000,
            "autogen_studio": 11001,
            "webhook_server": 11025,
            "magentic_one": 11003,
            "port_scanner": 11010,
            "nginx_proxy_manager_web": 8080,
            "nginx_proxy_manager_admin": 11082,
            "nginx_proxy_manager_https": 8443,
            "perplexica": 11020,
            "searxng": 11021,
            "openwebui": 11880,
            "ollama": 11434,
            "vscode_web": 57081,
            "windmill": 11006,
            "ntopng": 8888,
            "neo4j_web": 7474,
            "neo4j_bolt": 7687,
            "genai_stack_frontend": 8505,
            "genai_stack_api": 8504,
            "genai_stack_bot": 8501,
            "genai_stack_pdf_bot": 8503,
            "genai_stack_loader": 8509,
            "frontend_dev": 3000,
        }

        # Old ports that should be replaced (only for active services)
        self.deprecated_ports = {
            # Only flag ports for services that are still active but using wrong ports
            # Removed services (webhook, fortinet, etc.) are intentionally not flagged
        }

        # Removed/obsolete services - these are OK to have in old configs
        self.removed_services = {
            11002: "webhook_server_removed",
            11080: "nginx_proxy_manager_removed",
            11081: "nginx_proxy_manager_http_removed",
            3001: "fortinet_manager_removed",
            5000: "fortinet_api_removed",
        }

    def scan_files_for_ports(self) -> Dict[str, List[Tuple[int, str]]]:
        """Scan all configuration files for port references"""

        print("🔍 Scanning files for port configurations...")

        file_patterns = [
            "*.py",
            "*.sh",
            "*.js",
            "*.json",
            "*.md",
            "*.txt",
            "*.conf",
            "*.env",
            "*.yml",
            "*.yaml",
        ]

        results = {}
        port_pattern = r"\b(?:port|PORT)\s*[:=]\s*(\d+)|:\d{4,5}\b|localhost:(\d{4,5})|0\.0\.0\.0:(\d{4,5})|100\.123\.10\.72:(\d{4,5})"

        for pattern in file_patterns:
            for file_path in self.platform_dir.rglob(pattern):
                # Skip certain directories
                if any(
                    skip in str(file_path)
                    for skip in [
                        "node_modules",
                        ".git",
                        "build",
                        "__pycache__",
                        ".venv",
                    ]
                ):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        matches = re.findall(port_pattern, content)

                        if matches:
                            ports_found = []
                            for match in matches:
                                port = next((p for p in match if p), None)
                                if port and port.isdigit():
                                    port_num = int(port)
                                    if 1000 <= port_num <= 65535:  # Valid port range
                                        ports_found.append((port_num, str(file_path)))

                            if ports_found:
                                results[str(file_path)] = ports_found

                except Exception as e:
                    continue

        return results

    def check_port_violations(self, scan_results: Dict) -> List[Dict]:
        """Check for port configuration violations"""

        violations = []

        for file_path, ports in scan_results.items():
            for port_num, _ in ports:
                # Only flag deprecated ports, not removed services
                if port_num in self.deprecated_ports:
                    service = self.deprecated_ports[port_num]
                    correct_port = self.standard_ports.get(service)

                    violations.append(
                        {
                            "file": file_path,
                            "old_port": port_num,
                            "new_port": correct_port,
                            "service": service,
                            "severity": "high",
                        }
                    )
                # Skip ports for removed services - these are expected in old configs

        return violations

    def generate_fix_script(self, violations: List[Dict]) -> str:
        """Generate a script to fix port violations"""

        script_lines = [
            "#!/bin/bash",
            "# Auto-generated port configuration fix script",
            "# Generated by Port Configuration Validator",
            "",
            "set -e",
            "echo '🔧 Fixing port configuration violations...'",
            "",
        ]

        for violation in violations:
            file_path = violation["file"]
            old_port = violation["old_port"]
            new_port = violation["new_port"]

            if new_port:
                script_lines.append(
                    f"echo 'Fixing {file_path}: {old_port} -> {new_port}'"
                )
                script_lines.append(
                    f"sed -i 's/:{old_port}\\b/:{new_port}/g' '{file_path}'"
                )
                script_lines.append(
                    f"sed -i 's/port.*{old_port}/port {new_port}/g' '{file_path}'"
                )
                script_lines.append("")

        script_lines.extend(
            [
                "echo '✅ Port configuration fixes applied'",
                "echo '🔄 Please restart services to apply changes'",
            ]
        )

        return "\n".join(script_lines)

    def create_port_config_file(self):
        """Create a definitive port configuration file"""

        config = {
            "ai_research_platform_ports": {
                "version": "2.0",
                "last_updated": "2025-06-15",
                "standard_ports": self.standard_ports,
                "deprecated_ports": self.deprecated_ports,
                "port_ranges": {
                    "ai_services": "11000-11099",
                    "network_tools": "11100-11199",
                    "development": "3000, 57081",
                    "system": "11434",
                },
                "validation_rules": [
                    "All AI services must use ports 11000-11099",
                    "Network tools use ports 11100-11199",
                    "No services on deprecated ports",
                    "Use UV for Python environment management",
                ],
            }
        }

        config_file = self.platform_dir / "port-configuration.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        print(f"✅ Created port configuration file: {config_file}")
        return config_file

    def create_validation_hooks(self):
        """Create git hooks and cron jobs for validation"""

        # Pre-commit hook
        pre_commit_hook = f"""#!/bin/bash
# Port Configuration Validation Hook

echo "🔍 Checking port configurations..."
python3 {self.platform_dir}/port-config-validator.py --check

if [ $? -ne 0 ]; then
    echo "❌ Port configuration violations found!"
    echo "Run: python3 {self.platform_dir}/port-config-validator.py --fix"
    exit 1
fi

echo "✅ Port configurations validated"
"""

        # Cron job entry
        cron_job = f"0 * * * * python3 {self.platform_dir}/port-config-validator.py --check --quiet"

        hooks_dir = self.platform_dir / ".git" / "hooks"
        if hooks_dir.exists():
            pre_commit_file = hooks_dir / "pre-commit"
            with open(pre_commit_file, "w") as f:
                f.write(pre_commit_hook)
            os.chmod(pre_commit_file, 0o755)
            print("✅ Created git pre-commit hook")

        print(f"📅 Add this to crontab for hourly validation:")
        print(f"   {cron_job}")

    def run_validation(self, fix_mode: bool = False) -> bool:
        """Run full port configuration validation"""

        print("🔍 AI Research Platform Port Configuration Validator")
        print("=" * 60)

        # Scan for ports
        scan_results = self.scan_files_for_ports()
        print(f"📊 Scanned {len(scan_results)} files with port references")

        # Check violations
        violations = self.check_port_violations(scan_results)

        if not violations:
            print("✅ No port configuration violations found!")
            self.create_port_config_file()
            return True

        print(f"⚠️ Found {len(violations)} port configuration violations:")

        for violation in violations:
            print(f"   🔴 {violation['file']}")
            print(
                f"      Port {violation['old_port']} -> {violation['new_port']} ({violation['service']})"
            )

        if fix_mode:
            print("\n🔧 Applying fixes...")
            fix_script = self.generate_fix_script(violations)

            fix_script_file = self.platform_dir / "fix-ports.sh"
            with open(fix_script_file, "w") as f:
                f.write(fix_script)
            os.chmod(fix_script_file, 0o755)

            print(f"✅ Created fix script: {fix_script_file}")
            print("🚀 Run ./fix-ports.sh to apply fixes")

        self.create_port_config_file()
        return len(violations) == 0


def main():
    """Main validation function"""
    import sys

    validator = PortConfigValidator()

    # Parse arguments
    check_mode = "--check" in sys.argv
    fix_mode = "--fix" in sys.argv
    quiet_mode = "--quiet" in sys.argv

    if not quiet_mode:
        print("🔍 Port Configuration Validator v2.0")
        print("Standardized ports: 11000-12000 range")
        print("")

    success = validator.run_validation(fix_mode=fix_mode)

    if check_mode and not success:
        sys.exit(1)

    if not quiet_mode:
        validator.create_validation_hooks()

        print("\n🎯 Port Configuration Standards:")
        print("   🏠 Backend: 11000")
        print("   🤖 AutoGen: 11001")
        print("   🔗 Webhook: 11002")
        print("   🌟 Magentic-One: 11003")
        print("   🔍 Port Scanner: 11010")
        print("   🦙 Ollama: 11434")


if __name__ == "__main__":
    main()
