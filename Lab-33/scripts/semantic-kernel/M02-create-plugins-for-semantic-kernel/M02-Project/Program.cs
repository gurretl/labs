#pragma warning disable SKEXP0050 
using Microsoft.SemanticKernel;

string yourDeploymentName = "";
string yourEndpoint = "";
string yourApiKey = "";

var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    yourDeploymentName,
    yourEndpoint,
    yourApiKey,
    "gpt-35-turbo-16k");

var kernel = builder.Build();
var result = await kernel.InvokePromptAsync(
    "Give me a list of breakfast foods with eggs and cheese");

Console.WriteLine(result);

builder.Plugins.AddFromType<ConversationSummaryPlugin>();
var kernel = builder.Build();

string input = @"I'm a vegan in search of new recipes. I love spicy food! 
Can you give me a list of breakfast recipes that are vegan friendly?";

var result = await kernel.InvokeAsync(
    "ConversationSummaryPlugin", 
    "GetConversationActionItems", 
    new() {{ "input", input }});

Console.WriteLine(result);