from pedalboard import Pedalboard, Gain, HighShelfFilter, LowShelfFilter
import soundfile as sf
import librosa
import random
import gradio as gr

def load_audio(input_path):
    """Load audio file and return audio data and sample rate"""
    y, sr = sf.read(input_path)
    return y, sr

def apply_pitch(y, sr, semitones):
    """Apply pitch shifting to audio"""
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)

def apply_eq_amp(y, sr, gain_db=3, low_shelf_db=5, low_cutoff=200, high_shelf_db=-3, high_cutoff=5000):
    """Apply EQ and amplification to audio"""
    board = Pedalboard([
        Gain(gain_db=gain_db),
        LowShelfFilter(cutoff_frequency_hz=low_cutoff, gain_db=low_shelf_db),
        HighShelfFilter(cutoff_frequency_hz=high_cutoff, gain_db=high_shelf_db),
    ])
    return board(y, sr)

def process_voice(audio_file, semitones_text, gain_db, low_shelf_db, low_cutoff, high_shelf_db, high_cutoff):
    """Process voice with pitch shifting and EQ"""
    if audio_file is None:
        return None, "Please upload an audio file"
    
    try:
        # Parse semitones from text input
        semitone_list = []
        if semitones_text.strip():
            semitone_list = [float(x.strip()) for x in semitones_text.split(',')]
        else:
            semitone_list = [0]  # Default to no pitch shift
        
        # Load audio
        y, sr = load_audio(audio_file)
        
        # Process with the first semitone value for the interface
        # (you can modify this to handle multiple values differently)
        semitones = semitone_list[0] if semitone_list else 0
        
        # Apply pitch shifting
        y_shifted = apply_pitch(y, sr, semitones)
        
        # Apply EQ and amplification
        y_final = apply_eq_amp(y_shifted, sr, gain_db, low_shelf_db, low_cutoff, high_shelf_db, high_cutoff)
        
        # Create output filename
        output_file = f"processed_voice_{random.randint(1000, 9999)}.wav"
        
        # Write processed audio
        sf.write(output_file, y_final, sr)
        
        return output_file, f"✅ Processed successfully with {semitones} semitones"
        
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

def batch_process(audio_file, semitones_text):
    """Process voice with multiple semitone values and save separate files"""
    if audio_file is None:
        return "Please upload an audio file"
    
    try:
        # Parse semitones from text input
        semitone_list = [float(x.strip()) for x in semitones_text.split(',')]
        
        # Load audio
        y, sr = load_audio(audio_file)
        
        results = []
        for semitones in semitone_list:
            # Random filename
            out_file = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10)) + '.wav'
            y_shifted = apply_pitch(y, sr, semitones)
            y_final = apply_eq_amp(y_shifted, sr)
            sf.write(out_file, y_final, sr)
            results.append(f"✅ Saved: {out_file} (semitones={semitones})")
        
        return "\n".join(results)
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="Voice Changer") as demo:
    gr.Markdown("# 🎵 Voice Changer Tool")
    gr.Markdown("Upload an audio file and adjust parameters to change the voice characteristics.")
    
    with gr.Tab("Single Process"):
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    label="Upload Audio File",
                    type="filepath"
                )
                semitones_input = gr.Textbox(
                    label="Semitones (comma-separated for multiple values)",
                    placeholder="e.g., -5, 0, 5",
                    value="0"
                )
                
                with gr.Accordion("EQ Settings", open=False):
                    gain_db = gr.Slider(
                        minimum=-20, maximum=20, value=3, step=0.5,
                        label="Gain (dB)"
                    )
                    low_shelf_db = gr.Slider(
                        minimum=-20, maximum=20, value=5, step=0.5,
                        label="Low Shelf Gain (dB)"
                    )
                    low_cutoff = gr.Slider(
                        minimum=50, maximum=500, value=200, step=10,
                        label="Low Cutoff Frequency (Hz)"
                    )
                    high_shelf_db = gr.Slider(
                        minimum=-20, maximum=20, value=-3, step=0.5,
                        label="High Shelf Gain (dB)"
                    )
                    high_cutoff = gr.Slider(
                        minimum=2000, maximum=10000, value=5000, step=100,
                        label="High Cutoff Frequency (Hz)"
                    )
                
                process_btn = gr.Button("Process Voice", variant="primary")
            
            with gr.Column():
                audio_output = gr.Audio(label="Processed Audio")
                status_output = gr.Textbox(label="Status", interactive=False)
        
        process_btn.click(
            fn=process_voice,
            inputs=[audio_input, semitones_input, gain_db, low_shelf_db, low_cutoff, high_shelf_db, high_cutoff],
            outputs=[audio_output, status_output]
        )
    
    with gr.Tab("Batch Process"):
        with gr.Row():
            with gr.Column():
                batch_audio_input = gr.Audio(
                    label="Upload Audio File",
                    type="filepath"
                )
                batch_semitones_input = gr.Textbox(
                    label="Semitones (comma-separated)",
                    placeholder="e.g., -5, -2, 0, 2, 5",
                    value="-5, 0, 5"
                )
                batch_process_btn = gr.Button("Batch Process", variant="primary")
            
            with gr.Column():
                batch_status_output = gr.Textbox(
                    label="Batch Process Results",
                    interactive=False,
                    lines=10
                )
        
        batch_process_btn.click(
            fn=batch_process,
            inputs=[batch_audio_input, batch_semitones_input],
            outputs=[batch_status_output]
        )

if __name__ == "__main__":
    demo.launch(share=True)