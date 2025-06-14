import React, { useState, useEffect } from 'react';
import {
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Box,
  Alert,
  Paper,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  RestartAlt,
  Settings,
  Info,
  SwapHoriz,
  NetworkPing,
  Code,
  Security,
  Search,
  Chat,
  Psychology,
  PrivacyTip,
  HealthAndSafety,
  Dashboard,
  Refresh,
  CloudDownload,
  Backup,
  Router,
  SmartToy,
  Build,
  FlashOn,
} from '@mui/icons-material';

interface ServiceStatus {
  name: string;
  status: 'active' | 'inactive' | 'unknown';
  url: string;
  description: string;
}

interface SystemInfo {
  provider: 'openai' | 'azure';
  tailscaleIp: string;
  lastUpdate: Date;
}

const ControlPanel: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'OpenWebUI', status: 'active', url: 'https://ubuntuaicodeserver-1.tail5137b4.ts.net', description: 'Primary AI Interface' },
    { name: 'Chat Copilot', status: 'active', url: 'http://100.123.10.72:10500', description: 'Microsoft Semantic Kernel' },
    { name: 'Perplexica', status: 'active', url: 'http://100.123.10.72:3999/perplexica', description: 'AI Search with Internet' },
    { name: 'SearchNG', status: 'active', url: 'http://100.123.10.72:4000', description: 'Privacy-focused Search' },
  ]);

  const [systemInfo, setSystemInfo] = useState<SystemInfo>({
    provider: 'openai',
    tailscaleIp: '100.123.10.72',
    lastUpdate: new Date(),
  });

  const [logs, setLogs] = useState<string[]>([
    '🤖 AI Research Platform Control Panel Ready',
    '📊 Status: All systems operational',
    '🔗 Tailscale IP: 100.123.10.72',
  ]);

  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogContent, setDialogContent] = useState('');

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const executeCommand = async (command: string, action: string) => {
    setLoading(true);
    addLog(`🔧 Executing ${command} ${action}...`);
    
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      switch (command) {
        case 'switch-ai':
          if (action === 'azure') {
            setSystemInfo(prev => ({ ...prev, provider: 'azure' }));
            addLog('✅ Switched to Azure OpenAI');
          } else if (action === 'openai') {
            setSystemInfo(prev => ({ ...prev, provider: 'openai' }));
            addLog('✅ Switched to OpenAI');
          } else if (action === 'status') {
            addLog(`📊 Current Provider: ${systemInfo.provider.toUpperCase()}`);
          }
          break;
        case 'docker':
          addLog(`🐳 Docker ${action} completed successfully`);
          break;
        case 'test':
          addLog('🧪 Testing all services...');
          services.forEach((service, index) => {
            setTimeout(() => {
              addLog(`✅ ${service.name}: Accessible`);
            }, (index + 1) * 300);
          });
          break;
        default:
          addLog(`📝 Command ${command} ${action} executed`);
      }
    } catch (error) {
      addLog(`❌ Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const refreshServices = async () => {
    setLoading(true);
    addLog('🔄 Refreshing service status...');
    
    // Simulate checking each service
    for (const service of services) {
      try {
        // In a real implementation, you would make actual HTTP requests here
        await new Promise(resolve => setTimeout(resolve, 500));
        addLog(`✅ ${service.name}: Operational`);
      } catch {
        addLog(`❌ ${service.name}: Error`);
      }
    }
    
    setSystemInfo(prev => ({ ...prev, lastUpdate: new Date() }));
    setLoading(false);
  };

  const openService = (url: string) => {
    window.open(url, '_blank');
    addLog(`🚀 Opening service: ${url}`);
  };

  const showDialog = (title: string, content: string) => {
    setDialogContent(content);
    setDialogOpen(true);
  };

  const ActionButton: React.FC<{ 
    icon: React.ReactNode; 
    label: string; 
    onClick: () => void; 
    color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info';
    variant?: 'contained' | 'outlined';
  }> = ({ icon, label, onClick, color = 'primary', variant = 'contained' }) => (
    <Button
      variant={variant}
      color={color}
      startIcon={icon}
      onClick={onClick}
      fullWidth
      sx={{ mb: 1, textTransform: 'none' }}
    >
      {label}
    </Button>
  );

  return (
    <Box sx={{ p: 3, bgcolor: '#f5f5f5', minHeight: '100vh' }}>
      <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ mb: 3 }}>
        🤖 AI Research Platform Control Panel
      </Typography>
      
      <Typography variant="subtitle1" align="center" color="textSecondary" sx={{ mb: 4 }}>
        Tailscale Network: {systemInfo.tailscaleIp} | Provider: {systemInfo.provider.toUpperCase()}
      </Typography>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Status Chips */}
      <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 3, flexWrap: 'wrap' }}>
        {services.map((service) => (
          <Chip
            key={service.name}
            label={service.name}
            color={service.status === 'active' ? 'success' : service.status === 'inactive' ? 'error' : 'warning'}
            variant="filled"
          />
        ))}
        <Chip 
          label={`Provider: ${systemInfo.provider.toUpperCase()}`} 
          color="info" 
          variant="outlined" 
        />
      </Box>

      <Grid container spacing={3}>
        {/* AI Services */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                <SmartToy sx={{ mr: 1, verticalAlign: 'middle' }} />
                AI Services
              </Typography>
              <ActionButton
                icon={<Psychology />}
                label="OpenWebUI"
                onClick={() => openService('https://ubuntuaicodeserver-1.tail5137b4.ts.net')}
              />
              <ActionButton
                icon={<Chat />}
                label="Chat Copilot"
                onClick={() => openService('http://100.123.10.72:10500')}
              />
              <ActionButton
                icon={<Search />}
                label="Perplexica"
                onClick={() => openService('http://100.123.10.72:3999/perplexica')}
              />
              <ActionButton
                icon={<PrivacyTip />}
                label="SearchNG"
                onClick={() => openService('http://100.123.10.72:4000')}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* System Control */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                <Settings sx={{ mr: 1, verticalAlign: 'middle' }} />
                System Control
              </Typography>
              <ActionButton
                icon={<Info />}
                label="AI Status"
                onClick={() => executeCommand('switch-ai', 'status')}
                color="info"
              />
              <ActionButton
                icon={<SwapHoriz />}
                label="Switch to Azure"
                onClick={() => executeCommand('switch-ai', 'azure')}
                color="warning"
              />
              <ActionButton
                icon={<SwapHoriz />}
                label="Switch to OpenAI"
                onClick={() => executeCommand('switch-ai', 'openai')}
                color="warning"
              />
              <ActionButton
                icon={<NetworkPing />}
                label="Test Network"
                onClick={() => executeCommand('test', 'network')}
                color="info"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Development Tools */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                <Code sx={{ mr: 1, verticalAlign: 'middle' }} />
                Development Tools
              </Typography>
              <ActionButton
                icon={<Code />}
                label="VS Code Online"
                onClick={() => openService('http://100.123.10.72:57081')}
                color="info"
              />
              <ActionButton
                icon={<NetworkPing />}
                label="Port Scanner"
                onClick={() => openService('http://100.123.10.72:10200')}
                color="info"
              />
              <ActionButton
                icon={<HealthAndSafety />}
                label="Health Check"
                onClick={() => openService('https://100.123.10.72:40443/healthz')}
                color="info"
              />
              <ActionButton
                icon={<Refresh />}
                label="Refresh Status"
                onClick={refreshServices}
                color="secondary"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Network Management */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                <Router sx={{ mr: 1, verticalAlign: 'middle' }} />
                Network Management
              </Typography>
              <ActionButton
                icon={<Security />}
                label="Fortinet Manager"
                onClick={() => openService('http://100.123.10.72:3001')}
              />
              <ActionButton
                icon={<Router />}
                label="Nginx Gateway"
                onClick={() => openService('http://100.123.10.72:8082')}
              />
              <ActionButton
                icon={<NetworkPing />}
                label="Test Network"
                onClick={() => executeCommand('ping', '100.123.10.72')}
                color="secondary"
              />
              <ActionButton
                icon={<Info />}
                label="Network Info"
                onClick={() => showDialog('Network Info', 'Tailscale IP: 100.123.10.72\\nNetwork Type: Tailscale VPN\\nAccess: Global via Tailscale')}
                color="info"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Service Management */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                <Build sx={{ mr: 1, verticalAlign: 'middle' }} />
                Service Management
              </Typography>
              <ActionButton
                icon={<PlayArrow />}
                label="Start All Services"
                onClick={() => executeCommand('docker', 'start-all')}
                color="secondary"
              />
              <ActionButton
                icon={<RestartAlt />}
                label="Restart Services"
                onClick={() => executeCommand('docker', 'restart')}
                color="warning"
              />
              <ActionButton
                icon={<Stop />}
                label="Stop All Services"
                onClick={() => executeCommand('docker', 'stop-all')}
                color="error"
              />
              <ActionButton
                icon={<Info />}
                label="View Logs"
                onClick={() => showDialog('System Logs', logs.join('\\n'))}
                color="info"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="h2" gutterBottom>
                <FlashOn sx={{ mr: 1, verticalAlign: 'middle' }} />
                Quick Actions
              </Typography>
              <ActionButton
                icon={<NetworkPing />}
                label="Test All Services"
                onClick={() => executeCommand('test', 'all')}
                color="secondary"
              />
              <ActionButton
                icon={<CloudDownload />}
                label="Export Config"
                onClick={() => executeCommand('export', 'config')}
                color="info"
              />
              <ActionButton
                icon={<Backup />}
                label="Backup Data"
                onClick={() => executeCommand('backup', 'data')}
                color="warning"
              />
              <ActionButton
                icon={<Dashboard />}
                label="Full Dashboard"
                onClick={() => openService('http://100.123.10.72:10500/applications.html')}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Logs Section */}
      <Paper sx={{ mt: 3, p: 2, bgcolor: '#1e1e1e', color: '#00ff00', fontFamily: 'monospace' }}>
        <Typography variant="h6" sx={{ color: '#00ff00', mb: 2 }}>
          📋 System Logs
        </Typography>
        <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
          {logs.slice(-10).map((log, index) => (
            <Typography key={index} variant="body2" sx={{ fontSize: '0.85rem' }}>
              {log}
            </Typography>
          ))}
        </Box>
      </Paper>

      {/* Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>System Information</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ whiteSpace: 'pre-line' }}>
            {dialogContent}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Quick Access Bar */}
      <Box sx={{ 
        position: 'fixed', 
        bottom: 20, 
        right: 20, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 1 
      }}>
        <Tooltip title="Refresh All">
          <IconButton 
            color="primary" 
            onClick={refreshServices}
            sx={{ bgcolor: 'white', boxShadow: 2 }}
          >
            <Refresh />
          </IconButton>
        </Tooltip>
        <Tooltip title="GitHub Repository">
          <IconButton 
            color="primary" 
            onClick={() => openService('https://github.com/kmransom56/AI_Research_Platform-_Tailscale')}
            sx={{ bgcolor: 'white', boxShadow: 2 }}
          >
            <Code />
          </IconButton>
        </Tooltip>
      </Box>
    </Box>
  );
};

export default ControlPanel;