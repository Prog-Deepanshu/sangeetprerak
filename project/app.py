from flask import Flask, request, jsonify, render_template, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from audiocraft.models import musicgen
import torch
import numpy as np
from scipy.io.wavfile import write
from io import BytesIO
import threading
import time

app = Flask(__name__, static_folder='project/templates/static')
CORS(app, origins=["https://your-netlify-site.netlify.app"])  # Replace with your actual Netlify site URL
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Load pre-trained model
model = musicgen.MusicGen.get_pretrained('small', device='cuda')

@app.route('/')
def index():
    return render_template('index.html')

def generate_music_thread(prompts):
    try:
        # Set generation parameters before generating
        model.set_generation_params(duration=4)
        res = model.generate(prompts, progress=True)

        total_progress_steps = 5  # Define the number of progress updates
        for i in range(total_progress_steps):
            progress = (i + 1) * (100 // total_progress_steps)
            socketio.emit('progress', {'progress': progress})
            time.sleep(1)  # Sleep for 1 second between progress updates

        audio_data = res.detach().cpu().numpy()
        audio_data = np.int16(audio_data * 32767)  # Convert to 16-bit PCM format

        buffer = BytesIO()
        write(buffer, 48000, audio_data)  # Assuming a sample rate of 44100 Hz
        buffer.seek(0)

        socketio.emit('progress', {'progress': 100})

        return buffer
    except RuntimeError as e:
        socketio.emit('error', {'error': str(e)})
        return None

@app.route('/generate', methods=['POST'])
def generate_music():
    prompts = request.get_json()['prompts']
    buffer = generate_music_thread(prompts)
    if buffer:
        return send_file(buffer, mimetype='audio/wav', as_attachment=True, download_name='generated_music.wav')
    else:
        return jsonify({'error': 'Music generation failed'}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True)
