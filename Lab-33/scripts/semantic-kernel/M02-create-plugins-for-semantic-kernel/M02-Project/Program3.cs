using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.Plugins.Core;

var builder = Kernel.CreateBuilder();
builder.AddAzureOpenAIChatCompletion(
    "your-deployment-name",
    "your-endpoint",
    "your-api-key",
    "deployment-model");

var kernel = builder.Build();

string language = "French";
string history = @"I'm traveling with my kids and one of them has a peanut allergy.";

// Assign a persona to the prompt
string prompt = @$"
    You are a travel assistant. You are helpful, creative, and very friendly. 
    Consider the traveler's background:
    ${history}

    Create a list of helpful phrases and words in ${language} a traveler would find useful.

    Group phrases by category. Include common direction words. 
    Display the phrases in the following format: 
    Hello - Ciao [chow]

    Begin with: 'Here are some phrases in ${language} you may find helpful:' 
    and end with: 'I hope this helps you on your trip!'";

// string prompt = @$"
//     The following is a conversation with an AI travel assistant. 
//     The assistant is helpful, creative, and very friendly.

//     <message role=""user"">Can you give me some travel destination suggestions?</message>

//     <message role=""assistant"">Of course! Do you have a budget or any specific 
//     activities in mind?</message>

//     <message role=""user"">${input}</message>";

var result = await kernel.InvokePromptAsync(prompt);
Console.WriteLine(result);