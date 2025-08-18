import React, { useState } from 'react';

interface ServiceStatus {
  name: string;
  status: 'active' | 'inactive' | 'unknown';
  url: string;
  description: string;
}

const ControlPanel: React.FC = () => {
  const [services] = useState<ServiceStatus[]>([
    { name: 'OpenWebUI', status: 'active', url: 'https://ubuntuaicodeserver-1.tail5137b4.ts.net', description: 'Primary AI Interface' },
    { name: 'Chat Copilot', status: 'active', url: 'http://100.123.10.72:11000', description: 'Microsoft Semantic Kernel' },
    { name: 'Perplexica', status: 'active', url: 'http://100.123.10.72:3999/perplexica', description: 'AI Search with Internet' },
    { name: 'SearchNG', status: 'active', url: 'http://100.123.10.72:4000', description: 'Privacy-focused Search' },
  ]);

  const [logs, setLogs] = useState<string[]>([
    '🤖 AI Research Platform Control Panel Ready',
    '📊 Status: All systems operational',
    '🔗 Tailscale IP: 100.123.10.72',
  ]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, `[${timestamp}] ${message}`]);
  };

  const openService = (url: string) => {
    window.open(url, '_blank');
    addLog(`🚀 Opening service: ${url}`);
  };

  return (
    <div style={{ padding: '20px', backgroundColor: '#f5f5f5', minHeight: '100vh' }}>
      <h1 style={{ textAlign: 'center', marginBottom: '30px' }}>
        🤖 AI Research Platform Control Panel
      </h1>
      
      <p style={{ textAlign: 'center', color: '#666', marginBottom: '40px' }}>
        Tailscale Network: 100.123.10.72 | Provider: OPENAI
      </p>

      {/* Service Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '20px',
        marginBottom: '30px'
      }}>
        
        {/* AI Services */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
        }}>
          <h3>🤖 AI Services</h3>
          {services.map((service) => (
            <button
              key={service.name}
              onClick={() => openService(service.url)}
              style={{
                display: 'block',
                width: '100%',
                padding: '10px',
                margin: '5px 0',
                backgroundColor: '#0078d4',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              {service.name}
            </button>
          ))}
        </div>

        {/* Development Tools */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
        }}>
          <h3>💻 Development Tools</h3>
          <button
            onClick={() => openService('http://100.123.10.72:57081')}
            style={{
              display: 'block',
              width: '100%',
              padding: '10px',
              margin: '5px 0',
              backgroundColor: '#0078d4',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            VS Code Online
          </button>
          <button
            onClick={() => openService('http://100.123.10.72:11000/healthz')}
            style={{
              display: 'block',
              width: '100%',
              padding: '10px',
              margin: '5px 0',
              backgroundColor: '#0078d4',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Health Check
          </button>
        </div>

        {/* Network Management */}
        <div style={{ 
          backgroundColor: 'white', 
          padding: '20px', 
          borderRadius: '8px', 
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
        }}>
          <h3>🌐 Network Management</h3>
          <button
            onClick={() => openService('http://100.123.10.72:3001')}
            style={{
              display: 'block',
              width: '100%',
              padding: '10px',
              margin: '5px 0',
              backgroundColor: '#0078d4',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Fortinet Manager
          </button>
          <button
            onClick={() => openService('http://100.123.10.72:11082')}
            style={{
              display: 'block',
              width: '100%',
              padding: '10px',
              margin: '5px 0',
              backgroundColor: '#0078d4',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Nginx Gateway
          </button>
        </div>
      </div>

      {/* Logs Section */}
      <div style={{ 
        backgroundColor: '#1e1e1e', 
        color: '#00ff00', 
        padding: '20px', 
        borderRadius: '8px',
        fontFamily: 'monospace'
      }}>
        <h3 style={{ color: '#00ff00', marginBottom: '10px' }}>
          📋 System Logs
        </h3>
        <div style={{ maxHeight: '200px', overflow: 'auto' }}>
          {logs.slice(-10).map((log, index) => (
            <div key={index} style={{ fontSize: '0.9rem', marginBottom: '2px' }}>
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ControlPanel;