import os
import sys
import time

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import speech_recognition
        import pyttsx3
        import requests
        import bs4
        import schedule
        import pywhatkit
        print("All dependencies are installed.")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install all required dependencies using:")
        print("pip install -r requirements.txt")
        return False

def main():
    """Main function to start the Echo Assistant"""
    print("\n" + "=" * 50)
    print("\tECHO AI - Personal Voice Assistant")
    print("=" * 50)
    
    # Check if dependencies are installed
    if not check_dependencies():
        return
    
    # Import the assistant after checking dependencies
    from echo_assistant import main as start_assistant
    
    print("\nStarting Echo AI Voice Assistant...")
    print("Say 'help' or 'what can you do' to see available commands.")
    print("Say 'exit' or 'goodbye' to quit the assistant.")
    print("\nInitializing...\n")
    
    # Small delay for better user experience
    time.sleep(1)
    
    # Start the assistant
    try:
        start_assistant()
    except KeyboardInterrupt:
        print("\nExiting Echo AI Voice Assistant...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your setup and try again.")

if __name__ == "__main__":
    main()