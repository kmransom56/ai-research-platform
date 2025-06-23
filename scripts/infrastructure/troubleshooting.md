# CA Server Integration Troubleshooting Guide

## Common Issues and Solutions

### 1. Connection Failures

#### Problem: "Failed to connect to CA server"
```
Error: Failed to connect to CA server at https://192.168.0.2:443/api/generate-cert
```

**Solutions**:
```bash
# Test basic connectivity
ping 192.168.0.2

# Test port availability
nc -zv 192.168.0.2 443
nc -zv 192.168.0.2 3000

# Try HTTP instead of HTTPS
./generate-certificate.sh -n test.com --http

# Check with curl directly
curl -k -v https://192.168.0.2/api/generate-cert
curl -v http://192.168.0.2:3000/api/generate-cert
```

#### Problem: SSL/TLS errors
```
curl: (35) OpenSSL/3.0.13: error:0A00010B:SSL routines::wrong version number
```

**Solution**: Use HTTP or fix SSL configuration
```bash
# Use HTTP instead
./generate-certificate.sh -n test.com --http --port 3000

# Or check nginx SSL configuration on CA server
```

### 2. API Endpoint Issues

#### Problem: "404 Not Found" or "Cannot GET"
```json
{"error": "Cannot GET /api/certificates/generate"}
```

**Solution**: Use correct endpoint
```bash
# Wrong (old endpoints)
curl https://192.168.0.2/api/certificates/generate
curl https://192.168.0.2/api/csr/submit

# Correct (working endpoints)
curl https://192.168.0.2/api/generate-cert
curl https://192.168.0.2/api/certificate-operations
```

#### Problem: Method not allowed
```json
{"error": "Method not allowed"}
```

**Solution**: Check HTTP method
```bash
# GET for documentation/listing
curl -X GET https://192.168.0.2/api/generate-cert

# POST for operations
curl -X POST https://192.168.0.2/api/generate-cert -H "Content-Type: application/json" -d '{"serverName":"test.com"}'
```

### 3. Certificate Generation Failures

#### Problem: Permission denied errors
```
mkdir: cannot create directory '/home': Permission denied
genrsa: Can't open "/path/to/key" for writing, Permission denied
```

**Root Cause**: CA server script permission issues

**Investigation**:
```bash
# Check CA server logs
ssh 192.168.0.2 'tail -f /opt/cert-manager/logs/*.log'

# Check certificate directory permissions
ssh 192.168.0.2 'ls -la /opt/ca/'

# Check running processes
ssh 192.168.0.2 'ps aux | grep next'
```

**Temporary Workarounds**:
1. Run certificate generation on CA server directly
2. Fix permissions on CA server
3. Use different certificate type that works

#### Problem: Script not found
```json
{"error": "Certificate generation script not found: generate_server_cert.sh"}
```

**Solution**: Check available certificate types
```bash
# Get available types
curl -k https://192.168.0.2/api/generate-cert | jq .availableTypes

# Try different certificate type
./generate-certificate.sh -n test.com -t direct
./generate-certificate.sh -n test.com -t temp
```

### 4. Missing Dependencies

#### Problem: "jq: command not found"
```bash
./generate-certificate.sh: line 123: jq: command not found
```

**Solution**: Install jq
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install jq

# RHEL/CentOS/Fedora
sudo yum install jq
# or
sudo dnf install jq

# macOS
brew install jq
```

#### Problem: "curl: command not found"
**Solution**: Install curl
```bash
# Ubuntu/Debian
sudo apt-get install curl

# RHEL/CentOS
sudo yum install curl
```

### 5. CA Server-Side Issues

#### Problem: CA server not responding
**Check server status**:
```bash
# SSH to CA server
ssh 192.168.0.2

# Check Next.js process
ps aux | grep next
systemctl status cert-manager

# Check ports
netstat -tlnp | grep -E ":443|:3000"

# Check nginx
nginx -t
systemctl status nginx

# Restart services if needed
sudo systemctl restart cert-manager
sudo systemctl restart nginx
```

#### Problem: CA infrastructure not set up
```json
{"error": "CA infrastructure not found"}
```

**Solution**: Initialize CA on server
```bash
# SSH to CA server
ssh 192.168.0.2

# Check CA directory
ls -la /opt/ca/

# Run CA setup if needed
cd /opt/cert-manager
sudo ./scripts/setup_ca.sh
```

### 6. Script-Specific Issues

#### generate-certificate.sh

**Problem**: Required parameter missing
```
Error: Server name is required
```
**Solution**: Always provide `-n` parameter
```bash
./generate-certificate.sh -n example.com
```

**Problem**: Invalid certificate type
```json
{"error": "Unknown certificate type"}
```
**Solution**: Use valid types
```bash
# Valid types: server, https, nginx, web, fixed, temp, direct
./generate-certificate.sh -n test.com -t server
```

#### submit-csr.sh

**Problem**: Endpoint not implemented
```
❌ The /api/sign-csr endpoint is not yet implemented on the CA server.
```
**Solution**: 
1. Use `generate-certificate.sh` instead for new certificates
2. Request CA server admin to implement endpoint
3. Use web interface for manual CSR submission

#### list-certificates.sh

**Problem**: Empty certificate list
```
No certificates found.
```
**Investigation**:
```bash
# Check if certificates exist on server
ssh 192.168.0.2 'ls -la /opt/ca/intermediate/certs/*.crt'

# Check certificate directory configuration
ssh 192.168.0.2 'cat /opt/cert-manager/.env | grep CERT_DIR'
```

### 7. Network and Firewall Issues

#### Problem: Connection timeout
```
curl: (28) Connection timed out after 30000 milliseconds
```

**Solutions**:
```bash
# Check firewall on CA server
ssh 192.168.0.2 'sudo ufw status'
ssh 192.168.0.2 'sudo iptables -L'

# Check routing
traceroute 192.168.0.2

# Test from CA server to your system
ssh 192.168.0.2 'curl -v http://192.168.0.6:8080'
```

### 8. Authentication Issues (Future)

When authentication is implemented:

#### Problem: Unauthorized access
```json
{"error": "Unauthorized", "code": 401}
```

**Solutions**:
- Add API key header: `-H "X-API-Key: your-key"`
- Add authentication token: `-H "Authorization: Bearer token"`
- Update scripts with authentication parameters

### 9. Debugging Commands

#### Test CA server endpoints:
```bash
# Test all endpoints
for endpoint in "/api/generate-cert" "/api/certificate-operations" "/api/generate-https-cert"; do
  echo "Testing $endpoint"
  curl -k -s "https://192.168.0.2$endpoint" | head -c 100
  echo
done
```

#### Verbose script debugging:
```bash
# Run with debug output
bash -x ./generate-certificate.sh -n test.com

# Check script variables
./generate-certificate.sh -n test.com --help
```

#### Monitor CA server logs:
```bash
# Real-time log monitoring
ssh 192.168.0.2 'tail -f /var/log/nginx/access.log'
ssh 192.168.0.2 'tail -f /opt/cert-manager/.next/trace'
```

### 10. Emergency Procedures

#### Complete service restart:
```bash
ssh 192.168.0.2 '
sudo systemctl stop nginx
sudo systemctl stop cert-manager
sleep 5
sudo systemctl start cert-manager
sudo systemctl start nginx
systemctl status cert-manager nginx
'
```

#### Fallback manual certificate generation:
```bash
# Direct script execution on CA server
ssh 192.168.0.2 'cd /opt/cert-manager && sudo ./scripts/generate_server_cert.sh example.com'
```

#### Reset to working state:
```bash
# Backup current state
ssh 192.168.0.2 'sudo cp -r /opt/cert-manager /opt/cert-manager.backup'

# Restart with clean state
ssh 192.168.0.2 '
cd /opt/cert-manager
git status
git stash
npm run build
sudo systemctl restart cert-manager
'
```

## Getting Help

1. **Check CA server logs**: Always start with server-side logs
2. **Test with curl directly**: Eliminate script issues
3. **Verify network connectivity**: Basic ping and port checks
4. **Use minimal test cases**: Start with simple certificate generation
5. **Check server resources**: Ensure adequate disk space and memory

## Contact Information

- CA Server Admin: [Contact details]
- Network Admin: [Contact details]
- Documentation: This repository README.md