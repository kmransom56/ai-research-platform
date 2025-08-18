using CopilotChat.Shared.AI;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;

namespace CopilotChat.WebApi.Services;

public class OpenAiProvider : ILlmProvider
{
    private readonly HttpClient _http;
    private readonly string _model;

    public OpenAiProvider(IConfiguration config, IHttpClientFactory factory)
    {
        _http = factory.CreateClient();
        var baseUrl = config["Llm:OpenAI:BaseUrl"] ?? "https://api.openai.com/v1";
        _http.BaseAddress = new Uri(baseUrl);
        _http.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", config["Llm:OpenAI:ApiKey"]);
        _model = config["Llm:OpenAI:Model"] ?? "gpt-4o";
    }

    public async Task<string> ChatAsync(string prompt, CancellationToken cancellationToken = default)
    {
        var payload = new
        {
            model = _model,
            messages = new[] { new { role = "user", content = prompt } }
        };
        var resp = await _http.PostAsJsonAsync("/chat/completions", payload, cancellationToken);
        resp.EnsureSuccessStatusCode();
        var json = await resp.Content.ReadFromJsonAsync<JsonElement>(cancellationToken: cancellationToken);
        return json.GetProperty("choices")[0].GetProperty("message").GetProperty("content").GetString() ?? string.Empty;
    }

    public async Task<float[]> EmbedAsync(string text, CancellationToken cancellationToken = default)
    {
        var payload = new { model = "text-embedding-ada-002", input = text };
        var resp = await _http.PostAsJsonAsync("/embeddings", payload, cancellationToken);
        resp.EnsureSuccessStatusCode();
        var json = await resp.Content.ReadFromJsonAsync<JsonElement>(cancellationToken: cancellationToken);
        return json.GetProperty("data")[0].GetProperty("embedding").EnumerateArray().Select(e => e.GetSingle()).ToArray();
    }
} 