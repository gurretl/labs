using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Plugins.Core;
using Microsoft.SemanticKernel.ChatCompletion;

var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    "your-deployment-name",
    "your-endpoint",
    "your-api-key",
    "deployment-model");
var kernel = builder.Build();

kernel.ImportPluginFromType<ConversationSummaryPlugin>();
var prompts = kernel.ImportPluginFromPromptDirectory("Prompts/TravelPlugins");

ChatHistory history = [];
string input = @"I'm planning an anniversary trip with my spouse. We like hiking, 
    mountains, and beaches. Our travel budget is $15000";

var result = await kernel.InvokeAsync<string>(prompts["SuggestDestinations"],
    new() {{ "input", input }});

Console.WriteLine(result);
history.AddUserMessage(input);
history.AddAssistantMessage(result);

Console.WriteLine("Where would you like to go?");
input = Console.ReadLine();

result = await kernel.InvokeAsync<string>(prompts["SuggestActivities"],
    new() {
        { "history", history },
        { "destination", input },
    }
);
Console.WriteLine(result);