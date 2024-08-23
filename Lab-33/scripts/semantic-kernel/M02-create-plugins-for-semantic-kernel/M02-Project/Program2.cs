using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Plugins.Core;

var builder = Kernel.CreateBuilder();
builder..AddAzureOpenAIChatCompletion(
    "your-deployment-name",
    "your-endpoint",
    "your-api-key",
    "deployment-model");

var kernel = builder.Build();

string language = "French";
// string prompt = @$"Create a list of helpful phrases and 
//     words in ${language} a traveler would find useful.";

// string prompt = @$"Create a list of helpful phrases and 
//     words in ${language} a traveler would find useful.

//     Group phrases by category. Display the phrases in 
//     the following format: Hello - Ciao [chow]";


string language = "French";
string history = @"I'm traveling with my kids and one of them 
    has a peanut allergy.";

string prompt = @$"Consider the traveler's background:
    ${history}

    Create a list of helpful phrases and words in 
    ${language} a traveler would find useful.

    Group phrases by category. Include common direction 
    words. Display the phrases in the following format: 
    Hello - Ciao [chow]";
    
var result = await kernel.InvokePromptAsync(prompt);
Console.WriteLine(result);