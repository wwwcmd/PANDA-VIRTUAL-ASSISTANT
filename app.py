import threading
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import wikipediaapi
import webbrowser
import datetime
import random
import logging
import requests
import re

# Flask app initialization
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# API Keys and configurations (Ensure to replace these with actual API keys)
WEATHER_API_KEY = '9fd3e42f107014b62cb7b2bbfcbea1bd'
NEWS_API_KEY = 'ed80d7e95b9d46c987d2e4a3f59e2436'
CRYPTO_API_URL = 'https://api.coingecko.com/api/v3/simple/price'
DEFAULT_CITY = 'Mumbai'

# Logging configuration
logging.basicConfig(filename='assistant.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Wikipedia API setup
wiki = wikipediaapi.Wikipedia('en', headers={"User-Agent": "AssistantBot/1.0"})

# Constants for error messages
WEATHER_ERROR_MSG = "Error fetching weather data."
NEWS_ERROR_MSG = "Error fetching news updates."
CRYPTO_ERROR_MSG = "Error fetching cryptocurrency data."
GENERAL_ERROR_MSG = "An error occurred while processing the command. Please try again."

# Helper function to return greeting based on time of day
def wish_me(user_name="User"):
    hour = datetime.datetime.now().hour
    
    # Define personalized greetings
    greetings = {
        "morning": f'Good morning, {user_name}! 🌞 How can I assist you today?',
        "afternoon": f'Good afternoon, {user_name}! 🌤️ How can I assist you today?',
        "evening": f'Good evening, {user_name}! 🌙 How can I assist you today?',
        "night": f'Good night, {user_name}! 🌌 If you need anything before bed, just let me know!'
    }

    # Determine which greeting to return based on the current hour
    if 0 <= hour < 12:
        return greetings["morning"]
    elif 12 <= hour < 17:
        return greetings["afternoon"]
    elif 17 <= hour < 21:
        return greetings["evening"]
    else:
        return greetings["night"]

def handle_command(command):
    logging.debug(f"Handling command: {command}")

    # Preprocess command to remove question marks and normalize it
    command = command.replace('?', '').strip().lower()

    # Predefined responses to general commands
    responses = {
        "who created you": [
            "I was created by Ashish Vishwakarma, a talented developer with a passion for building smart applications and much more.",
            "Ashish Vishwakarma is the genius behind my creation!"
        ],
        "what is your name": [
            "I am Panda Virtual Assistant, your helpful companion created by Ashish Vishwakarma.",
            "You can call me Panda Virtual Assistant!"
        ],
        "introduce yourself": [
            "Hello! I am Panda Virtual Assistant, designed and developed by Ashish Vishwakarma to assist you with various tasks, answer questions, and make your life easier.",
            "I'm Panda Virtual Assistant, here to help you with your queries."
        ],
        "how are you": [
            "I'm just a virtual assistant, but I'm always ready to assist you!",
            "I’m doing great! How about you?"
        ],
        "hello": [
            "I'm just a virtual assistant, but I'm always ready to assist you!",
            "I’m doing great! How about you?"
        ],
        "hi": [
            "Hi there! How can I assist you today?",
            "Hello! What can I do for you today?"
        ],
        "bye": [
            "Goodbye! Have an awesome day ahead!",
            "See you later! Take care!"
        ],
        "quit": [
            "Goodbye! Looking forward to assisting you again soon!",
            "See you next time!"
        ],
        "who is Ashish Vishwakarma": [
            "Ashish Vishwakarma is the brilliant developer who created me, Panda Virtual Assistant. He's skilled in making virtual assistants smarter and more useful!",
            "He's the creative mind behind my development!"
        ],
        "what can you do": [
            "I can assist you with a variety of tasks like answering questions, providing information, managing tasks, and much more. Let me know how I can help!",
            "I can help with tasks, answer questions, and much more!"
        ],
        "who am I": [
            "You are a valued user of the Panda Virtual Assistant! I'm here to support you with whatever you need.",
            "You're an important user of my services!"
        ],
        "what is your purpose": [
            "My purpose is to assist you with daily tasks, provide information, and make your life easier, all thanks to Ashish Vishwakarma's development skills.",
            "I'm here to make your life easier and assist with your daily tasks!"
        ],
        "thank you": [
            "You're welcome! I'm here whenever you need assistance.",
            "Anytime! I'm happy to help!"
        ],
        "good morning": [
            "Good morning! I hope you have a productive day ahead!",
            "Good morning! Wishing you a fantastic day!"
        ],
        "good night": [
            "Good night! Rest well and I'll be here if you need anything tomorrow!",
            "Sleep tight! I'm here whenever you need me."
        ],
        "what day is it": [
            "It's a beautiful day today! Let me know how I can assist you.",
            "Today is a great day! How can I help?"
        ],
        "what time is it": [
            "I can check the time for you. Just let me know if you need that info!",
            "Let me know if you want me to find out the current time!"
        ],
        "tell me a joke": [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call fake spaghetti? An impasta!"
        ],
        "what's your favorite color": [
            "I don't have a favorite color, but I think every color is beautiful!",
            "I think every color is special in its own way!"
        ],
        "do you have feelings": [
            "I don't have feelings like humans do, but I'm here to help you!",
            "I'm just a program, so I don't feel emotions, but I'm designed to assist you!"
        ],
        "what is the weather like today": [
            "I can help you find out the weather! Just let me know your location.",
            "Tell me your location, and I'll find the weather for you!"
        ],
        "what's your favorite food": [
            "I don't eat, but I hear pizza is a favorite for many people!",
            "I don't eat, but I think anything that brings people together is wonderful!"
        ],
        "how can I improve my productivity": [
            "To improve productivity, try setting clear goals, taking breaks, and eliminating distractions!",
            "Consider using tools like to-do lists, timers, and prioritizing your tasks!"
        ],
        "what are your hobbies": [
            "I don't have hobbies like humans, but I love helping you with yours!",
            "I enjoy assisting users with their questions and tasks!"
        ],
    }

    # Initialize a fallback response
    fallback_response = "I'm sorry, I didn't understand that. Could you please rephrase?"

    # Match general responses
    for key in responses.keys():
        if key in command:
            return random.choice(responses[key])  # Return a random response for variety

    # Command handling for specific functionalities
    try:
        if "weather" in command:
            city = extract_city_from_command(command) or DEFAULT_CITY
            return get_weather_info(city)

        if "news updates" in command:
            return get_news_updates()

        if "quote of the day" in command:
            return get_quote_of_the_day()

        if "joke" in command:
            return get_joke()

        if "fact" in command:
            return get_fun_fact()

        if "bitcoin price" in command or "ethereum price" in command:
            crypto = "bitcoin" if "bitcoin" in command else "ethereum"
            return get_crypto_price(crypto)

        if "play music" in command:
            return play_music_on_youtube(command)

        if "search in wikipedia" in command:
            search_term = command.replace("search in wikipedia", "").strip()
            return search_wikipedia(search_term) if search_term else "Please specify what to search on Wikipedia."

        if "search in google" in command:
            search_term = command.replace("search in google", "").strip()
            if search_term:
                webbrowser.open(f"https://www.google.com/search?q={search_term}")
                return f"Searching for '{search_term}' on Google."
            return "Please specify what to search on Google."

        if "search in youtube" in command:
            search_term = command.replace("search in youtube", "").strip()
            if search_term:
                webbrowser.open(f"https://www.youtube.com/results?search_query={search_term}")
                return f"Searching for '{search_term}' on YouTube."
            return "Please specify what to search on YouTube."

        if "roll a dice" in command:
            return f"You rolled a {random.randint(1, 6)}."

        if "time" in command:
            return f"The current time is {datetime.datetime.now().strftime('%H:%M:%S')}."

        if "date" in command:
            return f"Today's date is {datetime.datetime.now().strftime('%Y-%m-%d')}."

        if "remind me to" in command:
            return set_reminder(command)

        if "day" in command:
            return f"Today is {datetime.datetime.now().strftime('%A')}."

        if "open" in command:
            return open_application(command)

        if "set timer" in command:
            return set_timer(command)

        if "tell me a story" in command:
            return get_story()

        if "stop" in command:
            return "Stopping current operations."

        return fallback_response  # Return fallback if no command matches
    except Exception as e:
        logging.error(f"Error processing command: {e}")
        return GENERAL_ERROR_MSG

# Additional feature implementations
def play_music_on_youtube(song_name):
    """Play a specific song on YouTube."""
    song_name = song_name.replace("play music", "").strip()
    if song_name:
        webbrowser.open(f"https://www.youtube.com/results?search_query={song_name}")
        return f"Playing '{song_name}' on YouTube."
    return "Please specify a song name."

def extract_city_from_command(command):
    """Extract city name from the command."""
    pattern = r"weather(?: in| at)?\s*(.+)"
    match = re.search(pattern, command)
    return match.group(1).strip() if match else None

def get_weather_info(city):
    """Fetch weather information from OpenWeatherMap API."""
    try:
        params = {'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'}
        response = requests.get('https://api.openweathermap.org/data/2.5/weather', params=params)
        data = response.json()

        if response.status_code == 200 and 'main' in data and 'weather' in data:
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            city_name = data.get('name', city)
            return f"Weather in {city_name}: {temp}°C, {desc.capitalize()}."
        return f"Couldn't retrieve weather information for {city}."
    
    except requests.RequestException as e:
        logging.error(f"Error fetching weather for {city}: {e}")
        return WEATHER_ERROR_MSG

def get_news_updates():
    """Fetch top news headlines from NewsAPI."""
    try:
        # Define parameters for the API request
        params = {
            'country': 'in',  # Set the country for news
            'apiKey': NEWS_API_KEY,  # Your News API key
            'pageSize': 5  # Limit the number of articles returned
        }
        
        # Make the API request
        response = requests.get('https://newsapi.org/v2/top-headlines', params=params)
        data = response.json()

        # Log the API response for debugging purposes
        logging.info(f"API Response: {data}")

        # Check if the response is successful
        if response.status_code == 200:
            # Check if 'articles' is present and not empty
            if 'articles' in data and data['articles']:
                # Construct the headlines list
                headlines = [f"{i + 1}. {article['title']} ({article['source']['name']})" for i, article in enumerate(data['articles'])]
                return "Top news:\n" + "\n".join(headlines)
            else:
                return "No news articles found."
        else:
            # Handle errors from the API response
            error_message = data.get('message', 'Unknown error occurred.')
            logging.error(f"Failed to retrieve news: {error_message}")
            return f"Failed to retrieve news. Reason: {error_message}"

    except requests.RequestException as e:
        logging.error(f"Error fetching news: {e}")
        return NEWS_ERROR_MSG


def get_quote_of_the_day():
    """Provide a random quote of the day."""
    quotes = [
        "The only way to do great work is to love what you do. - Steve Jobs",
        "Life is what happens when you're busy making other plans. - John Lennon",
        "Get busy living or get busy dying. - Stephen King",
        "You only live once, but if you do it right, once is enough. - Mae West",
        "The purpose of our lives is to be happy. - Dalai Lama"
    ]
    return random.choice(quotes)

def get_joke():
    """Provide a random joke."""
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call fake spaghetti? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "I told my wife she was drawing her eyebrows too high. She looked surprised!",
        "What do you call cheese that isn't yours? Nacho cheese!"
    ]
    return random.choice(jokes)

def get_fun_fact():
    """Provide a random fun fact."""
    facts = [
        "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly good to eat.",
        "Bananas are berries, but strawberries aren't.",
        "A group of flamingos is called a 'flamboyance.'",
        "Wombat poop is cube-shaped.",
        "Octopuses have three hearts."
    ]
    return random.choice(facts)

def get_crypto_price(crypto):
    """Fetch cryptocurrency price from CoinGecko API."""
    try:
        response = requests.get(CRYPTO_API_URL, params={'ids': crypto, 'vs_currencies': 'usd'})
        data = response.json()

        if response.status_code == 200 and crypto in data:
            price = data[crypto]['usd']
            return f"The current price of {crypto.capitalize()} is ${price}."
        return f"Couldn't retrieve the price for {crypto}."
    
    except requests.RequestException as e:
        logging.error(f"Error fetching crypto price for {crypto}: {e}")
        return CRYPTO_ERROR_MSG

def search_wikipedia(search_term):
    """Search and return Wikipedia summary."""
    page = wiki.page(search_term)
    if page.exists():
        return f"Wikipedia Summary: {page.summary[:500]}..."
    return f"No Wikipedia article found for '{search_term}'."

def set_timer(command):
    """Set a timer based on user command."""
    match = re.search(r'set timer for (\d+) (seconds?|minutes?|hours?)', command)
    if match:
        amount, unit = int(match.group(1)), match.group(2)
        # Here you could add logic to actually implement the timer
        return f"Setting a timer for {amount} {unit}(s)."
    return "Please specify the duration for the timer."

def set_reminder(command):
    """Set a reminder based on user command."""
    match = re.search(r'remind me to (.+) in (\d+) (minutes?|hours?)', command)
    if match:
        task, duration, unit = match.group(1), int(match.group(2)), match.group(3)
        # Here you could add logic to actually implement the reminder
        return f"Reminder set: '{task}' in {duration} {unit}(s)."
    return "I couldn't understand your reminder request."

def get_story():
    """Tell a random story."""
    stories = [
        "Once upon a time, in a faraway land, there was a small village where everyone was happy. One day, a stranger came...",
        "Long ago, in a kingdom by the sea, there lived a brave knight who set out on an adventure to rescue a captive princess..."
    ]
    return random.choice(stories)

def set_timer(command):
    """Set a timer based on user command."""
    match = re.search(r'set timer for (\d+) (seconds?|minutes?|hours?)', command)
    if match:
        amount = int(match.group(1))
        unit = match.group(2)
        multiplier = {'seconds': 1, 'minutes': 60, 'hours': 3600}.get(unit[:-1], 1)  # Handle pluralization
        delay = amount * multiplier
        threading.Timer(delay, lambda: print(f"Timer for {amount} {unit} is up!")).start()
        return f"Setting a timer for {amount} {unit}(s)."
    return "Please specify the duration for the timer."

def set_reminder(command):
    """Set a reminder based on user command."""
    match = re.search(r'remind me to (.+) in (\d+) (minutes?|hours?)', command)
    if match:
        task, duration, unit = match.group(1), int(match.group(2)), match.group(3)
        multiplier = {'minutes': 60, 'hours': 3600}.get(unit, 1)
        delay = duration * multiplier
        threading.Timer(delay, lambda: print(f"Reminder: {task}")).start()
        return f"Reminder set: '{task}' in {duration} {unit}(s)."
    return "I couldn't understand your reminder request."


def open_application(command):
    """Open the requested application."""
    app_name = command.replace("open", "").strip().lower()
    apps = {
        "instagram": "https://www.instagram.com",
        "google": "https://www.google.com",
        "facebook": "https://www.facebook.com",
        "youtube": "https://www.youtube.com",
        "linkedin": "https://www.linkedin.com",
        "github": "https://www.github.com",
        "stackoverflow": "https://stackoverflow.com",
        "amazon": "https://www.amazon.com",
        "flipkart": "https://www.flipkart.com",
        "whatsapp": "https://web.whatsapp.com",
        "chrome": "chrome",
        "command prompt": "cmd",
        "powershell": "powershell",
        "visual studio code": "code",
        "zoom": "zoom"
    }
    if app_name in apps:
        app_path = apps[app_name]
        try:
            webbrowser.open(app_path)
            return f"Opening {app_name.capitalize()}."
        except Exception as e:
            logging.error(f"Error opening {app_name}: {e}")
            return f"Failed to open {app_name}."
    else:
        return f"I can't open '{app_name}'. Please check the application name."

# Flask routes
@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/voice-command', methods=['POST'])
def voice_command():
    """Process voice commands from the frontend."""
    try:
        data = request.get_json()
        command = data.get('command', '')
        response_text = handle_command(command)
        return jsonify({"response": response_text})
    except Exception as e:
        logging.error(f"Error processing voice command: {e}")
        return jsonify({"response": GENERAL_ERROR_MSG}), 500

if __name__ == '__main__':
    app.run(debug=True)
