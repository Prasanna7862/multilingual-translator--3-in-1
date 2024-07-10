import tkinter as tk
from tkinter import filedialog, Entry, Label, Text, Button, ttk
from PIL import Image, ImageTk
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
import requests
from io import BytesIO
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from gtts import gTTS
import os
import pygame
import tempfile
import spacy
import webbrowser

# Supported languages for translation
supported_languages = {
    'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy', 'Azerbaijani': 'az',
    'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn', 'Bosnian': 'bs', 'Bulgarian': 'bg', 'Catalan': 'ca',
    'Cebuano': 'ceb', 'Chichewa': 'ny', 'Chinese (Simplified)': 'zh-cn', 'Chinese (Traditional)': 'zh-tw',
    'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs', 'Danish': 'da', 'Dutch': 'nl', 'English': 'en',
    'Esperanto': 'eo', 'Estonian': 'et', 'Filipino': 'tl', 'Finnish': 'fi', 'French': 'fr', 'Frisian': 'fy',
    'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el', 'Gujarati': 'gu', 'Haitian Creole': 'ht',
    'Hausa': 'ha', 'Hawaiian': 'haw', 'Hebrew': 'iw', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu',
    'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it', 'Japanese': 'ja',
    'Javanese': 'jw', 'Kannada': 'kn', 'Kazakh': 'kk', 'Khmer': 'km', 'Kinyarwanda': 'rw', 'Korean': 'ko',
    'Kurdish': 'ku', 'Kyrgyz': 'ky', 'Lao': 'lo', 'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt',
    'Luxembourgish': 'lb', 'Macedonian': 'mk', 'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt',
    'Maori': 'mi', 'Marathi': 'mr', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne', 'Norwegian': 'no',
    'Odia (Oriya)': 'or', 'Pashto': 'ps', 'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt', 'Punjabi': 'pa',
    'Romanian': 'ro', 'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd', 'Serbian': 'sr', 'Sesotho': 'st',
    'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala': 'si', 'Slovak': 'sk', 'Slovenian': 'sl', 'Somali': 'so', 'Spanish': 'es',
    'Sundanese': 'su', 'Swahili': 'sw', 'Swedish': 'sv', 'Tajik': 'tg', 'Tamil': 'ta', 'Tatar': 'tt', 'Telugu': 'te',
    'Thai': 'th', 'Turkish': 'tr', 'Turkmen': 'tk', 'Ukrainian': 'uk', 'Urdu': 'ur', 'Uyghur': 'ug', 'Uzbek': 'uz',
    'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh', 'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'
}

# Load spaCy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Load pre-trained model and tokenizer for image processing
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
feature_extractor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Move model to CUDA if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Set up decoding parameters
max_length = 16
num_beams = 4
gen_kwargs = {"max_length": max_length, "num_beams": num_beams}

def predict_step(image):
    if image.mode != "RGB":
        image = image.convert(mode="RGB")

    # Extract pixel values and move to CUDA
    pixel_values = feature_extractor(images=[image], return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)

    # Generate captions
    output_ids = model.generate(pixel_values, **gen_kwargs)

    # Decode and clean up the predictions
    preds = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    preds = [pred.strip() for pred in preds]
    return preds

def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        image = Image.open(file_path)
        result = predict_step(image)
        result_label.config(text="\n".join(result))
        display_image(image)

def open_online_image():
    url = online_url_entry.get()
    if url:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                result = predict_step(image)
                result_label.config(text="\n".join(result))
                display_image(image)
            else:
                result_label.config(text=f"Error: Unable to fetch image. HTTP Status Code: {response.status_code}")
        except Exception as e:
            result_label.config(text=f"Error: {str(e)}")

def display_image(image):
    image = image.resize((300, 300))  # Adjust the size as needed
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo

def translate():
    translator = Translator()
    translated = translator.translate(text=InputText.get(), dest=supported_languages[dest_lang_code.get()])
    OutputText.delete(1.0, "end")
    OutputText.insert("end", translated.text)

def upload_audio_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio files", "*.wav;*.mp3")])
    if file_path:
        with sr.AudioFile(file_path) as source:
            recognizer = sr.Recognizer()
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        InputText.delete(0, "end")
        InputText.insert(0, text)

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak something...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        InputText.delete(0, "end")
        InputText.insert(0, text)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print(f"Error with the request to Google Speech Recognition service; {e}")

def text_to_speech():
    text = OutputText.get("1.0", "end-1c")
    
    # Print the retrieved text for debugging
    print("Text for text-to-speech:", repr(text))

    # Check if there is text available
    if text.strip():
        lang_code = supported_languages[dest_lang_code.get()]

        # Check if the selected language is supported by gTTS, if not, use English as the default
        supported_languagesk = ['af', 'sq', 'am', 'ar', 'hy', 'az', 'eu', 'be', 'bn', 'bs', 'bg', 'ca', 'ceb', 'ny',
                                'zh-cn', 'co', 'hr', 'cs', 'da', 'nl', 'eo', 'et', 'tl', 'fi', 'fr', 'fy', 'gl', 'kn',
                                'de', 'el', 'gu', 'ht', 'ha', 'haw', 'iw', 'hi', 'hmn', 'hu', 'is', 'ig', 'id', 'ga',
                                'it', 'ja', 'jw', 'kn', 'kk', 'km', 'rw', 'ko', 'ku', 'ky', 'lo', 'la', 'lv', 'lt', 'lb',
                                'mk', 'mg', 'ms', 'ml', 'mt', 'mi', 'mr', 'mn', 'my', 'ne', 'no', 'or', 'ps', 'fa', 'pl',
                                'pt', 'pa', 'ro', 'ru', 'sm', 'gd', 'sr', 'st', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'es',
                                'su', 'sw', 'sv', 'tg', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'ug', 'uz', 'vi', 'cy', 'xh',
                                'yi', 'yo', 'zu']

        if lang_code not in supported_languagesk:
            lang_code = 'en'

        tts = gTTS(text=text, lang=lang_code)

        # Use a temporary file to avoid permission issues
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
            temp_audio_path = temp_audio.name
            tts.save(temp_audio_path)

        pygame.mixer.init()
        pygame.mixer.music.load(temp_audio_path)
        pygame.mixer.music.play()

        # Remove the temporary file after playing
        os.remove(temp_audio_path)
    else:
        print("No text available for text-to-speech conversion.")

def perform_nlp_analysis():
    text = OutputText.get("1.0", "end-1c")
    if text.strip():
        doc = nlp(text)

        # Extract dependency relationships with full names
        dependency_relations = [(token.text, token.dep_, spacy.explain(token.dep_)) for token in doc]

        # Print the dependency relationships
        print("Dependency Relationships:", dependency_relations)

        # Update the DependencyText widget
        DependencyText.delete(1.0, "end")
        DependencyText.insert("end", "\n".join([f"{token}: {full_name}" for token, _, full_name in dependency_relations]))
    else:
        print("No text available for NLP analysis.")

def translate_and_speak():
    if InputText.get():  # Check if there is text in the Entry widget
        translate()
        text_to_speech()
        perform_nlp_analysis()
    else:
        print("Please enter text or upload an audio file.")

class VoiceAssistantGUI:
    def __init__(self, master):
        self.master = master
        master.title("Voice Assistant")

        # Center the GUI on the screen
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        window_width = 700
        window_height = 300
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        master.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Apply a colorful background
        master.configure(bg="#3498db")  # You can change the color code as needed

        self.label = tk.Label(master, text="Press the button and speak:", bg="#3498db", fg="white", font=("Helvetica", 14))
        self.label.pack()

        self.query_var = tk.StringVar()
        self.query_var.set("")

        # Style for the buttons
        style = ttk.Style()
        style.configure('TButton', font=("Helvetica", 12))

        self.recognize_button = ttk.Button(master, text="Speak", command=self.recognize_and_search)
        self.recognize_button.pack(pady=10)

        self.exit_button = ttk.Button(master, text="Exit", command=master.destroy)
        self.exit_button.pack()

        self.result_label = tk.Label(master, textvariable=self.query_var, bg="#3498db", fg="white", font=("Helvetica", 12))
        self.result_label.pack()

    def recognize_and_search(self):
        user_input = recognize_speech()
        if user_input:
            if "exit" in user_input.lower():
                print("Exiting...")
                self.master.destroy()
            else:
                search_google(user_input)
                self.query_var.set(f"Recognized: {user_input}")

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=1)

    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio)
        print(f"You said: {query}")
        return query
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Error making the request; {e}")
        return None

def search_google(query):
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open(search_url)

if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()
    root.geometry("1000x1000")
    root.iconbitmap(r"C:/Users/ARK/Downloads/HAIR STYLE.jpg")
    root.config(bg='skyblue')
    root.title('Language Translator with NLP and Image Processing')

    # Title
    Label(root, text="Language Translator", font="Arial 20 bold", bg='skyblue').pack(pady=10)

    # Left Side (Language Translator)
    translator_frame = tk.Frame(root, bg='skyblue')
    translator_frame.pack(side=tk.LEFT, padx=20, pady=20)

    # Input Text Entry
    Label(translator_frame, text="Enter Text", font="arial 13 bold", bg='skyblue').pack()
    InputText = Entry(translator_frame, width=40, font="arial 12")
    InputText.pack()


    # Language Selection
    Label(translator_frame, text="Select Language", font="arial 13 bold", bg='skyblue').pack()
    dest_lang_code = tk.StringVar()
    dest_lang_code.set('en')  # Default language is English
    dest_lang_menu = ttk.Combobox(translator_frame, textvariable=dest_lang_code, values=list(supported_languages.keys()))
    dest_lang_menu.pack()

    # Output Text
    Label(translator_frame, text="Translated Text", font="arial 13 bold", bg='skyblue').pack()
    OutputText = Text(translator_frame, height=6, width=40, font="arial 12")
    OutputText.pack()

    # Translate Button
    translate_button = Button(translator_frame, text="Translate", command=translate_and_speak, font="arial 12 bold", bg='white')
    translate_button.pack(pady=10)

    # Upload Audio File Button
    upload_button = Button(translator_frame, text="Upload Audio File", command=upload_audio_file, font="arial 12 bold", bg='white')
    upload_button.pack(pady=10)

    # Speech to Text Button
    speech_to_text_button = Button(translator_frame, text="Speech to Text", command=speech_to_text, font="arial 12 bold", bg='white')
    speech_to_text_button.pack(pady=10)
    text_to_speech_button = Button(translator_frame, text="text to Speech", command=text_to_speech, font="arial 12 bold", bg='white')
    text_to_speech_button.pack(pady=10)
    nlp_button = Button(translator_frame, text="Perform NLP Analysis", command=perform_nlp_analysis, font="arial 12 bold", bg='white')
    nlp_button.pack(pady=10)
    # NLP Dependency Analysis Text
    Label(translator_frame, text="NLP Dependency Analysis", font="arial 13 bold", bg='skyblue').pack()
    DependencyText = Text(translator_frame, height=6, width=40, font="arial 12")
    DependencyText.pack()

    # Right Side (Image Processing)
    image_frame = tk.Frame(root, bg='skyblue')
    image_frame.pack(side=tk.RIGHT, padx=20, pady=20)

    # Image Display Label
    image_label = Label(image_frame, bg='white')
    image_label.pack()

    # Open Image Button
    open_image_button = Button(image_frame, text="Open Image", command=open_image, font="arial 12 bold", bg='white')
    open_image_button.pack(pady=10)

    # Open Online Image Entry
    Label(image_frame, text="Open Online Image", font="arial 13 bold", bg='skyblue').pack()
    online_url_entry = Entry(image_frame, width=40, font="arial 12")
    online_url_entry.pack()

    # Open Online Image Button
    open_online_image_button = Button(image_frame, text="Open Online Image", command=open_online_image, font="arial 12 bold", bg='white')
    open_online_image_button.pack(pady=10)

    # Image Processing Result Label
    result_label = Label(image_frame, text="", font="arial 12 bold", bg='white')
    result_label.pack()

    # Create Voice Assistant GUI
    voice_assistant_gui = VoiceAssistantGUI(root)

    # Run the main loop
    root.mainloop()
