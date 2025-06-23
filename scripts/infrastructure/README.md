# CA Server Integration Scripts

Updated automation scripts for the Certificate Authority server at `192.168.0.2`. These scripts use the correct API endpoints identified on the Next.js-based CA server.

## Quick Start

Copy these scripts to your AI Research Platform at `192.168.0.6:/home/keith/chat-copilot/scripts/infrastructure/`

## Scripts Overview

### 1. `generate-certificate.sh` - Primary Certificate Generation
**Purpose**: Generate new certificates using the CA server's `/api/generate-cert` endpoint.

**Usage**:
```bash
./generate-certificate.sh -n example.com
./generate-certificate.sh -n web.example.com -i 192.168.1.100 -t nginx
./generate-certificate.sh -n api.example.com -t https -d 730
```

**Parameters**:
- `-n, --server-name` (required): Domain or server name
- `-i, --server-ip`: IP address for SAN
- `-t, --type`: Certificate type (server, https, nginx, web, fixed, temp, direct)
- `-d, --days`: Validity period (default: 365)
- `-p, --password`: CA password if required
- `--http`: Use HTTP instead of HTTPS

### 2. `submit-csr.sh` - CSR Submission (Future)
**Purpose**: Submit Certificate Signing Requests to the CA server.

**Status**: ⚠️ The `/api/sign-csr` endpoint is not yet implemented on the CA server.

**Usage** (when implemented):
```bash
./submit-csr.sh -f my-server.csr
./submit-csr.sh -f web.csr -c "Intermediate CA" -d 730
```

### 3. `list-certificates.sh` - Certificate Listing
**Purpose**: List all certificates from the CA server with status information.

**Usage**:
```bash
./list-certificates.sh
./list-certificates.sh --format json
./list-certificates.sh --http --port 3000
```

### 4. `certificate-operations.sh` - Certificate Operations
**Purpose**: Perform operations on existing certificates.

**Usage**:
```bash
./certificate-operations.sh -o validate -c example.com
./certificate-operations.sh -o export-browser -c web-server
./certificate-operations.sh -o backup -c api.example.com
```

**Operations**:
- `validate`: Validate certificate and chain
- `export-browser`: Export for browser import
- `trust`: Trust certificate in system
- `backup`: Backup certificate files

## CA Server API Endpoints

### Working Endpoints ✅

1. **`GET/POST /api/generate-cert`**
   - Generate new certificates
   - Supports multiple certificate types
   - Returns certificate paths and details

2. **`GET/POST /api/certificate-operations`**
   - List certificates (GET)
   - Perform operations on certificates (POST)

3. **`POST /api/generate-https-cert`**
   - Legacy HTTPS certificate generation
   - Pages Router style endpoint

### Missing Endpoints ❌

1. **`POST /api/sign-csr`**
   - CSR submission and signing
   - Referenced by frontend but not implemented
   - Needs to be created for full automation

### Failed Original Endpoints ❌

Your original scripts were trying these non-existent endpoints:
- `/api/certificates/generate` → Use `/api/generate-cert`
- `/api/csr/submit` → Use `/api/sign-csr` (when implemented)
- `/generate` → Use `/api/generate-cert`
- `/certificates` → Use `/api/certificate-operations`

## Network Configuration

- **CA Server**: `192.168.0.2`
- **HTTPS Port**: `443` (with nginx proxy)
- **HTTP Port**: `3000` (direct Next.js)
- **Application**: Next.js v15.3.2 with App Router

## Examples

### Generate a standard server certificate:
```bash
./generate-certificate.sh -n myapp.example.com
```

### Generate an nginx certificate with IP SAN:
```bash
./generate-certificate.sh -n web.example.com -i 192.168.1.100 -t nginx -d 730
```

### List all certificates:
```bash
./list-certificates.sh
```

### Validate a certificate:
```bash
./certificate-operations.sh -o validate -c myapp.example.com
```

### Backup a certificate:
```bash
./certificate-operations.sh -o backup -c myapp.example.com
```

## Integration with Your Deployment Scripts

Replace your existing certificate automation calls:

**Old (failing)**:
```bash
curl -X POST https://192.168.0.2/api/certificates/generate
curl -X POST https://192.168.0.2/api/csr/submit
```

**New (working)**:
```bash
./generate-certificate.sh -n "$DOMAIN_NAME" -t nginx
./list-certificates.sh --format json
```

## Server Status Verification

CA server is operational:
- ✅ Next.js application running (PID: 1714318)
- ✅ Port 3000 active (next-server v15.3.2)
- ✅ HTTPS proxy on port 443
- ✅ API endpoints responding
- ⚠️ Permission issues with certificate generation scripts (needs investigation)

## Troubleshooting

### Connection Issues
```bash
# Test basic connectivity
curl -k https://192.168.0.2/api/generate-cert

# Test with HTTP if HTTPS fails
curl http://192.168.0.2:3000/api/generate-cert
```

### Permission Issues
The CA server has permission issues with certificate generation. If certificates fail to generate:

1. Check the CA server logs
2. Verify `/opt/ca` directory permissions
3. Ensure the `certgen` user has proper access
4. Consider running certificate generation with appropriate privileges

### Missing CSR Endpoint
To implement the missing `/api/sign-csr` endpoint, create:

**File**: `/opt/cert-manager/src/app/api/sign-csr/route.js`

```javascript
import { NextRequest, NextResponse } from 'next/server';
import formidable from 'formidable';
import fs from 'fs';
import { exec } from 'child_process';

export async function POST(request) {
  // Implementation for CSR signing
  // Parse multipart form data
  // Extract CSR file and parameters
  // Sign CSR using CA scripts
  // Return signed certificate
}
```

## Dependencies

Scripts require:
- `curl` - HTTP client
- `jq` - JSON processing
- `bash` - Shell environment

Install missing dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install curl jq

# RHEL/CentOS
sudo yum install curl jq
```

## Security Notes

- Scripts use `-k` flag to skip SSL verification (self-signed CA)
- No authentication is currently implemented on CA server
- Security relies on network isolation (internal 192.168.0.x network)
- Consider implementing API authentication for production use

## Migration Instructions

1. **Copy scripts to your platform**:
   ```bash
   scp -r ~/updated-automation-scripts/* 192.168.0.6:/home/keith/chat-copilot/scripts/infrastructure/
   ```

2. **Update your deployment scripts**:
   - Replace old API calls with new script calls
   - Update domain names and certificate types as needed
   - Test with development certificates first

3. **Verify operation**:
   ```bash
   ./list-certificates.sh
   ./generate-certificate.sh -n test.example.com
   ```

This integration should resolve your certificate automation issues and provide reliable programmatic access to the CA server.