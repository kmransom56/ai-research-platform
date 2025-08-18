using CopilotChat.Shared.AI;

namespace CopilotChat.WebApi.Services;

public class LlmRouter : ILlmProvider
{
    private readonly Func<string, ILlmProvider> _factory;
    private readonly IConfiguration _config;

    public LlmRouter(Func<string, ILlmProvider> factory, IConfiguration config)
    {
        _factory = factory;
        _config = config;
    }

    private ILlmProvider Current => _factory(_config["Llm:Provider"]?.ToLowerInvariant() ?? "ollama");

    public Task<string> ChatAsync(string prompt, CancellationToken cancellationToken = default) =>
        Current.ChatAsync(prompt, cancellationToken);

    public Task<float[]> EmbedAsync(string text, CancellationToken cancellationToken = default) =>
        Current.EmbedAsync(text, cancellationToken);
} 