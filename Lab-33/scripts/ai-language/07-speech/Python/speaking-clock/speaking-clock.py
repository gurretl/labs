# https://microsoftlearning.github.io/mslearn-ai-language/Instructions/Exercises/07-speech.html

from dotenv import load_dotenv
from datetime import datetime
import os

# Import namespaces
# pip install azure-cognitiveservices-speech==1.30.0
# pip install playsound==1.2.2

import azure.cognitiveservices.speech as speech_sdk
from playsound import playsound

def main():
    try:
        global speech_config

        # Get Configuration Settings
        load_dotenv()
        ai_key = os.getenv('SPEECH_KEY')
        ai_region = os.getenv('SPEECH_REGION')

        # Configure speech service
        speech_config = speech_sdk.SpeechConfig(ai_key, ai_region)
        print('Ready to use speech service in:', speech_config.region)
        
        # Get spoken input
        command = TranscribeCommand()
        if command.lower() == 'what time is it?':
            TellTime()

    except Exception as ex:
        print(ex)

def TranscribeCommand():
    command = ''

    # Configure speech recognition (using default microphone)
    # audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
    # speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)
    # print('Speak now...')

    # Configure speech recognition audio file
    current_dir = os.getcwd()
    audioFile = current_dir + '\\time.wav'
    playsound(audioFile)
    audio_config = speech_sdk.AudioConfig(filename=audioFile)
    speech_recognizer = speech_sdk.SpeechRecognizer(speech_config, audio_config)

    # Process speech input
    speech = speech_recognizer.recognize_once_async().get()
    if speech.reason == speech_sdk.ResultReason.RecognizedSpeech:
        command = speech.text
        print(command)
    else:
        print(speech.reason)
        if speech.reason == speech_sdk.ResultReason.Canceled:
            cancellation = speech.cancellation_details
            print(cancellation.reason)
            print(cancellation.error_details)

    # Return the command
    return command


def TellTime():
    now = datetime.now()
    response_text = 'The time is {}:{:02d}'.format(now.hour,now.minute)

    # Configure speech synthesis
    speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    # Configure speech synthesis (other voice)
    # speech_config.speech_synthesis_voice_name = 'en-GB-LibbyNeural' # change this
    # speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)

    
    # Synthesize spoken output
    speak = speech_synthesizer.speak_text_async(response_text).get()
    if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print(speak.reason)

    # Synthesize spoken output (SSML)
    # responseSsml = " \
    #     <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'> \
    #         <voice name='en-GB-LibbyNeural'> \
    #             {} \
    #             <break strength='weak'/> \
    #             Time to end this lab! \
    #         </voice> \
    #     </speak>".format(response_text)
    # speak = speech_synthesizer.speak_ssml_async(responseSsml).get()
    # if speak.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
    #     print(speak.reason)

    # Print the response
    print(response_text)


if __name__ == "__main__":
    main()