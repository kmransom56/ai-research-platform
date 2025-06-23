#!/bin/bash

# Certificate Listing Script for CA Server Integration
# Uses the /api/certificate-operations endpoint

set -e

# Configuration
CA_SERVER="192.168.0.2"
CA_PORT="443"
API_ENDPOINT="/api/certificate-operations"

# Default values
USE_HTTP=false
OUTPUT_FORMAT="table"

# Usage function
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

List certificates from the CA server

Optional:
  -s, --server SERVER              CA server address (default: 192.168.0.2)
  --port PORT                      CA server port (default: 443)
  --http                           Use HTTP instead of HTTPS
  -f, --format FORMAT              Output format (table, json, csv) (default: table)
  -h, --help                       Show this help message

Examples:
  $0
  $0 --format json
  $0 --http --port 3000
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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
        -f|--format)
            OUTPUT_FORMAT="$2"
            shift 2
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

echo "Fetching certificates from CA server: $CA_URL"
echo

# Make the API request
response=$(curl -s -k -X GET "$CA_URL" \
    --max-time 30 \
    --connect-timeout 10)

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
    echo "It needs to be converted to App Router format or moved to pages/api/"
    echo
    echo "Available alternatives:"
    echo "1. Check certificates manually on the CA server"
    echo "2. Request the CA server administrator to fix the endpoint"
    echo "3. Generate certificates and check their status individually"
    echo
    echo "To fix this endpoint, the file needs to be converted from:"
    echo "  export default function handler(req, res) { ... }"
    echo "To App Router format:"
    echo "  export async function GET() { ... }"
    echo "  export async function POST() { ... }"
    exit 1
fi

# Check if the request was successful
success=$(echo "$response" | jq -r '.success // false' 2>/dev/null)

if [[ "$success" == "true" ]]; then
    certificates=$(echo "$response" | jq -r '.certificates // []' 2>/dev/null)
    summary=$(echo "$response" | jq -r '.summary // {}' 2>/dev/null)
    
    # Display summary
    total=$(echo "$summary" | jq -r '.total // 0' 2>/dev/null)
    valid=$(echo "$summary" | jq -r '.valid // 0' 2>/dev/null)
    expiring=$(echo "$summary" | jq -r '.expiring // 0' 2>/dev/null)
    expired=$(echo "$summary" | jq -r '.expired // 0' 2>/dev/null)
    
    echo "Certificate Summary:"
    echo "  Total: $total"
    echo "  Valid: $valid"
    echo "  Expiring (≤30 days): $expiring"
    echo "  Expired: $expired"
    echo
    
    # Output certificates based on format
    case "$OUTPUT_FORMAT" in
        json)
            echo "$certificates" | jq .
            ;;
        csv)
            echo "Name,Subject,Status,Days Until Expiry,Not After,Serial"
            echo "$certificates" | jq -r '.[] | [.name, .subject, .status, .daysUntilExpiry, .notAfter, .serial] | @csv'
            ;;
        table|*)
            if [[ "$total" -eq 0 ]]; then
                echo "No certificates found."
            else
                echo "Certificates:"
                printf "%-20s %-30s %-10s %-15s %-25s\n" "NAME" "SUBJECT" "STATUS" "DAYS TO EXPIRY" "EXPIRES"
                printf "%-20s %-30s %-10s %-15s %-25s\n" "----" "-------" "------" "--------------" "-------"
                
                echo "$certificates" | jq -r '.[] | [.name, (.subject // "N/A"), .status, .daysUntilExpiry, (.notAfter // "N/A")] | @tsv' | \
                while IFS=$'\t' read -r name subject status days expiry; do
                    # Truncate long subjects
                    if [[ ${#subject} -gt 30 ]]; then
                        subject="${subject:0:27}..."
                    fi
                    
                    # Color code status
                    case "$status" in
                        expired)
                            status_colored="\033[31m$status\033[0m"  # Red
                            ;;
                        expiring)
                            status_colored="\033[33m$status\033[0m"  # Yellow
                            ;;
                        valid)
                            status_colored="\033[32m$status\033[0m"  # Green
                            ;;
                        *)
                            status_colored="$status"
                            ;;
                    esac
                    
                    printf "%-20s %-30s %-18s %-15s %-25s\n" "$name" "$subject" "$status_colored" "$days" "$expiry"
                done
            fi
            ;;
    esac
    
else
    echo "❌ Failed to retrieve certificates!"
    error_msg=$(echo "$response" | jq -r '.error // "Unknown error"' 2>/dev/null)
    echo "Error: $error_msg"
    
    # Show raw response if JSON parsing failed
    if ! echo "$response" | jq . >/dev/null 2>&1; then
        echo
        echo "Raw response:"
        echo "$response"
    fi
    
    exit 1
fi