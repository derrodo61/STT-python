import openai
import pygame
import os
from tempfile import NamedTemporaryFile

# Initialize OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

def text_to_speech(text, voice="alloy"):
    """
    Convert text to speech using OpenAI's TTS API and play the audio.
    
    :param text: The text to convert to speech
    :param voice: The voice to use (default is "alloy")
    """
    try:
        # Generate speech using OpenAI API
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )

        # Save the audio to a temporary file
        with NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio.write(response.content)
            temp_audio_path = temp_audio.name

        # Initialize pygame mixer
        pygame.mixer.init()

        # Load and play the audio
        pygame.mixer.music.load(temp_audio_path)
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        # Clean up
        pygame.mixer.quit()
        os.unlink(temp_audio_path)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Example usage
if __name__ == "__main__":
    text_to_speech("Hello, this is a test of the OpenAI text-to-speech functionality.")