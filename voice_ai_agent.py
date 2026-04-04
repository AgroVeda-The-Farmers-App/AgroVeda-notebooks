import pyttsx3
import speech_recognition as sr

user_name = input("Enter your name here: ")

engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)
engine.setProperty('volume', 1)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    engine.say(text)
    engine.runAndWait()

speak(f"Hello {user_name}, I am here to help you. Tell me what do you want me to do?")

r = sr.Recognizer()

while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source)

            text = r.recognize_google(audio)
            text = text.lower()
            print(f"{user_name}: {text}")

            if "hello" in text or "hi" in text:
                speak(f"Hello {user_name}, How are you?")
                #engine.say(" Hello how are you ?")

            elif "i am fine" in text or "i am okay" in text or "i am good" in text:
                speak("Glad to hear that!") 

            elif "bye" in text or "exit" in text or "quit" in text:
                speak("Goodbye! Have a great day.")
                break
            

    except sr.UnknownValueError:
        print("Could not understand audio.")

    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")

    except KeyboardInterrupt:
        print("\nProgram Terminated.")
        break