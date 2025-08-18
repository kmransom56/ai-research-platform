namespace CopilotChat.Shared.AI;

public interface ILlmProvider
{
    Task<string> ChatAsync(string prompt, CancellationToken cancellationToken = default);
    Task<float[]> EmbedAsync(string text, CancellationToken cancellationToken = default);
} 