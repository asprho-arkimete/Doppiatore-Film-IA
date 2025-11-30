import argparse
import warnings
warnings.filterwarnings('ignore')
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from deep_translator import GoogleTranslator
import numpy as np
import librosa
from scipy.signal import find_peaks

# ===== ARGPARSE =====
parser = argparse.ArgumentParser(description='Trascrizione, traduzione e TTS multilingue')
parser.add_argument('--path_input', type=str, required=True, help='Percorso file audio input')
parser.add_argument('--output', type=str, default='output.wav', help='Percorso file audio output')
parser.add_argument('--lingua', type=str, default='spanish', help='Lingua audio originale (es: spanish, italian, english)')
parser.add_argument('--lingua_inp', type=str, default='es', help='Codice lingua input per traduzione (es: es, it, en)')
parser.add_argument('--lingua_trad', type=str, default='it', help='Codice lingua target per traduzione (es: it, en, es)')
parser.add_argument('--espressione', type=float, default=None, help='Exaggeration manuale (0.3-1.0), None=auto')
parser.add_argument('--cfg', type=float, default=None, help='CFG weight manuale (0.2-0.7), None=auto')
parser.add_argument('--battuta', type=str, default=None, help='passa il testo della battuta da tradurre e sintetizzare')

args = parser.parse_args()

# ===== PARAMETRI MANUALI (None = calcolo automatico) =====
exaggeration_manual = args.espressione  # Imposta un valore tra 0.3 - 1.0 per override manuale
cfg_weight_manual = args.cfg    # Imposta un valore tra 0.2 - 0.7 per override manuale

audio_path = args.path_input

battuta = ''
battuta = args.battuta

print("="*60)
print("ANALISI AUDIO ORIGINALE")
print("="*60)

# Carica l'audio con librosa
y, sr = librosa.load(audio_path, sr=None)

print(f"Sample rate: {sr} Hz")
print(f"Durata: {len(y)/sr:.2f} secondi")

# Variabili per parametri calcolati (solo se necessario)
intonazione = None
speech_rate = None

# ===== CALCOLA PARAMETRI SOLO SE NON IMPOSTATI MANUALMENTE =====
if exaggeration_manual is None or cfg_weight_manual is None:
    print("\n[CALCOLO AUTOMATICO PARAMETRI ABILITATO]")
    
    # ===== ANALISI FFT =====
    fft = np.fft.fft(y)
    magnitude = np.abs(fft)
    frequency = np.linspace(0, sr, len(magnitude))
    
    # Prendi solo metà dello spettro (simmetria FFT)
    half_length = len(frequency) // 2
    frequency = frequency[:half_length]
    magnitude = magnitude[:half_length]
    
    # ===== ESTRAZIONE PITCH (frequenza fondamentale) =====
    if exaggeration_manual is None:
        # Metodo 1: Trova il picco massimo nello spettro
        idx_max = np.argmax(magnitude)
        pitch_fft = frequency[idx_max]
        
        # Metodo 2: Usa librosa (più accurato per voce)
        pitches, magnitudes_pitch = librosa.piptrack(y=y, sr=sr)
        pitch_librosa = []
        
        for t in range(pitches.shape[1]):
            index = magnitudes_pitch[:, t].argmax()
            pitch_value = pitches[index, t]
            if pitch_value > 0:  # Ignora i frame silenziosi
                pitch_librosa.append(pitch_value)
        
        pitch_medio = np.mean(pitch_librosa) if pitch_librosa else 0
        
        print(f"\n[PITCH (TONO)]")
        print(f"Pitch da FFT: {pitch_fft:.2f} Hz")
        print(f"Pitch medio (librosa): {pitch_medio:.2f} Hz")
        
        # ===== ESTRAZIONE ARMONICHE =====
        peaks, properties = find_peaks(magnitude, height=np.max(magnitude)*0.1, distance=10)
        frequenze_armoniche = frequency[peaks]
        
        # Filtra solo le armoniche vicine a multipli della fondamentale
        fondamentale = pitch_medio if pitch_medio > 0 else pitch_fft
        armoniche = []
        
        for freq in frequenze_armoniche:
            # Controlla se è un multiplo della fondamentale (con tolleranza del 5%)
            rapporto = freq / fondamentale
            if abs(rapporto - round(rapporto)) < 0.05 and rapporto >= 1:
                armoniche.append(freq)
        
        n_armoniche = len(armoniche)
        
        print(f"\n[ARMONICHE]")
        print(f"Fondamentale: {fondamentale:.2f} Hz")
        print(f"Numero di armoniche trovate: {n_armoniche}")
        print(f"Armoniche: {[f'{a:.2f} Hz' for a in armoniche[:10]]}")  # Prime 10
        
        # ===== TIMBRO (Spectral Centroid) =====
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        timbro = np.mean(spectral_centroid)
        
        print(f"\n[TIMBRO]")
        print(f"Spectral Centroid (timbro): {timbro:.2f} Hz")
        print(f"(Più alto = voce più brillante, più basso = voce più scura)")
        
        # ===== INTONAZIONE =====
        freq_max = np.max(frequenze_armoniche) if len(frequenze_armoniche) > 0 else pitch_fft
        intonazione = n_armoniche / (freq_max / fondamentale) if freq_max > 0 else 0.5
        
        print(f"\n[INTONAZIONE]")
        print(f"Frequenza massima: {freq_max:.2f} Hz")
        print(f"Intonazione (n_armoniche / rapporto_freq): {intonazione:.4f}")
        print(f"(Più alto = più armoniche rispetto alla frequenza, suono più ricco)")
    
    # ===== CALCOLA SPEECH RATE =====
    if cfg_weight_manual is None:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        speech_rate = np.mean(onset_env)
        print(f"\n[SPEECH RATE]")
        print(f"Speech rate: {speech_rate:.4f}")
        print(f"(Più alto = parlata più veloce)")
else:
    print("\n[PARAMETRI MANUALI IMPOSTATI - SKIP ANALISI AUDIO]")

print("\n" + "="*60)
print("TRASCRIZIONE E TRADUZIONE")
print("="*60)

# Configurazione dispositivo
device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
testo_originale = ''

if not battuta:
    model_id = "openai/whisper-large-v3"

    print(f"\nCaricamento modello {model_id}...")
    print(f"Dispositivo: {device}")

    # Carica il modello Whisper
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    # Carica il processor
    processor = AutoProcessor.from_pretrained(model_id)

    # Crea la pipeline per la trascrizione
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
        generate_kwargs={
            "language": args.lingua,  # Lingua originale
            "task": "transcribe"
        }
    )

    # Trascrivi l'audio
    print("\nTrascrizione in corso...")
    result = pipe(
        audio_path, 
        return_timestamps=True,
        chunk_length_s=30,
        batch_size=16
    )

    testo_originale = result["text"]
else:
    testo_originale = battuta

print(f"\n[TRASCRIZIONE {args.lingua.upper()}]:")
print(testo_originale)

# Traduzione
traduzione_ita = None
if testo_originale and testo_originale.strip():
    print("\n[TRADUZIONE IN CORSO...]")
    
    translator = GoogleTranslator(source=args.lingua_inp, target=args.lingua_trad)
    traduzione_ita = translator.translate(testo_originale)
    
    print(f"\n[TRADUZIONE {args.lingua_trad.upper()}]:")
    print(traduzione_ita)
    print("\n[OK] Traduzione salvata in: traduzione.txt")
else:
    print(f"\n[ERRORE] Errore: testo {args.lingua} vuoto")

# Genera audio nella lingua tradotta con la voce clonata
if traduzione_ita is not None and traduzione_ita.strip():
    print("\n" + "="*60)
    print(f"GENERAZIONE AUDIO {args.lingua_trad.upper()}")
    print("="*60)
    
    print("\nCaricamento modello multilingue Chatterbox...")
    multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device='cuda')

    # ===== DETERMINA PARAMETRI FINALI =====
    print(f"\n[PARAMETRI TTS]")
    
    # Exaggeration
    if exaggeration_manual is not None:
        exaggeration = exaggeration_manual
        print(f"  Exaggeration: {exaggeration} [MANUALE]")
    else:
        # Mappa intonazione automaticamente
        intonazione_norm = np.clip(intonazione, 0.1, 2.0)
        exaggeration = 0.3 + (intonazione_norm - 0.1) / (2.0 - 0.1) * (1.0 - 0.3)
        print(f"  Intonazione originale: {intonazione:.4f}")
        print(f"  → Exaggeration: {exaggeration} [AUTO]")
    
    # cfg_weight
    if cfg_weight_manual is not None:
        cfg_weight = cfg_weight_manual
        print(f"  cfg_weight: {cfg_weight} [MANUALE]")
    else:
        # Mappa speech rate automaticamente
        speech_rate_norm = np.clip(speech_rate, 0.5, 3.0)
        cfg_weight = 0.7 - (speech_rate_norm - 0.5) / (3.0 - 0.5) * (0.7 - 0.2)
        cfg_weight = np.clip(cfg_weight, 0.2, 0.7)
        print(f"  Speech rate originale: {speech_rate:.4f}")
        print(f"  → cfg_weight: {cfg_weight} [AUTO]")
    
    # Mostra note solo se ci sono parametri automatici
    if exaggeration_manual is None or cfg_weight_manual is None:
        print(f"\n  Note mappatura automatica:")
        if cfg_weight_manual is None:
            print(f"  - Speech veloce → cfg_weight basso (evita accelerazione)")
            print(f"  - Speech lento → cfg_weight alto (mantiene fedeltà)")
        if exaggeration_manual is None:
            print(f"  - Intonazione alta → exaggeration alto (più espressivo)")
            print(f"  - Intonazione bassa → exaggeration basso (più calmo)")
    
    print("\nGenerazione audio in corso...")
    wav_ita = multilingual_model.generate(
        traduzione_ita,
        audio_prompt_path=audio_path,
        cfg_weight=cfg_weight,
        exaggeration=exaggeration,
        language_id=args.lingua_trad
    )
    
    output_filename = args.output
    ta.save(output_filename, wav_ita, multilingual_model.sr)
    
    print(f"\n[OK] Audio {args.lingua_trad} salvato in: {output_filename}")
else:
    print(f"\n[ERRORE] Errore: traduzione {args.lingua_trad} vuota")

print("\n" + "="*60)
print("COMPLETATO")
print("="*60)
if traduzione_ita:
    print(f"\nFile generati:")
    print(f"  1. traduzione.txt")
    print(f"  2. {args.output}")