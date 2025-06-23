#!/bin/bash

# Certificate Generation Script for CA Server Integration
# Uses the correct API endpoints identified on the CA server at 192.168.0.2

set -e

# Configuration
CA_SERVER="192.168.0.2"
CA_PORT="443"
API_ENDPOINT="/api/generate-cert"

# Default values
CERTIFICATE_TYPE="server"
VALIDITY_DAYS=365
KEY_SIZE=2048
OUTPUT_FORMAT="pem"
USE_HTTP=false

# Usage function
usage() {
    cat << EOF
Usage: $0 -n SERVER_NAME [OPTIONS]

Generate certificates using the CA server API

Required:
  -n, --server-name SERVER_NAME    Domain or server name for the certificate

Optional:
  -i, --server-ip IP_ADDRESS       IP address for Subject Alternative Name
  -t, --type TYPE                  Certificate type (server, https, nginx, web, fixed, temp, direct)
  -p, --password PASSWORD          CA password if required
  -d, --days DAYS                  Validity period in days (default: 365)
  -k, --key-size SIZE              Key size in bits (default: 2048)
  -f, --format FORMAT              Output format (pem, der) (default: pem)
  -s, --server SERVER              CA server address (default: 192.168.0.2)
  --port PORT                      CA server port (default: 443)
  --http                           Use HTTP instead of HTTPS
  -h, --help                       Show this help message

Certificate Types:
  server    - Standard server certificate
  https     - HTTPS server certificate
  nginx     - Nginx web server certificate
  web       - Web application certificate
  fixed     - Fixed IP certificate
  temp      - Temporary certificate
  direct    - Direct certificate creation

Examples:
  $0 -n example.com
  $0 -n web.example.com -i 192.168.1.100 -t nginx
  $0 -n api.example.com -t https -d 730 -p mypassword
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--server-name)
            SERVER_NAME="$2"
            shift 2
            ;;
        -i|--server-ip)
            SERVER_IP="$2"
            shift 2
            ;;
        -t|--type)
            CERTIFICATE_TYPE="$2"
            shift 2
            ;;
        -p|--password)
            CA_PASSWORD="$2"
            shift 2
            ;;
        -d|--days)
            VALIDITY_DAYS="$2"
            shift 2
            ;;
        -k|--key-size)
            KEY_SIZE="$2"
            shift 2
            ;;
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -s|--server)
            CA_SERVER="$2"
            shift 2
            ;;
        --port)
            CA_PORT="$2"
            shift 2
            ;;
        --http)
            USE_HTTP=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$SERVER_NAME" ]]; then
    echo "Error: Server name is required"
    usage
    exit 1
fi

# Build the JSON payload
json_payload=$(cat << EOF
{
    "serverName": "$SERVER_NAME",
    "certificateType": "$CERTIFICATE_TYPE",
    "validityDays": $VALIDITY_DAYS,
    "keySize": $KEY_SIZE,
    "outputFormat": "$OUTPUT_FORMAT"
EOF
)

# Add optional fields
if [[ -n "$SERVER_IP" ]]; then
    json_payload=$(echo "$json_payload" | sed 's/}$/,\n    "serverIp": "'"$SERVER_IP"'"\n}/')
fi

if [[ -n "$CA_PASSWORD" ]]; then
    json_payload=$(echo "$json_payload" | sed 's/}$/,\n    "caPassword": "'"$CA_PASSWORD"'"\n}/')
fi

# Determine protocol
if [[ "$USE_HTTP" == true ]]; then
    PROTOCOL="http"
    if [[ "$CA_PORT" == "443" ]]; then
        CA_PORT="3000"  # Default HTTP port for Next.js
    fi
else
    PROTOCOL="https"
fi

# Build the URL
CA_URL="${PROTOCOL}://${CA_SERVER}:${CA_PORT}${API_ENDPOINT}"

echo "Generating certificate for: $SERVER_NAME"
echo "Certificate type: $CERTIFICATE_TYPE"
echo "CA Server: $CA_URL"
echo "Validity: $VALIDITY_DAYS days"
if [[ -n "$SERVER_IP" ]]; then
    echo "Server IP: $SERVER_IP"
fi
echo

# Make the API request
echo "Sending certificate generation request..."
echo "Payload: $json_payload"
echo

response=$(curl -s -k -X POST "$CA_URL" \
    -H "Content-Type: application/json" \
    -d "$json_payload" \
    --max-time 300 \
    --connect-timeout 30)

# Check if curl was successful
if [[ $? -ne 0 ]]; then
    echo "Error: Failed to connect to CA server at $CA_URL"
    exit 1
fi

# Parse the response
echo "Response received:"
echo "$response" | jq . 2>/dev/null || echo "$response"

# Check if the request was successful
success=$(echo "$response" | jq -r '.success // false' 2>/dev/null)

if [[ "$success" == "true" ]]; then
    echo
    echo "✅ Certificate generated successfully!"
    
    # Extract certificate information
    cert_path=$(echo "$response" | jq -r '.certificate.certificatePath // empty' 2>/dev/null)
    key_path=$(echo "$response" | jq -r '.certificate.keyPath // empty' 2>/dev/null)
    chain_path=$(echo "$response" | jq -r '.certificate.chainPath // empty' 2>/dev/null)
    
    if [[ -n "$cert_path" ]]; then
        echo "Certificate: $cert_path"
    fi
    if [[ -n "$key_path" ]]; then
        echo "Private Key: $key_path"
    fi
    if [[ -n "$chain_path" ]]; then
        echo "Certificate Chain: $chain_path"
    fi
    
    # Show certificate details if available
    subject=$(echo "$response" | jq -r '.certificate.subject // empty' 2>/dev/null)
    not_after=$(echo "$response" | jq -r '.certificate.notAfter // empty' 2>/dev/null)
    
    if [[ -n "$subject" ]]; then
        echo "Subject: $subject"
    fi
    if [[ -n "$not_after" ]]; then
        echo "Expires: $not_after"
    fi
    
else
    echo
    echo "❌ Certificate generation failed!"
    error_msg=$(echo "$response" | jq -r '.error // "Unknown error"' 2>/dev/null)
    echo "Error: $error_msg"
    
    # Show additional details if available
    details=$(echo "$response" | jq -r '.details // empty' 2>/dev/null)
    if [[ -n "$details" && "$details" != "null" ]]; then
        echo "Details: $details"
    fi
    
    exit 1
fi