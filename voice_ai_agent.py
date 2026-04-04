import pyttsx3
import speech_recognition as sr
import subprocess
import os
import sys

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
                engine.say(" Hello how are you ?")

            elif "i am fine" in text or "i am okay" in text or "i am good" in text:
                speak("Glad to hear that!") 

            elif "bye" in text or "exit" in text or "quit" in text:
                speak("Goodbye! Have a great day.")
                break

            elif "give weather update" in text or "show weather details" in text or "open weather page" in text or "weather" in text:
                speak("Sure, Opening the weather section...")

                weather_script = r"c:\Users\ARCHAN\Documents\AgroVeda-notebooks\weather_app.py"

                subprocess.Popen(["streamlit","run",weather_script])
                speak("Opened weather page.")

            elif "crop calender" in text or "crop timings" in text or "best time for crops" in text:
                engine.say("Sure, Opening crop calender section.")

                crop_cal = r"c:\Users\ARCHAN\Documents\AgroVeda-notebooks\crop_calender.py"

                subprocess.Popen(["streamlit","run",crop_cal])
                engine.say("Opened crop calender. Check what will be the best time for farming for you")



    except sr.UnknownValueError:
        print("Could not understand audio.")

    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")

    except KeyboardInterrupt:
        print("\nProgram Terminated.")
        break