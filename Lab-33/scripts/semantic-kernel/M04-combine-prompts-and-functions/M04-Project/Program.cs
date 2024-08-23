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

// kernel.ImportPluginFromType<MusicLibraryPlugin>();

// var result = await kernel.InvokeAsync(
//     "MusicLibraryPlugin", 
//     "AddToRecentlyPlayed", 
//     new() {
//         ["artist"] = "Tiara", 
//         ["song"] = "Danse", 
//         ["genre"] = "French pop, electropop, pop"
//     }
// );

// Console.WriteLine(result);
var kernel = builder.Build();
kernel.ImportPluginFromType<MusicLibraryPlugin>();

string prompt = @"This is a list of music available to the user:
    {{MusicLibraryPlugin.GetMusicLibrary}} 

    This is a list of music the user has recently played:
    {{MusicLibraryPlugin.GetRecentPlays}}

    Based on their recently played music, suggest a song from
    the list to play next";

var result = await kernel.InvokePromptAsync(prompt);
Console.WriteLine(result);