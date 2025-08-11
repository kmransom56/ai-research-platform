# 🌐🔒 Chat Copilot Platform - DNS and SSL Setup Guide

## 🚀 **Complete Professional DNS and SSL Configuration**

This guide will transform your Chat Copilot platform into an enterprise-grade secure environment with:
- **Network-wide DNS resolution** via unbound server
- **SSL certificates** for all services
- **Secure HTTPS access** to all Chat Copilot services
- **Professional security configuration**

---

## 📋 **Prerequisites**

### **Server Configuration:**
- **DNS/Cert Server**: `aicodeclient` (192.168.0.253) - user: `keransom`
- **Source Server**: `ubuntuaicodeserver` (192.168.0.1) - user: `keith`
- **Backup Server**: `ubuntuaicodeserver-2` (192.168.0.5) - user: `keith-ransom`

### **Required Access:**
- SSH access to all servers
- Sudo privileges on all servers
- Network access between all servers

---

## 🔧 **Step 1: Set Up SSH Access to DNS Server**

### **Generate SSH Key (if not exists):**
```bash
# Generate SSH key for secure connections
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -C "chatcopilot-platform"

# Display public key
cat ~/.ssh/id_rsa.pub
```

### **Configure DNS Server SSH Access:**
```bash
# Connect to DNS server (will require password)
ssh keransom@192.168.0.253

# On DNS server, set up SSH key access:
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add your public key (copy from above)
echo 'YOUR_PUBLIC_KEY_HERE' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Exit DNS server
exit
```

### **Test SSH Key Access:**
```bash
# Should connect without password
ssh aicodeclient "echo 'SSH key access working'"
```

---

## 🚀 **Step 2: Run Automated DNS and SSL Setup**

### **Execute Setup Script:**
```bash
# Run the comprehensive setup
./setup-dns-ssl.sh
```

### **What the Script Does:**
1. **Configures Unbound DNS** on aicodeclient
2. **Generates SSL Certificate Authority**
3. **Creates SSL certificates** for all servers
4. **Distributes certificates** to appropriate servers
5. **Configures Nginx with SSL** on both Chat Copilot servers
6. **Updates network DNS** to use unbound server
7. **Tests complete setup**

---

## 🌐 **Step 3: Configure Network DNS (Optional)**

### **Update Router/DHCP Settings:**
```bash
# Configure your router to use aicodeclient as DNS server
# Primary DNS: 192.168.0.253
# This provides network-wide hostname resolution
```

### **Manual DNS Configuration:**
```bash
# On each device, set DNS to:
# Primary DNS: 192.168.0.253
# Secondary DNS: 8.8.8.8 (fallback)
```

---

## 🔒 **Step 4: Verify SSL Setup**

### **Test HTTPS Access:**
```bash
# Test secure connections
curl -k https://ubuntuaicodeserver
curl -k https://ubuntuaicodeserver-2

# Test DNS resolution
nslookup ubuntuaicodeserver 192.168.0.253
nslookup ubuntuaicodeserver-2 192.168.0.253
```

### **Browser Access:**
- **Source Server**: https://ubuntuaicodeserver
- **Backup Server**: https://ubuntuaicodeserver-2
- **AutoGen Studio**: https://ubuntuaicodeserver/autogen/
- **OpenWebUI**: https://ubuntuaicodeserver/openwebui/
- **VS Code Web**: https://ubuntuaicodeserver/vscode/

---

## 🎯 **Expected Results**

### **✅ DNS Resolution:**
- All hostnames resolve via unbound DNS server
- Network-wide hostname resolution available
- Proper forward and reverse DNS lookup

### **✅ SSL Security:**
- All services accessible via HTTPS
- Valid SSL certificates for all hostnames
- Automatic HTTP to HTTPS redirects
- Security headers configured

### **✅ Professional Setup:**
- Enterprise-grade DNS and SSL configuration
- Secure access to all Chat Copilot services
- Professional certificate management
- Network-wide security implementation

---

## 🛠️ **Manual Configuration (If Needed)**

### **Unbound DNS Configuration:**
```bash
# Connect to DNS server
ssh aicodeclient

# Edit unbound configuration
sudo nano /etc/unbound/unbound.conf.d/chatcopilot.conf

# Add local zones:
server:
    local-zone: "local." static
    local-data: "ubuntuaicodeserver.local. IN A 192.168.0.1"
    local-data: "ubuntuaicodeserver-2.local. IN A 192.168.0.5"
    local-data: "aicodeclient.local. IN A 192.168.0.253"

# Restart unbound
sudo systemctl restart unbound
```

### **SSL Certificate Generation:**
```bash
# Generate CA certificate
openssl genrsa -out ca-key.pem 4096
openssl req -new -x509 -days 3650 -key ca-key.pem -out ca-cert.pem

# Generate server certificates
openssl genrsa -out server-key.pem 4096
openssl req -new -key server-key.pem -out server-csr.pem
openssl x509 -req -days 365 -in server-csr.pem -CA ca-cert.pem -CAkey ca-key.pem -out server-cert.pem
```

### **Nginx SSL Configuration:**
```bash
# Configure SSL in nginx
sudo nano /etc/nginx/sites-available/chatcopilot-ssl

server {
    listen 443 ssl http2;
    server_name ubuntuaicodeserver;
    
    ssl_certificate /etc/ssl/chatcopilot/ubuntuaicodeserver-cert.pem;
    ssl_certificate_key /etc/ssl/chatcopilot/ubuntuaicodeserver-key.pem;
    
    # Proxy configuration for Chat Copilot services
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable and restart nginx
sudo ln -sf /etc/nginx/sites-available/chatcopilot-ssl /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## 🔍 **Troubleshooting**

### **DNS Issues:**
```bash
# Check unbound status
ssh aicodeclient "sudo systemctl status unbound"

# Test DNS resolution
nslookup ubuntuaicodeserver 192.168.0.253

# Check unbound logs
ssh aicodeclient "sudo journalctl -u unbound -f"
```

### **SSL Issues:**
```bash
# Check nginx status
ssh ubuntuaicodeserver "sudo systemctl status nginx"

# Test SSL certificate
openssl s_client -connect ubuntuaicodeserver:443 -servername ubuntuaicodeserver

# Check nginx logs
ssh ubuntuaicodeserver "sudo tail -f /var/log/nginx/error.log"
```

### **Certificate Issues:**
```bash
# Verify certificate
openssl x509 -in /etc/ssl/chatcopilot/ubuntuaicodeserver-cert.pem -text -noout

# Check certificate chain
openssl verify -CAfile ca-cert.pem ubuntuaicodeserver-cert.pem
```

---

## 🎉 **Success Indicators**

### **✅ DNS Working:**
- `nslookup ubuntuaicodeserver 192.168.0.253` returns 192.168.0.1
- `ping ubuntuaicodeserver` resolves correctly
- Network devices can resolve hostnames

### **✅ SSL Working:**
- `https://ubuntuaicodeserver` loads without certificate errors
- Browser shows secure connection (lock icon)
- All Chat Copilot services accessible via HTTPS

### **✅ Complete Setup:**
- Professional DNS resolution network-wide
- Secure HTTPS access to all services
- Enterprise-grade security configuration
- Certificate-based authentication working

---

## 🚀 **Next Steps After Setup**

### **1. Update Bookmarks:**
```bash
# Update all bookmarks to use HTTPS
https://ubuntuaicodeserver/autogen/
https://ubuntuaicodeserver/openwebui/
https://ubuntuaicodeserver-2/
```

### **2. Configure Certificate Trust:**
```bash
# Install CA certificate on client devices for trusted connections
# Copy ca-cert.pem to client devices and install as trusted CA
```

### **3. Monitor and Maintain:**
```bash
# Set up certificate renewal (certificates expire in 1 year)
# Monitor DNS server performance
# Regular security updates
```

---

**Your Chat Copilot platform will have enterprise-grade DNS and SSL security! 🌐🔒🚀**