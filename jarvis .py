import os, webbrowser, datetime, threading, requests, psutil, asyncio, subprocess, math
import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext
import edge_tts
import pygame
import pyautogui

# ==========================================
# 1. CONFIGURATION & AI (अपनी Key यहाँ डालें)
# ==========================================
API_KEY = "apni_api_key_dale"
VOICE = "hi-IN-MadhurNeural" 
pygame.mixer.init()

# ==========================================
# 2. NEURAL VOICE ENGINE
# ==========================================
async def amain(text):
    temp_file = "jarvis_voice.mp3"
    communicate = edge_tts.Communicate(text, VOICE) 
    await communicate.save(temp_file)
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy(): pygame.time.Clock().tick(100)
    pygame.mixer.music.unload()
    try: os.remove(temp_file)
    except: pass

def speak(text):
    update_chat(text, "jarvis")
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(amain(text))
    except: pass

# ==========================================
# 3. ADVANCED UI - 6 ROTATING ARC REACTORS
# ==========================================
root = tk.Tk()
root.title("J.A.R.V.I.S - ARC CORE MAINFRAME 17.0")
root.geometry("1200x850")
root.configure(bg="black")

canvas = tk.Canvas(root, width=1200, height=550, bg="black", highlightthickness=0)
canvas.pack()

angles = [0, 0, 0, 0, 0, 0] # 6 रिएक्टर्स के लिए एंगल्स

def draw_reactors():
    canvas.delete("arc")
    
    # रिएक्टर्स की पोजीशन और डेटा
    # 1. Main Core (Big Center)
    draw_single_reactor(600, 250, 140, 0, "#00fbff", "CORE", angles[0])
    
    # 2. CPU Reactor
    cpu = psutil.cpu_percent()
    draw_single_reactor(250, 150, 80, 1, "#ff003c", f"CPU\n{cpu}%", angles[1])
    
    # 3. RAM Reactor
    ram = psutil.virtual_memory().percent
    draw_single_reactor(950, 150, 80, 2, "#ff8c00", f"RAM\n{ram}%", angles[2])
    
    # 4. DISK Reactor
    disk = psutil.disk_usage('/').percent
    draw_single_reactor(250, 400, 80, 3, "#00ff41", f"DISK\n{disk}%", angles[3])
    
    # 5. BATTERY Reactor
    bat = psutil.sensors_battery()
    bat_per = bat.percent if bat else 0
    draw_single_reactor(950, 400, 80, 4, "#ffff00", f"BATT\n{bat_per}%", angles[4])
    
    # 6. NETWORK Reactor
    draw_single_reactor(600, 460, 70, 5, "#bf00ff", "NET\nACTIVE", angles[5])

    # रोटेशन स्पीड सेट करना
    angles[0] += 2; angles[1] -= 4; angles[2] += 5
    angles[3] -= 3; angles[4] += 6; angles[5] += 8
    
    root.after(30, draw_reactors)

def draw_single_reactor(x, y, r, id, color, label, angle):
    # Outer Rotating Arcs
    canvas.create_arc(x-r, y-r, x+r, y+r, start=angle, extent=100, outline=color, width=3, style='arc', tags="arc")
    canvas.create_arc(x-r, y-r, x+r, y+r, start=angle+180, extent=100, outline=color, width=3, style='arc', tags="arc")
    # Inner Fixed Circles
    canvas.create_oval(x-(r-20), y-(r-20), x+(r-20), y+(r-20), outline=color, width=1, tags="arc")
    # Center Text
    canvas.create_text(x, y, text=label, fill="white", font=("Consolas", 12, "bold"), justify="center", tags="arc")

# Chat & Input Layout
bottom_frame = tk.Frame(root, bg="black")
bottom_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

chat_box = scrolledtext.ScrolledText(bottom_frame, bg="#050505", fg="#00fbff", font=("Consolas", 10), height=8)
chat_box.pack(fill=tk.X)

entry_box = tk.Entry(root, bg="#111111", fg="white", font=("Consolas", 14), insertbackground="#00fbff")
entry_box.pack(fill=tk.X, padx=20, pady=10)

def update_chat(msg, sender):
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, f"\n[{sender.upper()}]: {msg}\n")
    chat_box.see(tk.END); chat_box.config(state=tk.DISABLED)

# ==========================================
# 4. UNIVERSAL LOGIC (Apps & Mic Fix)
# ==========================================
def open_app(app_name):
    app_name = app_name.lower().replace("open", "").replace("jarvis", "").strip()
    special_cases = {"whatsapp": "start whatsapp:", "chrome": "start chrome", "calculator": "calc"}
    speak(f"ठीक है सर, {app_name} खोल रहा हूँ।")
    if app_name in special_cases:
        os.system(special_cases[app_name])
    else:
        try: subprocess.run(f"start {app_name}", shell=True)
        except: speak("सिस्टम में यह ऐप नहीं मिला।")

def process(query):
    if query == "none": return
    update_chat(query, "boss")
    
    if "open" in query or "खोल" in query:
        open_app(query)
    elif "shutdown" in query:
        speak("शटडाउन सीक्वेंस शुरू।")
        os.system("shutdown /s /t 5")
    elif "stop" in query or "exit" in query:
        speak("Goodbye Boss."); root.after(500, root.destroy)
    else:
        # AI Response
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"You are JARVIS. Boss: Ankit Nishad. Short Hinglish: {query}"}]}]}
        try:
            res = requests.post(url, json=payload, timeout=10).json()
            ans = res['candidates'][0]['content']['parts'][0]['text']
            speak(ans)
        except: speak("AI ब्रेन से संपर्क नहीं हो पा रहा।")

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.energy_threshold = 100 
        r.dynamic_energy_threshold = True
        r.adjust_for_ambient_noise(source, duration=0.6)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            return r.recognize_google(audio, language='en-in').lower()
        except: return "none"

def on_enter(event):
    msg = entry_box.get(); entry_box.delete(0, tk.END)
    threading.Thread(target=process, args=(msg,), daemon=True).start()

entry_box.bind("<Return>", on_enter)

def main_loop():
    draw_reactors()
    speak("Master Mainframe online. All six reactors are stabilized. Hello Boss Ankit.")
    while True:
        cmd = take_command()
        if cmd != "none": process(cmd)

threading.Thread(target=main_loop, daemon=True).start()
root.mainloop()