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

// string prompt = @"This is a list of music available to the user:
//     {{MusicLibraryPlugin.GetMusicLibrary}} 

//     This is a list of music the user has recently played:
//     {{MusicLibraryPlugin.GetRecentPlays}}

//     Based on their recently played music, suggest a song from
//     the list to play next";

// var result = await kernel.InvokePromptAsync(prompt);
// Console.WriteLine(result);

var kernel = builder.Build();
kernel.ImportPluginFromType<MusicLibraryPlugin>();
kernel.ImportPluginFromType<MusicConcertPlugin>();
kernel.ImportPluginFromPromptDirectory("Prompts");

// var planner = new HandlebarsPlanner(new HandlebarsPlannerOptions() { AllowLoops = true });

// string location = "Redmond WA USA";
// string goal = @$"Based on the user's recently played music, suggest a 
//     concert for the user living in ${location}";

// var plan = await planner.CreatePlanAsync(kernel, goal);
// var result = await plan.InvokeAsync(kernel);

// Console.WriteLine($"Results: {result}");

var planner = new HandlebarsPlanner(new HandlebarsPlannerOptions() { AllowLoops = true });

string location = "Redmond WA USA";
string goal = @$"Based on the user's recently played music, suggest a 
    concert for the user living in ${location}";

var concertPlan = await planner.CreatePlanAsync(kernel, goal);
// output the plan result
Console.WriteLine("Concert Plan:");
Console.WriteLine(concertPlan);

var songSuggesterFunction = kernel.CreateFunctionFromPrompt(
    promptTemplate: @"Based on the user's recently played music:
        {{$recentlyPlayedSongs}}
        recommend a song to the user from the music library:
        {{$musicLibrary}}",
    functionName: "SuggestSong",
    description: "Suggest a song to the user"
);

kernel.Plugins.AddFromFunctions("SuggestSongPlugin", [songSuggesterFunction]);

var songSuggestPlan = await planner.CreatePlanAsync(kernel, @"Suggest a song from the 
    music library to the user based on their recently played songs");

Console.WriteLine("Song Plan:");
Console.WriteLine(songSuggestPlan);