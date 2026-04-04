import pyttsx3
import speech_recognition as sr
import subprocess
import os
import sys
import datetime
import random
import webbrowser

user_name = input("Enter your name here: ")

engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate - 50)
engine.setProperty('volume', 1)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak(text):
    print(f"Agent: {text}")          
    engine.say(text)
    engine.runAndWait()

def get_greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        period = "Good morning"
    elif hour < 17:
        period = "Good afternoon"
    else:
        period = "Good evening"
    return f"{period}, {user_name}! How can I assist you today?"

def get_time():
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."

def get_date():
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %d %B %Y')}."

def get_weather_tip():
    tips = [
        "Make sure to check humidity levels before irrigation today.",
        "Wind speed looks relevant for spraying — check before you apply pesticides.",
        "Opening the weather page now so you get the full forecast.",
    ]
    return random.choice(tips)

def get_crop_tip():
    tips = [
        "Kharif crops like rice and maize are best sown between June and July.",
        "Rabi crops like wheat thrive when sown between October and December.",
        "Always check soil moisture before deciding your sowing date.",
    ]
    return random.choice(tips)

running_apps = {}   # track launched processes

def launch_streamlit(name, script_path):
    # If already running and process hasn't exited, skip relaunch
    if name in running_apps and running_apps[name].poll() is None:
        speak(f"The {name} is already open in your browser!")
        return
    proc = subprocess.Popen(["streamlit", "run", script_path])
    running_apps[name] = proc
    speak(f"Launched {name}. It should open in your browser shortly.")

BASE = r"c:\Users\ARCHAN\Documents\AgroVeda-notebooks"
WEATHER_SCRIPT   = os.path.join(BASE, "weather_app.py")
CROP_CAL_SCRIPT  = os.path.join(BASE, "crop_calender.py")

def match_intent(text):
    t = text.lower()

    if any(w in t for w in ["hello", "hi", "hey", "good morning", "good evening", "good afternoon"]):
        return "greeting"
    
    if any(w in t for w in ["i am fine", "i am okay", "i am good", "doing well", "feeling good"]):
        return "wellbeing"

    if any(w in t for w in ["how are you", "how do you do", "are you okay"]):
        return "agent_wellbeing"
    if any(w in t for w in ["time", "what time", "current time"]):
        return "time"

    if any(w in t for w in ["date", "today", "what day", "which day"]):
        return "date"
    if any(w in t for w in ["weather", "rain", "forecast", "temperature", "humidity", "climate"]):
        return "weather"
    
    if any(w in t for w in ["crop", "calendar", "calender", "sowing", "farming", "harvest", "plantation", "kharif", "rabi"]):
        return "crop_calendar"
    if any(w in t for w in ["help", "what can you do", "commands", "features"]):
        return "help"
    

    if any(w in t for w in ["bye", "exit", "quit", "goodbye", "stop", "close"]):
        return "exit"

    return "unknown"


def handle_intent(intent):
    if intent == "greeting":
        speak(get_greeting())

    elif intent == "wellbeing":
        speak(random.choice([
            "Glad to hear that!",
            f"That's great, {user_name}! Let's get to work.",
            "Wonderful! How can I help you today?"
        ]))

    elif intent == "agent_wellbeing":
        speak(random.choice([
            f"I am doing great, {user_name}! Always ready to help you.",
            "All systems running smoothly! What do you need?",
            "I am functioning perfectly. What can I do for you?"
        ]))

    elif intent == "time":
        speak(get_time())

    elif intent == "date":
        speak(get_date())

    elif intent == "weather":
        speak(get_weather_tip())
        launch_streamlit("Weather App", WEATHER_SCRIPT)

    elif intent == "crop_calendar":
        speak(get_crop_tip())
        launch_streamlit("Crop Calendar", CROP_CAL_SCRIPT)

    elif intent == "help":
        speak(
            f"Sure {user_name}! I can help you with: "
            "weather updates, crop calendar, current time and date, "
            "and general conversation. Just speak naturally!"
        )

    elif intent == "exit":
        speak(f"Goodbye {user_name}! Have a productive day. See you soon.")
        return False    # signal to break loop

    else:
        speak(random.choice([
            f"I am not sure I understood that, {user_name}. Could you rephrase?",
            "Hmm, I didn't catch that. Try asking about weather, crops, or say help.",
            f"Sorry {user_name}, I don't know how to help with that yet."
        ]))

    return True     # continue loop

speak(f"Hello {user_name}! I am AgroSathi, your smart farming assistant. How can I help you today?")

r = sr.Recognizer()

while True:
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source)

        # Recognize outside 'with' block so mic releases cleanly before speak()
        text = r.recognize_google(audio)
        text = text.lower()
        print(f"{user_name}: {text}")

        intent = match_intent(text)
        should_continue = handle_intent(intent)
        if not should_continue:
            break

    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
    except KeyboardInterrupt:
        print("\nProgram Terminated.")
        break