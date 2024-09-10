import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
from tts_module import text_to_speech
from stt_module import (
    start_listening, 
    stop_listening, 
    test_microphone, 
    list_microphones, 
    save_and_transcribe_audio, 
    recognizer, 
    sr
)

# Add this import at the top of the file
import pyperclip

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Speech Recognition App")
    root.geometry("500x400+500+300")  # Increased size to accommodate the microphone selection

    # Set the window icon
    root.iconbitmap('images/stt_icon_xgT_icon.ico')

    # Create a frame for microphone selection
    mic_frame = tk.Frame(root)
    mic_frame.pack(pady=10)

    # Create a dropdown for microphone selection
    mic_label = tk.Label(mic_frame, text="Select Microphone:")
    mic_label.pack()
    mic_names = sr.Microphone.list_microphone_names()
    mic_var = tk.StringVar(root)
    mic_var.set(mic_names[0])  # Set the default value
    mic_dropdown = ttk.Combobox(mic_frame, textvariable=mic_var, values=mic_names, width=50)
    mic_dropdown.pack()

    # Create a button to start the microphone test
    test_button = tk.Button(mic_frame, text="Test Microphone", command=lambda: test_mic(root, mic_button, tts_button, mic_var))
    test_button.pack(pady=5)

    # Create a checkbox for playing audio before sending to API
    global play_audio_var
    play_audio_var = tk.BooleanVar(value=True)
    play_audio_checkbox = tk.Checkbutton(mic_frame, text="Play audio before sending to API", variable=play_audio_var)
    play_audio_checkbox.pack(pady=5)

    # Create a frame for the buttons
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    # Create the microphone button with text
    mic_button = tk.Button(button_frame, text="🎤", font=("Arial", 20), state=tk.DISABLED)
    mic_button.pack(side=tk.LEFT, padx=5)
    mic_button.bind("<ButtonPress>", lambda event: on_mic_press(event, selected_microphone))
    mic_button.bind("<ButtonRelease>", lambda event: on_mic_release(event, selected_microphone))

    # Create the TTS button
    tts_button = tk.Button(button_frame, text="🔊", font=("Arial", 20), command=on_tts_click, state=tk.DISABLED)
    tts_button.pack(side=tk.LEFT, padx=5)

    # Create the Copy button
    copy_button = tk.Button(button_frame, text="📋", font=("Arial", 20), command=on_copy_click)
    copy_button.pack(side=tk.LEFT, padx=5)

    # Create a scrolled text widget for displaying multiple lines
    global text_area
    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=10)
    text_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

    # Start the GUI event loop
    root.mainloop()

def test_mic(root, mic_button, tts_button, mic_var):
    text_area.insert(tk.END, "Testing microphone...\n")
    text_area.see(tk.END)
    root.update()  # Force update of the GUI

    print("Testing microphone...")
    mic_names = sr.Microphone.list_microphone_names()
    selected_index = mic_names.index(mic_var.get())
    
    global selected_microphone
    selected_microphone = sr.Microphone(device_index=selected_index)
    
    if not test_microphone(selected_microphone):
        error_message = "Microphone test failed. Please check your microphone settings and console output for details."
        text_area.insert(tk.END, "Microphone test failed. Check console for details.\n")
        messagebox.showerror("Microphone Error", error_message)
    else:
        text_area.insert(tk.END, "Microphone test passed. Ready to use.\n")
        text_area.see(tk.END)
        mic_button.config(state=tk.NORMAL)
        tts_button.config(state=tk.NORMAL)

def on_mic_press(event, microphone):
    # Clear the content of the text area
    text_area.delete(1.0, tk.END)
    
    text_area.insert(tk.END, "Listening...\n")
    text_area.see(tk.END)
    event.widget.config(relief=tk.SUNKEN, bg='red')
    global audio_data, audio_thread
    audio_data = None
    
    def capture_audio():
        global audio_data
        try:
            with microphone as source:
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Capturing audio...")
                audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                print(f"Audio captured. Duration: {len(audio_data.frame_data) / audio_data.sample_rate:.2f} seconds")
        except Exception as e:
            print(f"Error capturing audio: {type(e).__name__}: {str(e)}")
            text_area.insert(tk.END, f"Error capturing audio: {type(e).__name__}\n")
            text_area.see(tk.END)
    
    # Start audio capture in a separate thread
    audio_thread = threading.Thread(target=capture_audio)
    audio_thread.start()

def on_mic_release(event, microphone):
    event.widget.config(relief=tk.RAISED, bg='SystemButtonFace')
    global audio_data, audio_thread
    
    # Wait for the audio capture thread to complete
    audio_thread.join()
    
    if audio_data:
        print("Audio data captured, proceeding to transcription...")
        recognized_text = save_and_transcribe_audio(audio_data, should_play_audio=play_audio_var.get())
        if recognized_text:
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, f"{recognized_text}")
        # Copy recognized text to clipboard
        if recognized_text:
            pyperclip.copy(recognized_text)
            text_area.insert(tk.END, "\nText copied to clipboard.\n")
        else:
            text_area.insert(tk.END, "Speech not recognized. Please try again.\n")
    else:
        print("No audio data captured.")
        text_area.insert(tk.END, "No audio captured. Please try again.\n")
    text_area.see(tk.END)
    
    # Reset audio_data after processing
    audio_data = None

def on_tts_click():
    # This function will be called when the TTS button is clicked
    text = text_area.get("1.0", tk.END).strip()
    if text:
        text_to_speech(text)
    else:
        text_area.insert(tk.END, "Please enter some text to convert to speech.\n")
    text_area.see(tk.END)

def on_copy_click():
    # This function will be called when the Copy button is clicked
    text = text_area.get("1.0", tk.END).strip()
    if text:
        pyperclip.copy(text)
        text_area.insert(tk.END, "\nText copied to clipboard.\n")
    else:
        text_area.insert(tk.END, "No text to copy.\n")
    text_area.see(tk.END)

if __name__ == "__main__":
    main()