# ECHO AI - Personal Voice Assistant

ECHO AI is a Python-based personal voice assistant that can perform various tasks through voice commands. It's designed to help you control your computer, search the web, manage reminders, and more.

## Features

- **Voice Recognition**: Listens to your commands and converts speech to text
- **Text-to-Speech**: Responds verbally to your queries
- **Application Control**: Opens applications on your PC
- **Web Search**: Searches Google, Bing, or YouTube and reads results
- **System Settings**: Controls volume and WiFi settings
- **Reminders & Alarms**: Sets reminders and alarms
- **Time & Date**: Provides current time and date information

## Requirements

- Python 3.x
- Required Python packages (see requirements.txt)
- Microphone for voice input
- Speakers for voice output

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

Run the assistant by executing the main.py file:

```
python main.py
```

Once the assistant is running, you can interact with it using voice commands. Say "help" or "what can you do" to see a list of available commands.

### Example Commands

- "What time is it?"
- "Open Notepad"
- "Search for weather in New York"
- "Turn WiFi off"
- "Set a reminder"
- "Set an alarm"

## Extending Functionality

The assistant is designed with a modular structure, making it easy to add new features. To add a new command, modify the `process_command` method in the `EchoAssistant` class.

## Troubleshooting

- **Microphone not detected**: Ensure your microphone is properly connected and set as the default recording device
- **Speech not recognized**: Speak clearly and ensure you're in a quiet environment
- **Dependencies missing**: Run `pip install -r requirements.txt` to install all required packages

## Future Enhancements

- Integration with smart home devices
- Mobile device control
- Email and messaging capabilities
- Calendar integration
- Weather forecasts
- News updates

## License

This project is open source and available under the MIT License.