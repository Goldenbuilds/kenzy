import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import winsound
import sys


app = Flask(__name__)

# Set up Spotipy with your Spotify API credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='f2533b00a91d4edeab4f300efd021411',
    client_secret='c232de093d4e404896d2704cea82f80c',
    redirect_uri='http://localhost:8888/callback',
    scope='user-modify-playback-state user-read-playback-state'
))



try:
    import winsound
except ImportError:
    from playsound import playsound

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/command', methods=['POST'])
def handle_command():
    """Handle voice commands for Spotify."""
    data = request.get_json()
    command = data.get('command', '').lower()

    if not command:
        return jsonify({'status': 'error', 'message': 'No command received.'}), 400

    # Process command
    response = process_command(command)
    return jsonify({'message': response})


def process_command(command):
    """Process the received command and interact with Spotify."""
    try:
        # Handle playlist-specific commands
        if "play" in command:
            return play_music(command)

        # Handle volume and playback controls
        if "change the song" in command:
            sp.next_track()
            return "Changing the song!"

        if "volume" in command:
            return adjust_volume(command)

        if "pause" in command:
            sp.pause_playback()
            return "Music paused."

        if "resume" in command or "play the music" in command:
            sp.start_playback()
            return "Resuming music!"

        if "mute" in command:
            sp.volume(0)
            return "Music muted."

        if "unmute" in command:
            sp.volume(50)  # Default unmute volume
            return "Unmuted and volume set to 50%."

        return "I didn't understand that command. Please try again."
    except Exception as e:
        return f"An error occurred: {e}"


def play_music(command):
    """Handle commands to play music on Spotify."""
    keywords = {
        "exciting": ["exciting", "hype", "lively", "energetic", "pump me up"],
        "focus": ["focus", "study", "work", "chill", "productive"],
        "nigerian": ["gbedu", "jam", "banger", "as e be"]
    }

    # Match command to a category
    for category, terms in keywords.items():
        if any(term in command for term in terms):
            return search_and_play(category)

    # Handle specific song/artist requests
    if "play" in command:
        song_or_artist = command.split("play", 1)[1].strip()
        return search_and_play(song_or_artist, is_custom=True)

    return "Sorry, I couldn't find a suitable playlist or song."


def search_and_play(query, is_custom=False):
    """Search and play a Spotify playlist or track."""
    try:
        if is_custom:
            results = sp.search(q=query, type='track', limit=1)
            if results['tracks']['items']:
                sp.start_playback(uris=[results['tracks']['items'][0]['uri']])
                return f"Playing: {query}"
        else:
            results = sp.search(q=f'{query} playlist', type='playlist', limit=1)
            if results['playlists']['items']:
                sp.start_playback(context_uri=results['playlists']['items'][0]['uri'])
                return f"Playing {query} playlist!"
    except Exception as e:
        return f"An error occurred: {e}"

    return f"No results found for {query}."


def adjust_volume(command):
    """Increase or decrease the volume."""
    playback = sp.current_playback()
    if not playback or 'device' not in playback:
        return "No active device found. Please play music on Spotify first."

    current_volume = playback['device']['volume_percent']
    if "increase" in command:
        new_volume = min(current_volume + 10, 100)
        sp.volume(new_volume)
        return f"Increased volume to {new_volume}%."

    if "decrease" in command:
        new_volume = max(current_volume - 10, 0)
        sp.volume(new_volume)
        return f"Decreased volume to {new_volume}%."


def say(text):
    """Speak the given text."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def play_sound(frequency, duration):
    """Play a beep sound."""
    winsound.Beep(frequency, duration)


if __name__ == '__main__':
    app.run(debug=True)
