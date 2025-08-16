#!/usr/bin/env python3
"""
Secret File Format Converter
Converts various secret file formats to the standard format for bulk import

Supports:
- PowerShell format: SECRET_NAME -Value 'value'
- Environment format: SECRET_NAME=value
- JSON format: {"SECRET_NAME": "value"}
- YAML format: SECRET_NAME: value
"""

import re
import sys
import json
import yaml
from pathlib import Path

def detect_format(content: str) -> str:
    """Auto-detect the format of the secrets file"""
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
    
    if not lines:
        return 'unknown'
    
    # Check for JSON
    try:
        json.loads(content)
        return 'json'
    except:
        pass
    
    # Check for YAML
    try:
        yaml.safe_load(content)
        # Additional check to ensure it's actually YAML and not just plain text
        if ':' in lines[0] and not '=' in lines[0] and not '-Value' in lines[0]:
            return 'yaml'
    except:
        pass
    
    # Check for PowerShell format
    if any('-Value' in line for line in lines):
        return 'powershell'
    
    # Check for environment format
    if any('=' in line and not '-Value' in line for line in lines):
        return 'env'
    
    return 'unknown'

def convert_powershell_format(content: str) -> str:
    """Convert PowerShell format: SECRET_NAME -Value 'value'"""
    converted_lines = []
    
    for line_num, line in enumerate(content.split('\n'), 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            converted_lines.append(line)
            continue
        
        # Match PowerShell format: SECRET_NAME -Value 'value' or SECRET_NAME -Value "value"
        match = re.match(r"^([A-Z_][A-Z0-9_]*)\s+-Value\s+['\"](.+?)['\"]?$", line, re.IGNORECASE)
        if match:
            secret_name = match.group(1).upper()
            secret_value = match.group(2)
            converted_lines.append(f"{secret_name}={secret_value}")
        else:
            # Try without quotes
            match = re.match(r"^([A-Z_][A-Z0-9_]*)\s+-Value\s+(.+)$", line, re.IGNORECASE)
            if match:
                secret_name = match.group(1).upper()
                secret_value = match.group(2)
                converted_lines.append(f"{secret_name}={secret_value}")
            else:
                print(f"Warning: Could not parse line {line_num}: {line}")
                converted_lines.append(f"# UNPARSED: {line}")
    
    return '\n'.join(converted_lines)

def convert_json_format(content: str) -> str:
    """Convert JSON format: {"SECRET_NAME": "value"}"""
    try:
        data = json.loads(content)
        converted_lines = ['# Converted from JSON format']
        
        for key, value in data.items():
            key = key.upper().replace('-', '_').replace(' ', '_')
            converted_lines.append(f"{key}={value}")
        
        return '\n'.join(converted_lines)
    except Exception as e:
        raise ValueError(f"Invalid JSON format: {e}")

def convert_yaml_format(content: str) -> str:
    """Convert YAML format: SECRET_NAME: value"""
    try:
        data = yaml.safe_load(content)
        converted_lines = ['# Converted from YAML format']
        
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        if isinstance(data, dict):
            flat_data = flatten_dict(data)
            for key, value in flat_data.items():
                key = key.upper().replace('-', '_').replace(' ', '_')
                converted_lines.append(f"{key}={value}")
        
        return '\n'.join(converted_lines)
    except Exception as e:
        raise ValueError(f"Invalid YAML format: {e}")

def convert_env_format(content: str) -> str:
    """Convert environment format: SECRET_NAME=value (already correct, just validate)"""
    converted_lines = []
    
    for line_num, line in enumerate(content.split('\n'), 1):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            converted_lines.append(line)
            continue
        
        # Validate environment format
        if '=' in line:
            name, value = line.split('=', 1)
            name = name.strip().upper()
            # Ensure valid secret name format
            if re.match(r'^[A-Z_][A-Z0-9_]*$', name):
                converted_lines.append(f"{name}={value}")
            else:
                print(f"Warning: Invalid secret name on line {line_num}: {name}")
                converted_lines.append(f"# INVALID_NAME: {line}")
        else:
            print(f"Warning: No '=' found on line {line_num}: {line}")
            converted_lines.append(f"# UNPARSED: {line}")
    
    return '\n'.join(converted_lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert-secrets-format.py <input_file> [output_file]")
        print()
        print("Converts various secret file formats to the standard format:")
        print("  PowerShell: SECRET_NAME -Value 'value'")
        print("  JSON:       {\"SECRET_NAME\": \"value\"}")
        print("  YAML:       SECRET_NAME: value")
        print("  Env:        SECRET_NAME=value")
        print()
        print("If output_file is not provided, writes to <input_file>.converted")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"{input_file}.converted"
    
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    print(f"🔄 Converting secrets file format...")
    print(f"📥 Input:  {input_file}")
    print(f"📤 Output: {output_file}")
    print()
    
    # Read input file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Failed to read input file: {e}")
        sys.exit(1)
    
    # Detect format
    format_type = detect_format(content)
    print(f"🔍 Detected format: {format_type}")
    
    # Convert based on format
    try:
        if format_type == 'powershell':
            converted = convert_powershell_format(content)
        elif format_type == 'json':
            converted = convert_json_format(content)
        elif format_type == 'yaml':
            converted = convert_yaml_format(content)
        elif format_type == 'env':
            converted = convert_env_format(content)
        else:
            print(f"❌ Unknown or unsupported format: {format_type}")
            print("Supported formats: PowerShell, JSON, YAML, Environment")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        sys.exit(1)
    
    # Write output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Add header comment
            f.write(f"# Converted from {format_type} format\n")
            f.write(f"# Original file: {input_file}\n")
            f.write(f"# Generated by convert-secrets-format.py\n\n")
            f.write(converted)
    except Exception as e:
        print(f"❌ Failed to write output file: {e}")
        sys.exit(1)
    
    # Count secrets
    secret_count = len([line for line in converted.split('\n') 
                       if line.strip() and not line.strip().startswith('#') and '=' in line])
    
    print(f"✅ Conversion completed successfully!")
    print(f"📊 Found {secret_count} secrets")
    print()
    print("Next steps:")
    print(f"1. Review: cat {output_file}")
    print(f"2. Validate: python3 scripts/security/bulk-import-secrets.py {output_file} --validate")
    print(f"3. Import: python3 scripts/security/bulk-import-secrets.py {output_file} --dry-run")

if __name__ == '__main__':
    main()