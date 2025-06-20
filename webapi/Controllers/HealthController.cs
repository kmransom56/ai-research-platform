using Microsoft.AspNetCore.Mvc;
using System.Net.Http;
using System.Threading.Tasks;
using System;
using System.Collections.Generic;
using System.Linq;

namespace CopilotChat.WebApi.Controllers
{
    [ApiController]
    // Summary of downstream service health; keep distinct from built-in /healthz endpoint.
    [Route("healthz/services")]
    public class HealthController : ControllerBase
    {
        private static readonly HttpClient _http = new () { Timeout = TimeSpan.FromSeconds(5)};

        private record ServiceTarget(string Name, string Url);

        private readonly ServiceTarget[] _targets = new[]
        {
            new ServiceTarget("OpenWebUI", "http://localhost:8080/api/config"),
            new ServiceTarget("Perplexica", "http://localhost:11020/perplexica"),
            new ServiceTarget("SearXNG", "http://localhost:11021"),
            new ServiceTarget("Ollama", "http://localhost:11434/api/version")
        };

        [HttpGet]
        public async Task<IActionResult> GetSummary()
        {
            var healthResults = new List<object>();
            foreach (var t in _targets)
            {
                try
                {
                    var resp = await _http.GetAsync(t.Url);
                    healthResults.Add(new {
                        t.Name,
                        t.Url,
                        StatusCode = (int)resp.StatusCode,
                        Healthy = resp.IsSuccessStatusCode
                    });
                }
                catch(Exception ex)
                {
                    healthResults.Add(new {
                        t.Name,
                        t.Url,
                        Healthy = false,
                        Error = ex.Message
                    });
                }
            }

            var summary = new {
                Status = healthResults.All(h => (bool)h.GetType().GetProperty("Healthy")!.GetValue(h)!) ? "healthy" : "degraded",
                Timestamp = DateTime.UtcNow,
                TailscaleIp = Environment.GetEnvironmentVariable("TAILSCALE_IP") ?? "unknown",
                Services = healthResults
            };

            return Ok(summary);
        }
    }
} 