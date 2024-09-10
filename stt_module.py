import speech_recognition as sr
import openai
import wave
import os
import pygame

# Initialize OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

recognizer = sr.Recognizer()
listening = False
last_audio_file = None

def start_listening():
    global listening, last_audio_file
    listening = True
    print("Listening started...")
    
    # Delete the previous audio file if it exists
    if last_audio_file and os.path.exists(last_audio_file):
        os.remove(last_audio_file)
        print(f"Previous audio file {last_audio_file} deleted.")

def stop_listening(microphone):
    global listening, last_audio_file
    listening = False
    print("Listening stopped.")
    
    try:
        with microphone as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.energy_threshold = 300  # Adjust this value if needed
            print(f"Energy threshold: {recognizer.energy_threshold}")
            print("Capturing audio...")
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            print(f"Audio captured. Duration: {len(audio.frame_data) / audio.sample_rate:.2f} seconds")
            print(f"Sample width: {audio.sample_width}, Sample rate: {audio.sample_rate}, Frame data length: {len(audio.frame_data)}")
            
            # Check if the audio contains speech
            if len(audio.frame_data) / audio.sample_rate < 0.5:  # If audio is shorter than 0.5 seconds
                print("Audio too short, likely doesn't contain speech.")
                return None
            
        return save_and_transcribe_audio(audio)
    except sr.WaitTimeoutError:
        print("No speech detected (timeout)")
    except Exception as e:
        print(f"Error capturing audio: {type(e).__name__}: {str(e)}")
    return None

def save_and_transcribe_audio(audio, should_play_audio=True):
    global last_audio_file
    try:
        # Save audio to a WAV file in the current directory
        last_audio_file = "last_recorded_audio.wav"
        with wave.open(last_audio_file, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(audio.sample_width)
            wav.setframerate(audio.sample_rate)
            wav.writeframes(audio.frame_data)

        print(f"Audio file saved: {last_audio_file}")
        file_size = os.path.getsize(last_audio_file)
        print(f"File size: {file_size} bytes")

        if file_size == 0:
            print("Error: Audio file is empty")
            return None

        # Play back the recorded audio if should_play_audio is True
        if should_play_audio:
            play_audio(last_audio_file)

        # Use OpenAI's Whisper model for transcription
        with open(last_audio_file, 'rb') as audio_file:
            print("Sending audio to OpenAI for transcription...")
            transcript = openai.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text",
                language="en"  # Specify English as the language
            )
        
        print(f"Raw transcription result: {transcript}")
        
        return transcript.strip()
    except Exception as e:
        print(f"Error during transcription: {type(e).__name__}: {str(e)}")
    finally:
        # Ensure pygame mixer is stopped and uninitialized
        pygame.mixer.quit()
    return None

def play_audio(file_path):
    print(f"Playing back recorded audio: {file_path}")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error playing audio: {type(e).__name__}: {str(e)}")
    finally:
        pygame.mixer.quit()
    print("Playback finished")

def test_microphone(microphone):
    try:
        print("Attempting to initialize microphone...")
        print("Microphone initialized successfully.")
        
        with microphone as source:
            print("Microphone opened. Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.energy_threshold = 300  # Adjust this value if needed
            print(f"Energy threshold set to: {recognizer.energy_threshold}")
            print("Listening for audio...")
            audio = recognizer.listen(source, timeout=5)
            print(f"Audio captured successfully. Duration: {len(audio.frame_data) / audio.sample_rate:.2f} seconds")
            print(f"Sample width: {audio.sample_width}, Sample rate: {audio.sample_rate}, Frame data length: {len(audio.frame_data)}")
        
        # Save and play the test audio
        test_file = "microphone_test.wav"
        with wave.open(test_file, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(audio.sample_width)
            wav.setframerate(audio.sample_rate)
            wav.writeframes(audio.frame_data)
        print(f"Test audio saved to {test_file}")
        play_audio(test_file)
        
        return True
    except Exception as e:
        print(f"Error detecting microphone: {type(e).__name__}: {str(e)}")
    return False

# Add this function to get a list of available microphones
def list_microphones():
    print("Available microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"Microphone with name \"{name}\" found for `Microphone(device_index={index})`")

def select_microphone():
    list_microphones()
    while True:
        try:
            index = int(input("Enter the index of the microphone you want to use: "))
            return sr.Microphone(device_index=index)
        except ValueError:
            print("Please enter a valid number.")
        except sr.RequestError:
            print("Invalid microphone index. Please try again.")

if __name__ == "__main__":
    selected_microphone = select_microphone()
    test_microphone(selected_microphone)