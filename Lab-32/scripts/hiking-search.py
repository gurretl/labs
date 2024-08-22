# Inspired by https://microsoftlearning.github.io/mslearn-openai/Instructions/Exercises/06-use-own-data.html
# pip install openai==1.13.3

import os
import json
from dotenv import load_dotenv
import prompts

# Add OpenAI import
from openai import AzureOpenAI

def main(): 
        
    try:
        # Get configuration settings 
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
        azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        azure_search_key = os.getenv("AZURE_SEARCH_KEY")
        azure_search_index = os.getenv("AZURE_SEARCH_INDEX")
        
        # Initialize the Azure OpenAI client
        client = AzureOpenAI(
            base_url=f"{azure_oai_endpoint}/openai/deployments/{azure_oai_deployment}/extensions",
            api_key=azure_oai_key,
            api_version="2023-09-01-preview")

        # Get the prompt
        # text = input('\nEnter a question:\n')
        kilometers = input("Enter the number of kilometers: ")
        elevation_gain = input("Enter the elevation gain: ")

        # Generate the prompt
        system_message = prompts.system_message
        text = prompts.generate_prompt_search(kilometers, elevation_gain)

        # Configure your data source
        extension_config = dict(dataSources = [  
                { 
                    "type": "AzureCognitiveSearch", 
                    "parameters": { 
                        "endpoint":azure_search_endpoint, 
                        "key": azure_search_key, 
                        "indexName": azure_search_index,
                    }
                }]
            )

        # Send request to Azure OpenAI model
        print("...Sending the following request to Azure OpenAI endpoint...")
        print("Request: " + text + "\n")

        response = client.chat.completions.create(
            model = azure_oai_deployment,
            temperature = 0.5,
            max_tokens = 1000,
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": text}
            ],
            extra_body = extension_config
        )

        # Print response
        print("Response: " + response.choices[0].message.content + "\n")
        
    except Exception as ex:
        print(ex)


if __name__ == '__main__': 
    main()


