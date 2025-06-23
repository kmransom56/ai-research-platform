#!/bin/bash

# CSR Submission Script for CA Server Integration
# Note: The /api/sign-csr endpoint needs to be implemented on the CA server

set -e

# Configuration
CA_SERVER="192.168.0.2"
CA_PORT="443"
API_ENDPOINT="/api/sign-csr"

# Default values
VALIDITY_DAYS=365
USE_HTTP=false

# Usage function
usage() {
    cat << EOF
Usage: $0 -f CSR_FILE [OPTIONS]

Submit a Certificate Signing Request (CSR) to the CA server

Required:
  -f, --csr-file CSR_FILE          Path to the CSR file (.csr or .pem)

Optional:
  -c, --ca-name CA_NAME            CA name to use for signing
  -d, --days DAYS                  Validity period in days (default: 365)
  -a, --sans SANS                  Subject Alternative Names (comma-separated)
  -s, --server SERVER              CA server address (default: 192.168.0.2)
  --port PORT                      CA server port (default: 443)
  --http                           Use HTTP instead of HTTPS
  -h, --help                       Show this help message

Examples:
  $0 -f my-server.csr
  $0 -f web.csr -c "Intermediate CA" -d 730
  $0 -f api.csr -a "api.example.com,192.168.1.100"

Note: The /api/sign-csr endpoint is not yet implemented on the CA server.
      This script is prepared for when that endpoint becomes available.
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--csr-file)
            CSR_FILE="$2"
            shift 2
            ;;
        -c|--ca-name)
            CA_NAME="$2"
            shift 2
            ;;
        -d|--days)
            VALIDITY_DAYS="$2"
            shift 2
            ;;
        -a|--sans)
            SANS="$2"
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
if [[ -z "$CSR_FILE" ]]; then
    echo "Error: CSR file is required"
    usage
    exit 1
fi

if [[ ! -f "$CSR_FILE" ]]; then
    echo "Error: CSR file '$CSR_FILE' not found"
    exit 1
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

echo "Submitting CSR: $CSR_FILE"
echo "CA Server: $CA_URL"
echo "Validity: $VALIDITY_DAYS days"
if [[ -n "$CA_NAME" ]]; then
    echo "CA Name: $CA_NAME"
fi
if [[ -n "$SANS" ]]; then
    echo "SANs: $SANS"
fi
echo

# Check if the API endpoint exists first
echo "Checking if CSR submission endpoint is available..."
check_response=$(curl -s -k -X GET "$CA_URL" \
    --max-time 10 \
    --connect-timeout 5 || echo "")

if [[ -z "$check_response" ]]; then
    echo "❌ Error: Cannot connect to CA server at $CA_URL"
    echo
    echo "Troubleshooting steps:"
    echo "1. Verify the CA server is running on $CA_SERVER:$CA_PORT"
    echo "2. Check network connectivity"
    echo "3. Try using --http flag if HTTPS is not configured"
    exit 1
fi

# Check if the response indicates the endpoint doesn't exist
if echo "$check_response" | grep -q "404\|Not Found\|Cannot GET"; then
    echo "❌ The /api/sign-csr endpoint is not yet implemented on the CA server."
    echo
    echo "Available alternatives:"
    echo "1. Use the generate-certificate.sh script to generate new certificates"
    echo "2. Request the CA server administrator to implement the /api/sign-csr endpoint"
    echo "3. Use the CA server's web interface to manually upload the CSR"
    echo
    echo "To implement the missing endpoint, add this to the CA server:"
    echo "File: /opt/cert-manager/src/app/api/sign-csr/route.js"
    exit 1
fi

# Prepare the multipart form data
echo "Preparing CSR submission..."

# Create a temporary form data
temp_boundary="----WebKitFormBoundary$(date +%s)$(shuf -i 1000-9999 -n 1)"

# Build form data
form_data="--${temp_boundary}\r\n"
form_data+="Content-Disposition: form-data; name=\"csr\"; filename=\"$(basename "$CSR_FILE")\"\r\n"
form_data+="Content-Type: application/x-pem-file\r\n\r\n"
form_data+="$(cat "$CSR_FILE")\r\n"
form_data+="--${temp_boundary}\r\n"
form_data+="Content-Disposition: form-data; name=\"validityDays\"\r\n\r\n"
form_data+="$VALIDITY_DAYS\r\n"

if [[ -n "$CA_NAME" ]]; then
    form_data+="--${temp_boundary}\r\n"
    form_data+="Content-Disposition: form-data; name=\"caName\"\r\n\r\n"
    form_data+="$CA_NAME\r\n"
fi

if [[ -n "$SANS" ]]; then
    form_data+="--${temp_boundary}\r\n"
    form_data+="Content-Disposition: form-data; name=\"sans\"\r\n\r\n"
    form_data+="$(echo "$SANS" | jq -R 'split(",") | map(gsub("^\\s+|\\s+$"; ""))' 2>/dev/null || echo "[]")\r\n"
fi

form_data+="--${temp_boundary}--\r\n"

# Make the API request
echo "Submitting CSR to CA server..."
response=$(curl -s -k -X POST "$CA_URL" \
    -H "Content-Type: multipart/form-data; boundary=${temp_boundary}" \
    -d "$form_data" \
    --max-time 300 \
    --connect-timeout 30)

# Check if curl was successful
if [[ $? -ne 0 ]]; then
    echo "Error: Failed to submit CSR to CA server at $CA_URL"
    exit 1
fi

# Parse the response
echo "Response received:"
echo "$response" | jq . 2>/dev/null || echo "$response"

# Check if the request was successful
success=$(echo "$response" | jq -r '.success // false' 2>/dev/null)

if [[ "$success" == "true" ]]; then
    echo
    echo "✅ CSR submitted and certificate signed successfully!"
    
    # Check for download link
    download_link=$(echo "$response" | jq -r '.downloadLink // empty' 2>/dev/null)
    if [[ -n "$download_link" ]]; then
        echo "Download link: $download_link"
    fi
    
    # Save certificate if provided in response
    certificate=$(echo "$response" | jq -r '.certificate // empty' 2>/dev/null)
    if [[ -n "$certificate" && "$certificate" != "null" ]]; then
        cert_filename="${CSR_FILE%.csr}.crt"
        cert_filename="${cert_filename%.pem}.crt"
        echo "$certificate" > "$cert_filename"
        echo "Certificate saved as: $cert_filename"
    fi
    
else
    echo
    echo "❌ CSR submission failed!"
    error_msg=$(echo "$response" | jq -r '.error // "Unknown error"' 2>/dev/null)
    echo "Error: $error_msg"
    
    exit 1
fi