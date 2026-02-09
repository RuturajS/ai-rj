
import speech_recognition as sr
import pyaudio

def test_mic():
    p = pyaudio.PyAudio()
    print("\n=== Audio Devices ===")
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            name = p.get_device_info_by_host_api_device_index(0, i).get('name')
            print(f"Device ID {i} - {name}")

    print("\n=== Testing Default Mic ===")
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("Please speak now for 5 seconds...")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=5)
            print("Audio captured! Transcribing...")
            try:
                print("You said: " + r.recognize_google(audio))
            except sr.UnknownValueError:
                print("Error: Could not understand audio (Result was empty/noise)")
            except sr.RequestError as e:
                print(f"Error: Could not reach Google API ({e})")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        print("This usually means no microphone is detected or access is denied.")

if __name__ == "__main__":
    test_mic()
