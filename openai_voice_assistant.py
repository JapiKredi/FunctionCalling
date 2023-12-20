# !pip install -q TTS
# !pip install -U numpy==1.21
# !pip install -q openai-whisper
# !pip install -q gradio
# !pip install -q openai

import whisper
import gradio as gr 
import openai
from TTS.api import TTS

from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


# TTS.list_models()

model_name = TTS.list_models()[9]
tts = TTS(model_name)

tts.tts_to_file(text="I love playing Chess", file_path="output.wav")

from IPython.display import Audio, display

display(Audio('output.wav', autoplay=True))

model = whisper.load_model("medium")

def voice_chat(user_voice):

    messages = [
    {"role": "system", "content": "You are a kind helpful assistant."},
    ]
          
    
    user_message = model.transcribe(user_voice)["text"]

    #reply = user_message

    messages.append(
        {"role": "user", "content": user_message},
    )

    print(messages)

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    
    reply = chat.choices[0].message.content
    
    messages.append({"role": "assistant", "content": reply})

    tts.tts_to_file(text=reply, file_path="output.wav")

    return(reply, 'output.wav')

text_reply = gr.Textbox(label="ChatGPT Text")
voice_reply = gr.Audio('output.wav')

gr.Interface(
    title = 'AI Voice Assistant with ChatGPT AI', 
    fn=voice_chat, 
    inputs=[
        gr.inputs.Audio(source="microphone", type="filepath")
    ],

    outputs=[
        text_reply,  voice_reply
    ], live = True).launch(debug = True)

