#!/bin/bash

# Certificate Operations Script for CA Server Integration
# Uses the /api/certificate-operations endpoint

set -e

# Configuration
CA_SERVER="192.168.0.2"
CA_PORT="443"
API_ENDPOINT="/api/certificate-operations"

# Default values
USE_HTTP=false

# Usage function
usage() {
    cat << EOF
Usage: $0 -o OPERATION -c CERTIFICATE_NAME [OPTIONS]

Perform operations on certificates via the CA server

Required:
  -o, --operation OPERATION        Operation to perform
  -c, --certificate CERT_NAME      Certificate name to operate on

Operations:
  validate        - Validate certificate and chain
  export-browser  - Export certificate for browser import
  trust          - Trust certificate in system
  backup         - Backup certificate files

Optional:
  -s, --server SERVER              CA server address (default: 192.168.0.2)
  --port PORT                      CA server port (default: 443)
  --http                           Use HTTP instead of HTTPS
  -h, --help                       Show this help message

Examples:
  $0 -o validate -c example.com
  $0 -o export-browser -c web-server
  $0 -o backup -c api.example.com
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--operation)
            OPERATION="$2"
            shift 2
            ;;
        -c|--certificate)
            CERTIFICATE_NAME="$2"
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
if [[ -z "$OPERATION" ]]; then
    echo "Error: Operation is required"
    usage
    exit 1
fi

if [[ -z "$CERTIFICATE_NAME" ]]; then
    echo "Error: Certificate name is required"
    usage
    exit 1
fi

# Validate operation
case "$OPERATION" in
    validate|export-browser|trust|backup)
        ;;
    *)
        echo "Error: Invalid operation '$OPERATION'"
        echo "Valid operations: validate, export-browser, trust, backup"
        exit 1
        ;;
esac

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

# Build the JSON payload
json_payload=$(cat << EOF
{
    "operation": "$OPERATION",
    "certificateName": "$CERTIFICATE_NAME"
}
EOF
)

echo "Performing operation '$OPERATION' on certificate '$CERTIFICATE_NAME'"
echo "CA Server: $CA_URL"
echo

# Make the API request
echo "Sending request..."
response=$(curl -s -k -X POST "$CA_URL" \
    -H "Content-Type: application/json" \
    -d "$json_payload" \
    --max-time 120 \
    --connect-timeout 30)

# Check if curl was successful
if [[ $? -ne 0 ]]; then
    echo "Error: Failed to connect to CA server at $CA_URL"
    exit 1
fi

# Check if we got a 404 error (endpoint not implemented)
if echo "$response" | grep -q "404\|This page could not be found"; then
    echo "❌ The /api/certificate-operations endpoint is not properly implemented."
    echo
    echo "This endpoint exists as a file but uses Pages Router syntax in an App Router directory."
    echo "It needs to be converted to App Router format."
    echo
    echo "Alternative: Use the generate-certificate.sh script for certificate generation"
    echo "and manual verification on the CA server for certificate management."
    exit 1
fi

# Parse the response
echo "Response received:"
echo "$response" | jq . 2>/dev/null || echo "$response"

# Check if the request was successful
success=$(echo "$response" | jq -r '.success // false' 2>/dev/null)

if [[ "$success" == "true" ]]; then
    echo
    echo "✅ Operation '$OPERATION' completed successfully!"
    
    # Show operation-specific results
    case "$OPERATION" in
        validate)
            cert_valid=$(echo "$response" | jq -r '.validation.certificateValid // false' 2>/dev/null)
            chain_valid=$(echo "$response" | jq -r '.validation.chainValid // false' 2>/dev/null)
            
            echo "Certificate validation: $([[ "$cert_valid" == "true" ]] && echo "✅ Valid" || echo "❌ Invalid")"
            echo "Chain validation: $([[ "$chain_valid" == "true" ]] && echo "✅ Valid" || echo "❌ Invalid")"
            
            chain_error=$(echo "$response" | jq -r '.validation.chainError // empty' 2>/dev/null)
            if [[ -n "$chain_error" && "$chain_error" != "null" ]]; then
                echo "Chain error: $chain_error"
            fi
            ;;
        backup)
            backup_location=$(echo "$response" | jq -r '.backup.location // empty' 2>/dev/null)
            backup_timestamp=$(echo "$response" | jq -r '.backup.timestamp // empty' 2>/dev/null)
            
            if [[ -n "$backup_location" ]]; then
                echo "Backup location: $backup_location"
            fi
            if [[ -n "$backup_timestamp" ]]; then
                echo "Backup timestamp: $backup_timestamp"
            fi
            
            # List backed up files
            files=$(echo "$response" | jq -r '.backup.files[]? | "\(.type): \(.path)"' 2>/dev/null)
            if [[ -n "$files" ]]; then
                echo "Backed up files:"
                echo "$files" | sed 's/^/  /'
            fi
            ;;
    esac
    
    # Show any output from the operation
    output=$(echo "$response" | jq -r '.output // empty' 2>/dev/null)
    if [[ -n "$output" && "$output" != "null" ]]; then
        echo
        echo "Operation output:"
        echo "$output"
    fi
    
    # Show any warnings
    warnings=$(echo "$response" | jq -r '.warnings // empty' 2>/dev/null)
    if [[ -n "$warnings" && "$warnings" != "null" ]]; then
        echo
        echo "⚠️  Warnings:"
        echo "$warnings"
    fi
    
else
    echo
    echo "❌ Operation '$OPERATION' failed!"
    error_msg=$(echo "$response" | jq -r '.error // "Unknown error"' 2>/dev/null)
    echo "Error: $error_msg"
    
    # Show additional details if available
    details=$(echo "$response" | jq -r '.details // empty' 2>/dev/null)
    if [[ -n "$details" && "$details" != "null" ]]; then
        echo "Details: $details"
    fi
    
    exit 1
fi