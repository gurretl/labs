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

// var kernel = builder.Build();
// var result = await kernel.InvokePromptAsync(
//     "Give me a list of breakfast foods with eggs and cheese");
    
// Console.WriteLine(result);

var kernel = builder.Build();
kernel.ImportPluginFromType<MusicLibraryPlugin>();

var result = await kernel.InvokeAsync(
    "MusicLibraryPlugin", 
    "AddToRecentlyPlayed", 
    new() {
        ["artist"] = "Tiara", 
        ["song"] = "Danse", 
        ["genre"] = "French pop, electropop, pop"
    }
);

Console.WriteLine(result);