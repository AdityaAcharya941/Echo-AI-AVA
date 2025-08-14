import speech_recognition as sr
import pyttsx3
import datetime
import os
import webbrowser
import requests
import json
import time
import logging
from bs4 import BeautifulSoup
import logging_config
import spacy
from transformers import pipeline
from google.cloud import translate
from newsapi import NewsApiClient
import openweathermap
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

class EchoAssistant:
    def __init__(self):
        # Initialize the speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Set voice properties
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)  # Use female voice
        self.engine.setProperty('rate', 180)  # Speed of speech
        
        # Initialize logger
        self.logger = logging.getLogger('echo')
        
        # Initialize command history
        self.command_history = []
        
        # Initialize the assistant name
        self.name = "Echo"
        
        # Initialize NLP components
        self.nlp = spacy.load('en_core_web_sm')
        self.sentiment_analyzer = pipeline('sentiment-analysis')
        
        # Initialize translation client
        self.translate_client = translate.TranslationClient()
        
        # Initialize news API client
        self.news_client = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        
        # Initialize weather client
        self.weather_client = openweathermap.OpenWeatherMap(os.getenv('WEATHER_API_KEY'))
        
        # Initialize database connection
        engine = create_engine('sqlite:///echo_assistant.db')
        Session = sessionmaker(bind=engine)
        self.db_session = Session()
        
        # Initialize conversation context
        self.conversation_context = {}
        
        # Greet the user
        self.speak(f"Hello, I am {self.name}, your personal voice assistant. How can I help you today?")
    
    def listen(self):
        """Listen for voice commands from the user"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                # Adjust for ambient noise and set timeout
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                
                print("Recognizing...")
                command = self.recognizer.recognize_google(audio, language='en-US')
                command = command.lower()
                print(f"User said: {command}")
                
                # Add command to history
                self.command_history.append(command)
                
                return command
        except sr.UnknownValueError:
            print("Sorry, I didn't understand that.")
            self.speak("Sorry, I didn't understand that.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            self.speak("I'm having trouble connecting to the speech recognition service.")
            return ""
        except Exception as e:
            self.logger.error(f"Error in listen function: {e}")
            self.speak("I encountered an error while listening.")
            return ""
    
    def speak(self, text):
        """Convert text to speech"""
        try:
            print(f"{self.name}: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error in speak function: {e}")
    
    def process_command(self, command):
        """Process the voice command and execute appropriate action"""
        try:
            # Check for wake word/phrase
            if self.name.lower() in command:
                command = command.replace(self.name.lower(), "").strip()
            
            # Basic commands
            if "hello" in command or "hi" in command:
                self.speak(f"Hello! How can I help you today?")
            
            elif "time" in command:
                self.get_time()
            
            elif "date" in command:
                self.get_date()
            
            # Application control
            elif "open" in command:
                self.open_application(command)
            
            # Web search
            elif "search" in command or "google" in command:
                self.search_online(command)
            
            # System settings
            elif "volume" in command:
                self.control_volume(command)
            
            elif "wifi" in command:
                self.toggle_wifi(command)
            
            # Reminders and alarms
            elif "remind" in command or "reminder" in command:
                self.set_reminder(command)
            
            elif "alarm" in command:
                self.set_alarm(command)
            
            # Exit command
            elif "exit" in command or "quit" in command or "goodbye" in command:
                self.speak("Goodbye! Have a great day!")
                return False
            
            # Help command
            elif "help" in command or "what can you do" in command:
                self.provide_help()
            
            # If no command matches
            else:
                self.speak("I'm not sure how to help with that yet. Please try a different command.")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            self.speak("I encountered an error while processing your command.")
            return True
    
    def get_time(self):
        """Get and speak the current time"""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.speak(f"The current time is {current_time}")
    
    def get_date(self):
        """Get and speak the current date"""
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        self.speak(f"Today is {current_date}")
    
    def open_application(self, command):
        """Open applications on the PC"""
        # Extract application name from command
        if "open" in command:
            app_name = command.replace("open", "").strip()
            
            # Common applications dictionary
            apps = {
                "notepad": "notepad",
                "calculator": "calc",
                "paint": "mspaint",
                "word": "winword",
                "excel": "excel",
                "chrome": "chrome",
                "firefox": "firefox",
                "edge": "msedge",
                "file explorer": "explorer",
                "settings": "ms-settings:"
            }
            
            # Check if the app is in our dictionary
            for key in apps:
                if key in app_name:
                    self.speak(f"Opening {key}")
                    os.system(f"start {apps[key]}")
                    return
            
            # If app not found in dictionary, try to open it directly
            try:
                self.speak(f"Trying to open {app_name}")
                os.system(f"start {app_name}")
            except Exception as e:
                print(f"Error opening application: {e}")
                self.speak(f"I couldn't open {app_name}")
    
    def search_online(self, command):
        """Search online and provide results"""
        search_engines = {
            "google": "https://www.google.com/search?q=",
            "bing": "https://www.bing.com/search?q=",
            "youtube": "https://www.youtube.com/results?search_query="
        }
        
        # Extract search query and engine
        query = ""
        engine_url = search_engines["google"]  # Default to Google
        
        if "youtube" in command:
            query = command.replace("search on youtube", "").replace("youtube", "").strip()
            engine_url = search_engines["youtube"]
        elif "bing" in command:
            query = command.replace("search on bing", "").replace("bing", "").strip()
            engine_url = search_engines["bing"]
        else:  # Default to Google
            query = command.replace("search", "").replace("google", "").strip()
        
        if query:
            self.speak(f"Searching for {query}")
            webbrowser.open(f"{engine_url}{query}")
            
            # For Google searches, try to extract and read the first result
            if engine_url == search_engines["google"]:
                try:
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    response = requests.get(f"{engine_url}{query}", headers=headers)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Try to find the first search result
                    search_results = soup.find_all('h3')
                    if search_results and len(search_results) > 0:
                        first_result = search_results[0].text
                        self.speak(f"Here's what I found: {first_result}")
                except Exception as e:
                    print(f"Error extracting search results: {e}")
        else:
            self.speak("What would you like me to search for?")
    
    def control_volume(self, command):
        """Control system volume"""
        try:
            if "up" in command or "increase" in command:
                self.speak("Increasing volume")
                # For Windows
                os.system("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]175)\"")
            elif "down" in command or "decrease" in command or "lower" in command:
                self.speak("Decreasing volume")
                # For Windows
                os.system("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]174)\"")
            elif "mute" in command or "unmute" in command:
                self.speak("Toggling mute")
                # For Windows
                os.system("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]173)\"")
            else:
                self.speak("I'm not sure what volume action you want me to perform.")
        except Exception as e:
            self.logger.error(f"Error controlling volume: {e}")
            self.speak("I encountered an error while trying to control the volume.")
    
    def toggle_wifi(self, command):
        """Toggle WiFi on/off"""
        try:
            if "on" in command or "enable" in command:
                self.speak("Turning WiFi on")
                os.system('netsh interface set interface "Wi-Fi" enable')
            elif "off" in command or "disable" in command:
                self.speak("Turning WiFi off")
                os.system('netsh interface set interface "Wi-Fi" disable')
            else:
                self.speak("Would you like to turn WiFi on or off?")
        except Exception as e:
            self.logger.error(f"Error toggling WiFi: {e}")
            self.speak("I encountered an error while trying to control WiFi.")
    
    def set_reminder(self, command):
        """Set a reminder"""
        try:
            self.speak("What would you like me to remind you about?")
            reminder_text = self.listen()
            
            if reminder_text:
                self.speak("When should I remind you? Please specify the time.")
                reminder_time = self.listen()
                
                if reminder_time:
                    self.speak(f"I'll remind you to {reminder_text} at {reminder_time}")
                    # Here you would implement the actual reminder functionality
                    # This could involve scheduling a task or using a timer
                    # For now, we'll just acknowledge the reminder
                else:
                    self.speak("I couldn't understand the reminder time.")
            else:
                self.speak("I couldn't understand what to remind you about.")
        except Exception as e:
            self.logger.error(f"Error setting reminder: {e}")
            self.speak("I encountered an error while setting the reminder.")
    
    def set_alarm(self, command):
        """Set an alarm"""
        try:
            self.speak("At what time would you like to set the alarm?")
            alarm_time = self.listen()
            
            if alarm_time:
                self.speak(f"Alarm set for {alarm_time}")
                # Here you would implement the actual alarm functionality
                # This could involve scheduling a task or using a timer
                # For now, we'll just acknowledge the alarm
            else:
                self.speak("I couldn't understand the alarm time.")
        except Exception as e:
            self.logger.error(f"Error setting alarm: {e}")
            self.speak("I encountered an error while setting the alarm.")
    
    def provide_help(self):
        """Provide information about available commands"""
        help_text = (
            "I can help you with various tasks. Here are some things you can ask me to do:\n"
            "1. Get the time or date\n"
            "2. Open applications like Notepad, Calculator, or Chrome\n"
            "3. Search the web using Google, Bing, or YouTube\n"
            "4. Control system settings like volume and WiFi\n"
            "5. Set reminders and alarms\n"
            "6. Say 'exit' or 'goodbye' to close the assistant"
        )
        self.speak(help_text)

# Main function to run the assistant
def main():
    try:
        # Create the assistant
        assistant = EchoAssistant()
        
        running = True
        while running:
            command = assistant.listen()
            if command:
                running = assistant.process_command(command)
            
            # Small delay to prevent high CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nExiting Echo Assistant...")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()