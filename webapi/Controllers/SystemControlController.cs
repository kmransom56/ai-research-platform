using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

namespace CopilotChat.WebApi.Controllers;

/// <summary>
/// Controller for system control and AI platform management
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class SystemControlController : ControllerBase
{
    private readonly ILogger<SystemControlController> _logger;

    public SystemControlController(ILogger<SystemControlController> logger)
    {
        _logger = logger;
    }

    /// <summary>
    /// Get system status
    /// </summary>
    [HttpGet("status")]
    public IActionResult GetSystemStatus()
    {
        try
        {
            var status = new
            {
                TailscaleIp = "100.123.10.72",
                Provider = Environment.GetEnvironmentVariable("CURRENT_AI_PROVIDER") ?? "openai",
                Services = new[]
                {
                    new { Name = "OpenWebUI", Status = "active", Url = "https://ubuntuaicodeserver-1.tail5137b4.ts.net" },
                    new { Name = "Chat Copilot", Status = "active", Url = "http://100.123.10.72:10500" },
                    new { Name = "Perplexica", Status = "active", Url = "http://100.123.10.72:3999/perplexica" },
                    new { Name = "SearchNG", Status = "active", Url = "http://100.123.10.72:4000" }
                },
                LastUpdate = DateTime.UtcNow
            };

            return Ok(status);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting system status");
            return StatusCode(500, new { error = "Failed to get system status" });
        }
    }

    /// <summary>
    /// Switch AI provider
    /// </summary>
    [HttpPost("switch-provider")]
    public async Task<IActionResult> SwitchProvider([FromBody] SwitchProviderRequest request)
    {
        try
        {
            var scriptPath = "/home/keith/chat-copilot/switch-ai-provider.sh";
            
            if (!System.IO.File.Exists(scriptPath))
            {
                return BadRequest(new { error = "Switch script not found" });
            }

            var result = await ExecuteCommandAsync("bash", $"{scriptPath} {request.Provider}");
            
            // Set environment variable for current provider
            Environment.SetEnvironmentVariable("CURRENT_AI_PROVIDER", request.Provider);
            
            return Ok(new { 
                success = true, 
                provider = request.Provider,
                output = result.Output,
                message = $"Successfully switched to {request.Provider.ToUpper()}"
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error switching AI provider to {Provider}", request.Provider);
            return StatusCode(500, new { error = $"Failed to switch to {request.Provider}" });
        }
    }

    /// <summary>
    /// Execute Docker commands
    /// </summary>
    [HttpPost("docker")]
    public async Task<IActionResult> ExecuteDockerCommand([FromBody] DockerCommandRequest request)
    {
        try
        {
            string command = request.Action switch
            {
                "status" => "docker ps --format 'table {{.Names}}\\t{{.Ports}}\\t{{.Status}}'",
                "start-all" => "docker start perplexica-app-1 perplexica-searxng-1 fortinet-manager_frontend_1 fortinet-manager_backend_1 port-scanner-tailscale",
                "stop-all" => "docker stop perplexica-app-1 perplexica-searxng-1 fortinet-manager_frontend_1 fortinet-manager_backend_1 port-scanner-tailscale",
                "restart" => "docker restart perplexica-app-1 perplexica-searxng-1 fortinet-manager_frontend_1 fortinet-manager_backend_1",
                _ => throw new ArgumentException($"Unknown docker action: {request.Action}")
            };

            var result = await ExecuteCommandAsync("bash", $"-c \"{command}\"");
            
            return Ok(new { 
                success = true, 
                action = request.Action,
                output = result.Output
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing Docker command {Action}", request.Action);
            return StatusCode(500, new { error = $"Failed to execute Docker command: {request.Action}" });
        }
    }

    /// <summary>
    /// Test service connectivity
    /// </summary>
    [HttpPost("test-services")]
    public async Task<IActionResult> TestServices()
    {
        try
        {
            var services = new[]
            {
                new { Name = "OpenWebUI", Url = "https://ubuntuaicodeserver-1.tail5137b4.ts.net" },
                new { Name = "Chat Copilot", Url = "http://100.123.10.72:10500" },
                new { Name = "Perplexica", Url = "http://100.123.10.72:3999/perplexica" },
                new { Name = "SearchNG", Url = "http://100.123.10.72:4000" },
                new { Name = "Health Check", Url = "https://100.123.10.72:40443/healthz" }
            };

            var results = new List<object>();
            
            using var httpClient = new HttpClient();
            httpClient.Timeout = TimeSpan.FromSeconds(10);

            foreach (var service in services)
            {
                try
                {
                    var response = await httpClient.GetAsync(service.Url);
                    results.Add(new
                    {
                        service.Name,
                        service.Url,
                        Status = response.IsSuccessStatusCode ? "accessible" : "error",
                        StatusCode = (int)response.StatusCode
                    });
                }
                catch (Exception ex)
                {
                    results.Add(new
                    {
                        service.Name,
                        service.Url,
                        Status = "error",
                        Error = ex.Message
                    });
                }
            }

            return Ok(new { success = true, services = results });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error testing services");
            return StatusCode(500, new { error = "Failed to test services" });
        }
    }

    /// <summary>
    /// Get system logs
    /// </summary>
    [HttpGet("logs")]
    public async Task<IActionResult> GetSystemLogs([FromQuery] int lines = 50)
    {
        try
        {
            var logCommands = new[]
            {
                "journalctl --no-pager -n " + lines,
                "docker logs perplexica-app-1 --tail " + lines + " 2>&1 || echo 'Perplexica logs not available'",
                "docker logs fortinet-manager_frontend_1 --tail " + lines + " 2>&1 || echo 'Fortinet logs not available'"
            };

            var logs = new List<object>();

            foreach (var cmd in logCommands)
            {
                try
                {
                    var result = await ExecuteCommandAsync("bash", $"-c \"{cmd}\"");
                    logs.Add(new { Command = cmd, Output = result.Output });
                }
                catch (Exception ex)
                {
                    logs.Add(new { Command = cmd, Error = ex.Message });
                }
            }

            return Ok(new { success = true, logs });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting system logs");
            return StatusCode(500, new { error = "Failed to get system logs" });
        }
    }

    /// <summary>
    /// Execute backup
    /// </summary>
    [HttpPost("backup")]
    public async Task<IActionResult> CreateBackup()
    {
        try
        {
            var backupDir = "/home/keith/backups";
            var timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
            var backupName = $"ai-platform-backup-{timestamp}";
            
            var commands = new[]
            {
                $"mkdir -p {backupDir}",
                $"cd /home/keith/chat-copilot && tar -czf {backupDir}/{backupName}.tar.gz --exclude=node_modules --exclude=bin --exclude=obj .",
                $"docker ps > {backupDir}/{backupName}-docker-status.txt",
                $"cp ~/.bashrc {backupDir}/{backupName}-bashrc-backup.txt"
            };

            foreach (var cmd in commands)
            {
                await ExecuteCommandAsync("bash", $"-c \"{cmd}\"");
            }

            return Ok(new { 
                success = true, 
                backupName,
                location = $"{backupDir}/{backupName}.tar.gz",
                timestamp
            });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating backup");
            return StatusCode(500, new { error = "Failed to create backup" });
        }
    }

    private async Task<(string Output, int ExitCode)> ExecuteCommandAsync(string command, string arguments)
    {
        using var process = new Process
        {
            StartInfo = new ProcessStartInfo
            {
                FileName = command,
                Arguments = arguments,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            }
        };

        process.Start();
        
        var output = await process.StandardOutput.ReadToEndAsync();
        var error = await process.StandardError.ReadToEndAsync();
        
        await process.WaitForExitAsync();
        
        var result = !string.IsNullOrEmpty(error) ? $"{output}\n{error}" : output;
        return (result, process.ExitCode);
    }
}

public class SwitchProviderRequest
{
    public string Provider { get; set; } = string.Empty;
}

public class DockerCommandRequest
{
    public string Action { get; set; } = string.Empty;
}