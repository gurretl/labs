# Inspired by https://github.com/chenjd/azure-openai-gpt4-voice-chatbot
# Thank you Jiadong Chen for the inspiration!
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import prompts

import azure.cognitiveservices.speech as speechsdk

load_dotenv()
azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
azure_oai_key = os.getenv("AZURE_OAI_KEY")
azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")

# Set up Azure Speech-to-Text and Text-to-Speech credentials
speech_key = os.getenv("SPEECH_KEY")
service_region = os.getenv("SERVICE_REGION")
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# Set up Azure Text-to-Speech language 
speech_config.speech_synthesis_language = "en-US"
# Set up Azure Speech-to-Text language recognition
speech_config.speech_recognition_language = "en-US"

# Set up the voice configuration
speech_config.speech_synthesis_voice_name = "en-US-DavisNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# Define the speech-to-text function
def speech_to_text():
    # Set up the audio configuration
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    # Create a speech recognizer and start the recognition
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    print("Say something...")

    result = speech_recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        return "Sorry, I didn't catch that."
    elif result.reason == speechsdk.ResultReason.Canceled:
        return "Recognition canceled."

# Define the Azure OpenAI language generation function
def generate_text(prompt):
    
    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=azure_oai_endpoint,
        api_key=azure_oai_key,
        api_version="2024-02-15-preview"
    )

    # Generate the prompt
    system_message = prompts.system_message

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
    return generated_text


# Define the text-to-speech function
import azure.cognitiveservices.speech as speechsdk

def text_to_speech(text):
    """
    Converts the given text to speech using the Azure Cognitive Services Speech Synthesis API.

    Args:
        text (str): The text to be converted to speech.

    Returns:
        bool: True if the text-to-speech conversion is successful, False otherwise.
    """
    try:
        # Construct the SSML string with the provided text
        ssml_string = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
                <voice name="en-US-DavisNeural">
                    <mstts:express-as style="angry" styledegree="8">
                        <prosody pitch="medium" rate="30%">{text}</prosody>
                    </mstts:express-as>
                </voice>
            </speak>
        """
                
        # Create a speech synthesizer with the provided speech configuration
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        # Perform the text-to-speech conversion
        result = speech_synthesizer.speak_ssml_async(ssml_string).get()
        
        # Check the result of the conversion
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Text-to-speech conversion successful.")
            return True
        else:
            print(f"Error synthesizing audio: {result}")
            return False
    except Exception as ex:
        print(f"Error synthesizing audio: {ex}")
        return False

# Main program loop
while True:
    # Get input from user using speech-to-text
    user_input = speech_to_text()
    print(f"You said: {user_input}")

    # Generate a response using OpenAI
    prompt = f"Q: {user_input}\nA:"
    response = generate_text(prompt)
    #response = user_input
    print(f"AI says: {response}")

    # Convert the response to speech using text-to-speech
    text_to_speech(response)
