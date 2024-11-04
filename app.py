import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, request, jsonify # type: ignore
import speech_recognition as sr # type: ignore
import requests
import os
import winsound 
import pyttsx3

app = Flask(__name__)

# Set up Spotipy with your Spotify API credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='f2533b00a91d4edeab4f300efd021411',
    client_secret='c232de093d4e404896d2704cea82f80c',
    redirect_uri='http://localhost:8888/callback',
    scope='user-modify-playback-state user-read-playback-state'
))


@app.route('/')
def home():
    return render_template('index.html') 

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    command = data.get('command').lower()

    # Logic to handle the command, e.g., play music, pause, etc.
    if command:
        # Process the command to play music
        if "play" in command:
            return play_music(command)  # Call the play_music function with the command
        else:
            return jsonify({'status': 'error', 'message': 'Invalid command.'}), 400
    else:
        return jsonify({'status': 'error', 'message': 'No command received.'}), 400
    

def listen():  
    recognizer = sr.Recognizer() 
    with sr.Microphone() as source: #captures audio from mic
        recognizer.adjust_for_ambient_noise(source, duration= 1)
        play_sound(300,500)
        audio = recognizer.listen(source) #listens to the audio input from the mic and stores it in the audio variable

    return audio 

def recognize(audio):
    recognizer = sr.Recognizer()

    try:
        text = recognizer.recognize_google(audio)
        print("Recognized Text:", text)  # Added this line for debugging
        return text
        
    except sr.UnknownValueError:
        return ""
    
    
def say(text): 
    engine = pyttsx3.init(driverName='sapi5')
    engine.say(text)
    engine.runAndWait()

def play_sound(sound_freq, duration): 
    winsound.Beep(sound_freq, duration)
         

@app.route('/play', methods=['POST'])
def play_music(command):
    """Handle the voice command to play music on Spotify."""
    
    # Exciting playlists
    exciting_keywords = ["exciting", "hype", "vibrant", "lively", "energetic", "jolly", "fun", "pump me up", "get me hyped", "make me happy", "fire me up", "let's go"]

    # Focus playlists
    focus_keywords = ["focus", "concentrate", "study", "work", "serious", "calm", "chill", "deep work", "stay on task", "productive", "make me focus", "silent vibes"]

    # Additional Nigerian terms
    nigerian_keywords = ["gbedu", "jam", "jazz", "no wahala", "chop", "banger", "as e be"]

    # Default message
    final_message = "Sorry, I couldn't find a suitable playlist for your request."
    
    # Check for active device
    devices = sp.devices()
    if not devices['devices']:
        return jsonify({"message": "Please open the Spotify app on a device and start playing a song."})

    # Initialize a variable to hold the found playlist or song URI
    playlist_uri = None

    # Check for commands
    if "play" in command:
        # Existing logic to play a song or playlist
        final_message = handle_play_command(command)

    elif "change the song" in command:
        sp.next_track()  # Skip to the next track
        final_message = "Changing the song!"

    elif "increase the volume" in command:
        current_volume = sp.current_playback()['device']['volume_percent']
        new_volume = min(current_volume + 10, 100)  # Increase volume by 10%, max 100%
        sp.volume(new_volume)  # Set new volume
        final_message = f"Increasing volume to {new_volume}%."

    elif "decrease the volume" in command:
        current_volume = sp.current_playback()['device']['volume_percent']
        new_volume = max(current_volume - 10, 0)  # Decrease volume by 10%, min 0%
        sp.volume(new_volume)  # Set new volume
        final_message = f"Decreasing volume to {new_volume}%."

    elif "pause the music" in command:
        sp.pause_playback()  # Pause the currently playing track
        final_message = "Music paused."

    elif "resume the music" in command or "play the music" in command:
        sp.start_playback()  # Resume playback
        final_message = "Resuming music!"

    elif "mute" in command:
        sp.volume(0)  # Mute the volume
        final_message = "Music muted."

    elif "unmute" in command:
        current_volume = sp.current_playback()['device']['volume_percent']
        new_volume = max(current_volume + 10, 100)  # Unmute to a default volume level
        sp.volume(new_volume)  # Set new volume
        final_message = f"Unmuted. Volume set to {new_volume}%."

    else:
        final_message = "I didn't understand that command. Please try again."

    # Log the final message to provide feedback and speak it
    print(final_message)
    say(final_message)

    # Return a JSON response
    return jsonify({"message": final_message})

def handle_play_command(command):
    """Handle the logic to play a song or playlist based on the command."""
    
    # Use the existing playlist and song logic from your previous code
    exciting_keywords = ["exciting", "hype", "vibrant", "lively", "energetic", "jolly", "fun", "pump me up", "get me hyped", "make me happy", "fire me up", "let's go"]
    focus_keywords = ["focus", "concentrate", "study", "work", "serious", "calm", "chill", "deep work", "stay on task", "productive", "make me focus", "silent vibes"]
    nigerian_keywords = ["gbedu", "jam", "jazz", "no wahala", "chop", "banger", "as e be"]

    # Initialize a variable to hold the found playlist or song URI
    playlist_uri = None
    final_message = "Sorry, I couldn't find a suitable playlist for your request."

    # Check for exciting playlist
    if any(keyword in command for keyword in exciting_keywords):
        results = sp.search(q='exciting playlist', type='playlist', limit=1)
        if results['playlists']['items']:
            playlist_uri = results['playlists']['items'][0]['uri']
            final_message = "Playing your exciting playlist! Enjoy!"

    # Check for focus playlist
    elif any(keyword in command for keyword in focus_keywords):
        results = sp.search(q='focus playlist', type='playlist', limit=1)
        if results['playlists']['items']:
            playlist_uri = results['playlists']['items'][0]['uri']
            final_message = "Playing your focus playlist! Let's get to work!"

    # Check for Nigerian terms
    elif any(keyword in command for keyword in nigerian_keywords):
        results = sp.search(q='Nigerian playlist', type='playlist', limit=1)
        if results['playlists']['items']:
            playlist_uri = results['playlists']['items'][0]['uri']
            final_message = "Playing some sweet gbedu! Enjoy!"

    # If a playlist was found, start playback
    if playlist_uri:
        sp.start_playback(context_uri=playlist_uri)
    
    # Handle specific artist or song requests
    else:
        if "play" in command:
            parts = command.split("play", 1)[1].strip()  # Get everything after the word "play"
            song_title = None
            artist_name = None

            # Logic to identify if a song title and artist are mentioned
            if "by" in parts:
                song_title, artist_name = map(str.strip, parts.rsplit("by", 1))
            else:
                song_title = parts  # No artist mentioned, assume it's just a song title

            # Search for the song or artist
            if artist_name:
                results = sp.search(q=f'track:{song_title} artist:{artist_name}', type='track', limit=1)
                if results['tracks']['items']:
                    sp.start_playback(uris=[results['tracks']['items'][0]['uri']])
                    final_message = f"Playing '{song_title}' by {artist_name}!"
                else:
                    results = sp.search(q=f'artist:{artist_name}', type='track', limit=1)
                    if results['tracks']['items']:
                        sp.start_playback(uris=[results['tracks']['items'][0]['uri']])
                        final_message = f"Playing a song by {artist_name}!"
                    else:
                        final_message = f"Sorry, I couldn't find any songs by {artist_name}."
            else:
                results = sp.search(q=f'track:{song_title}', type='track', limit=1)
                if results['tracks']['items']:
                    sp.start_playback(uris=[results['tracks']['items'][0]['uri']])
                    final_message = f"Playing '{song_title}'!"
    
    return final_message
    
if __name__ == '__main__':
    app.run(debug=True)

