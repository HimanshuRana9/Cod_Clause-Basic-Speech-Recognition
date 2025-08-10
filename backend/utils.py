import webbrowser, datetime, urllib.parse, pyttsx3

engine = None
def _init_tts():
    global engine
    if engine is None:
        try:
            engine = pyttsx3.init()
        except Exception:
            engine = None

def say(text):
    _init_tts()
    if engine:
        engine.say(text); engine.runAndWait()
    else:
        print('[TTS]', text)

def match_command(text):
    if not text: return None, None
    t = text.lower().strip()
    if 'youtube' in t:
        return 'open_youtube', t.replace('open youtube','').strip()
    if 'search' in t and 'google' in t:
        return 'search_google', t.replace('search google','').strip()
    if 'time' in t:
        now = datetime.datetime.now(); return 'time', now.strftime('%I:%M %p')
    if 'play' in t and 'music' in t:
        return 'play_music', ''
    if 'hello' in t or 'hi' in t:
        return 'greet', ''
    if 'exit' in t or 'quit' in t:
        return 'exit', ''
    return None, t

def handle_command(key, args):
    if not key: return False, 'no_command'
    if key == 'open_youtube':
        q = args or ''
        url = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote_plus(q)
        webbrowser.open(url); return True, url
    if key == 'search_google':
        q = args or ''
        url = 'https://www.google.com/search?q=' + urllib.parse.quote_plus(q)
        webbrowser.open(url); return True, url
    if key == 'time':
        return True, args
    if key == 'play_music':
        url = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote_plus('top hits')
        webbrowser.open(url); return True, url
    if key == 'greet':
        say('Hello! How can I help?'); return True, 'greeted'
    if key == 'exit':
        say('Exiting. Goodbye!'); return True, 'exit'
    return False, 'unknown'
