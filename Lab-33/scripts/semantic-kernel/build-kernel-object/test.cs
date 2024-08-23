using Microsoft.SemanticKernel;

var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    "your-deployment-name",
    "your-endpoint",
    "your-api-key",
    "deployment-model");
var kernel = builder.Build();

var result = await kernel.InvokePromptAsync(
        "Give me a list of breakfast foods with eggs and cheese");
    Console.WriteLine(result);