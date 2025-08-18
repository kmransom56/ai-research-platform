using System.Net.Http.Json;
using System.Text.Json;
using CopilotChat.Shared.AI;

namespace CopilotChat.WebApi.Services;

public class OllamaProvider : ILlmProvider
{
    private readonly HttpClient _http;
    private readonly IConfiguration _config;
    private readonly string _model;

    public OllamaProvider(IConfiguration config, IHttpClientFactory factory)
    {
        _config = config;
        _http = factory.CreateClient();
        var baseUrl = config["Llm:Ollama:BaseUrl"] ?? "http://ollama:11434";
        _http.BaseAddress = new Uri(baseUrl);
        _model = config["Llm:Ollama:Model"] ?? "phi3";
    }

    public async Task<string> ChatAsync(string prompt, CancellationToken cancellationToken = default)
    {
        var payload = new
        {
            model = _model,
            prompt
        };
        var resp = await _http.PostAsJsonAsync("/api/generate", payload, cancellationToken);
        resp.EnsureSuccessStatusCode();
        var json = await resp.Content.ReadFromJsonAsync<JsonElement>(cancellationToken: cancellationToken);
        return json.GetProperty("response").GetString() ?? string.Empty;
    }

    public async Task<float[]> EmbedAsync(string text, CancellationToken cancellationToken = default)
    {
        var payload = new { model = _model, prompt = text }; // Ollama's embeddings API still evolving
        var resp = await _http.PostAsJsonAsync("/api/embeddings", payload, cancellationToken);
        resp.EnsureSuccessStatusCode();
        var json = await resp.Content.ReadFromJsonAsync<JsonElement>(cancellationToken: cancellationToken);
        return json.GetProperty("embedding").EnumerateArray().Select(e => e.GetSingle()).ToArray();
    }
} 