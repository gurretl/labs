# import the necessary libraries
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import prompts

def main():
    try:
        # Get configuration settings
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")

        # Initialize the Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=azure_oai_endpoint,
            api_key=azure_oai_key,
            api_version="2024-02-15-preview"
        )

        # Read the hikes.txt file
        with open('hikes.txt', 'r') as file:
            hikes = file.read()

        # Ask the user for the kilometers and elevation gain
        kilometers = input("Enter the number of kilometers: ")
        elevation_gain = input("Enter the elevation gain: ")

        # Generate the prompt
        system_message = prompts.system_message
        prompt = prompts.generate_prompt(kilometers, elevation_gain, hikes)

        # Write the prompt to the generated_prompt.txt file
        with open('generated_prompt.txt', 'w') as file:
            file.write("Prompt: " + prompt)
        # exit()
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        # Send request to Azure OpenAI model
        response = client.chat.completions.create(
            model=azure_oai_deployment,
            temperature=0.5,
            max_tokens=400,
            messages=messages
        )
        generated_text = response.choices[0].message.content

        # Print the response
        print("Response: " + generated_text + "\n")

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    main()
