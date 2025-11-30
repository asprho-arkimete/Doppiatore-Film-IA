from optparse import Values
import shutil
import tkinter as tk
from tkinter import NO, YES, Message, filedialog
import webbrowser


window = tk.Tk()
window.title("Traduttore")
window.geometry("900x720")

barr = tk.Toplevel(window)  # Usa Toplevel invece di un secondo Tk()
barr.title("Progress")
barr.geometry("1000x100")

def close_windows():
     try:
         if barr.winfo_exists():
             barr.destroy()
     except:
         pass
     window.destroy()
 
window.protocol("WM_DELETE_WINDOW", close_windows)


path_file = None

# Bottone per aprire il sito
opensite = tk.Button(text="1> Scarica video Da: Clipto", command=lambda: webbrowser.open("https://www.clipto.com/it/media-downloader/youtube-downloader"))
opensite.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# Label per istruzioni trascrizione
lab1 = tk.Label(text="2> Inserisci Trascrizione video Youtube")
lab1.grid(row=1, column=0, padx=10, pady=5, sticky="w")

# Frame per contenere Text e Scrollbar
frame_text = tk.Frame(window)
frame_text.grid(row=2, column=0, padx=10, pady=5)

# Scrollbar verticale
scrollbar_v = tk.Scrollbar(frame_text, orient="vertical")
scrollbar_v.pack(side="right", fill="y")

# Scrollbar orizzontale
scrollbar_h = tk.Scrollbar(frame_text, orient="horizontal")
scrollbar_h.pack(side="bottom", fill="x")

# Area di testo per la trascrizione
text_time = tk.Text(frame_text, width=90, height=30, 
                    yscrollcommand=scrollbar_v.set,
                    xscrollcommand=scrollbar_h.set,
                    wrap="none")
text_time.pack(side="left", fill="both", expand=True)

# Collega le scrollbar al widget Text
scrollbar_v.config(command=text_time.yview)
scrollbar_h.config(command=text_time.xview)

# Label per mostrare il file caricato (sotto le scrollbar)
lab2 = tk.Label(window, text="File caricato> Nessun file selezionato")
lab2.grid(row=3, column=0, pady=5)

def f_sfoglia():
    global path_file
    path_file = filedialog.askopenfilename()
    if path_file:  # Controlla che sia stato selezionato un file
        print(f"File selezionato: {path_file}")
        lab2.config(text=f"File caricato> {path_file}")
    else:
        lab2.config(text="File caricato> Nessun file selezionato")

frame_button = tk.Frame(window)
frame_button.grid(row=4, column=0)

# Bottone per caricare il video
sfoglia = tk.Button(frame_button, text="3> Carica Video Scaricato", command=f_sfoglia)
sfoglia.grid(row=0, column=0, padx=2)

import re
import os
from moviepy import VideoFileClip
import subprocess
        
def f_avvia_traduzione():
    global path_file
    if path_file:
        nome_base = os.path.splitext(os.path.basename(path_file))[0]
        nome_file_output = f"{nome_base}.txt"
        
        trascrizione = text_time.get("1.0", tk.END).strip()
        if trascrizione:
            # Rimuove le linee vuote e la parola "Trascrizione"
            linee = trascrizione.split('\n')
            linee_pulite = []
            
            for linea in linee:
                linea = linea.strip()
                if linea and linea != "Trascrizione":
                    linee_pulite.append(linea)
            
            # Unisce timestamp con la riga successiva
            risultato = []
            i = 0
            while i < len(linee_pulite):
                linea = linee_pulite[i]
                
                # Se è un timestamp (mm:ss o h:mm:ss)
                if re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', linea):
                    # Prende la riga successiva e la mette sulla stessa riga
                    if i + 1 < len(linee_pulite):
                        risultato.append(f"{linea} {linee_pulite[i + 1]}")
                        i += 2
                    else:
                        risultato.append(linea)
                        i += 1
                else:
                    risultato.append(linea)
                    i += 1
            
            testo_finale = '\n'.join(risultato)
            
            # Salva nel file
            with open(nome_file_output, "w", encoding="utf-8") as t:
                t.write(testo_finale)
            
            print(f"Trascrizione salvata in: {nome_file_output}")
            print(f"Numero di righe: {len(risultato)}")

        # Ridimensiona il video usando GPU NVIDIA completamente
        temp_video = f"temp_{nome_base}.mp4"
        if not os.path.exists(temp_video):
            print(f"\nRidimensionamento video in corso con GPU NVIDIA...")
            
            with VideoFileClip(path_file) as video:
                nuova_larghezza = video.w // 4
                nuova_altezza = video.h // 4
                
                print(f"Dimensioni originali: {video.w}x{video.h}")
                print(f"Nuove dimensioni: {nuova_larghezza}x{nuova_altezza}")
            
            # Usa ffmpeg con massima compressione video + audio perfetto
            comando = [
                'ffmpeg',
                '-hwaccel', 'cuda',  # Accelerazione hardware CUDA
                '-hwaccel_output_format', 'cuda',  # Output su GPU
                '-i', path_file,  # File input
                '-vf', f'scale_cuda={nuova_larghezza}:{nuova_altezza}',  # Resize su GPU
                '-c:v', 'h264_nvenc',  # Codec GPU NVIDIA
                '-preset', 'fast',
                '-cq', '35',  # Massima compressione video (tanto poi usi originale)
                '-c:a', 'copy',  # AUDIO ORIGINALE NON RICODIFICATO - qualità perfetta!
                '-y',  # Sovrascrivi se esiste
                temp_video
            ]
            
            subprocess.run(comando, check=True)
            
            # Stampa dimensioni file
            size_originale = os.path.getsize(path_file) / (1024 * 1024)
            size_ridotto = os.path.getsize(temp_video) / (1024 * 1024)
            print(f"File originale: {size_originale:.2f} MB")
            print(f"File ridotto: {size_ridotto:.2f} MB")
            print(f"Riduzione: {((1 - size_ridotto/size_originale) * 100):.1f}%")
            print(f"Video ridimensionato salvato: {temp_video}")
        else:
            print(f"Video ridimensionato già esistente: {temp_video}")
    else:
        print("Errore: Nessun file video caricato")
# Bottone per avviare la traduzione
Avvia_traduzione = tk.Button(frame_button,text="4> Ridimensiona & Trascrizioni", command=f_avvia_traduzione)
Avvia_traduzione.grid(row=1, column=0, padx=2)

from moviepy import VideoFileClip, AudioFileClip
import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import subprocess
import shutil
import shlex
import time
import threading
from queue import Queue
import re

# ===== CLASSE PER GESTIRE PROCESSI IN BACKGROUND =====
class DubbingProcess:
    def __init__(self, clip_counter, voce_path, accompagnamento_path, battuta_pulita, 
                 voice_start_offset_ms, output_dir, codice_originale, codice_traduzione,
                 val_exaggeration, val_cfg, tempo_precedente, tempo_finale):
        self.clip_counter = clip_counter
        self.voce_path = voce_path
        self.accompagnamento_path = accompagnamento_path
        self.battuta_pulita = battuta_pulita
        self.voice_start_offset_ms = voice_start_offset_ms
        self.output_dir = output_dir
        self.codice_originale = codice_originale
        self.codice_traduzione = codice_traduzione
        self.val_exaggeration = val_exaggeration
        self.val_cfg = val_cfg
        self.tempo_precedente = tempo_precedente
        self.tempo_finale = tempo_finale
        self.thread = None
        self.completed = False
        self.success = False
        
    def run(self):
        """Esegue il doppiaggio in background"""
        self.thread = threading.Thread(target=self._processo_doppiaggio)
        self.thread.start()
        
    def is_alive(self):
        """Verifica se il thread è ancora in esecuzione"""
        return self.thread and self.thread.is_alive()
    
    def wait(self):
        """Attende il completamento del thread"""
        if self.thread:
            self.thread.join()
    
    def _processo_doppiaggio(self):
        """Processo di doppiaggio (eseguito in background)"""
        try:
            print(f"\n[BACKGROUND] Inizio doppiaggio clip {self.clip_counter}")
            
            # Chiamata al doppiaggio con voice.py
            audio_doppiato = os.path.join(self.output_dir, f"audio_doppiato_{self.clip_counter}.wav")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            voice_script = os.path.join(script_dir, 'voice.py')
            
            # Costruisci comando
            comando_lista = [
                'python', voice_script,
                '--path_input', self.voce_path,
                '--battuta', self.battuta_pulita,
                '--output', audio_doppiato,
                '--lingua', self.codice_originale,
                '--lingua_inp', self.codice_originale,
                '--lingua_trad', self.codice_traduzione,
            ]
            
            if self.val_exaggeration != 'Auto':
                comando_lista.extend(['--espressione', str(self.val_exaggeration)])
            if self.val_cfg != 'Auto':
                comando_lista.extend(['--cfg', str(self.val_cfg)])
            
            print(f"[BACKGROUND CLIP {self.clip_counter}] Esecuzione doppiaggio...")
            try:
                result = subprocess.run(comando_lista, capture_output=True, text=True, timeout=300)
            except subprocess.TimeoutExpired:
                print(f"[BACKGROUND CLIP {self.clip_counter}] ERRORE: Timeout (>5min)")
                self.completed = True
                self.success = False
                return
            
            if result.returncode != 0:
                error_msg = result.stderr.lower()
                # Gestisci errori specifici per clip troppo corte
                if 'indexerror' in error_msg or 'non-zero size' in error_msg or 'expected reduction' in error_msg:
                    print(f"[BACKGROUND CLIP {self.clip_counter}] ERRORE: Audio troppo corto per il doppiaggio")
                else:
                    print(f"[BACKGROUND CLIP {self.clip_counter}] ERRORE: {result.stderr}")
                self.completed = True
                self.success = False
                return
            
            # Trova il file audio generato
            possible_files = [
                audio_doppiato,
                os.path.join(self.output_dir, "output.wav"),
                "output.wav"
            ]
            
            actual_audio_file = None
            for possible_file in possible_files:
                if os.path.exists(possible_file):
                    actual_audio_file = possible_file
                    break
            
            if actual_audio_file is None:
                print(f"[BACKGROUND CLIP {self.clip_counter}] ERRORE: File audio non trovato")
                self.completed = True
                self.success = False
                return
            
            if actual_audio_file != audio_doppiato:
                shutil.move(actual_audio_file, audio_doppiato)
            
            # Carica audio e sincronizza
            audio_voce_doppiata = AudioSegment.from_wav(audio_doppiato)
            audio_music = AudioSegment.from_wav(self.accompagnamento_path)
            
            # Aggiungi silenzio per sincronizzazione
            if self.voice_start_offset_ms > 0:
                silenzio = AudioSegment.silent(duration=self.voice_start_offset_ms)
                audio_voce_doppiata = silenzio + audio_voce_doppiata
                print(f"[BACKGROUND CLIP {self.clip_counter}] Silenzio: {self.voice_start_offset_ms}ms")
            
            # Overlay voce + musica
            audio_finale = audio_music.overlay(audio_voce_doppiata)
            audio_finale_path = os.path.join(self.output_dir, f"audio_finale_{self.clip_counter}.wav")
            audio_finale.export(audio_finale_path, format="wav")
            
            # Salva info per la fase di composizione video
            self.audio_finale_path = audio_finale_path
            self.audio_doppiato_path = audio_doppiato
            
            print(f"[BACKGROUND CLIP {self.clip_counter}] Doppiaggio completato!")
            self.completed = True
            self.success = True
            
        except Exception as e:
            print(f"[BACKGROUND CLIP {self.clip_counter}] ECCEZIONE: {e}")
            self.completed = True
            self.success = False


# ===== FUNZIONE PRINCIPALE ESTRAZIONE CLIPS =====
def estrai_clips():
    global path_file, audio_finale_path
    
    try:
        import pynvml
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        
        def get_free_vram_gb():
            """Ritorna VRAM libera in GB"""
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            return info.free / (1024**3)  # Converti in GB
        
        vram_available = True
        print(f"VRAM libera iniziale: {get_free_vram_gb():.2f} GB")
    except:
        print("AVVISO: Impossibile monitorare VRAM, elaborazione sequenziale")
        vram_available = False
        def get_free_vram_gb():
            return 0
    
    print("estrai clips")
    
    if not path_file:
        print("Seleziona File Video (Sfoglia)")
        return
    
    base_name = os.path.basename(path_file).split('.')[0]
    dir_name = os.path.dirname(path_file)
    
    transcription_file = os.path.join(dir_name, f"{base_name}.txt")
    temp_file = os.path.join(dir_name, f"temp_{os.path.basename(path_file)}")
    
    if not os.path.exists(transcription_file):
        print("crea file trascrizioni da youtube")
        return
    
    if not os.path.exists(temp_file):
        print("Ridimensiona Il file Originale")
        return
    
    print("estrai clips")
    Video = VideoFileClip(temp_file)
    
    # Array per memorizzare timestamp e battute
    timeslaps = []
    battute = []
    
    # Leggi file trascrizione
    for riga in open(transcription_file, encoding='utf-8').readlines():
        riga = riga.strip()
        if not riga:
            continue
        
        primo_spazio = riga.find(' ')
        if primo_spazio != -1:
            timeslap = riga[:primo_spazio]
            battuta = riga[primo_spazio+1:].strip()
            timeslaps.append(timeslap)
            battute.append(battuta)
        else:
            timeslap = riga
            battuta = ""
            timeslaps.append(timeslap)
            battute.append(battuta)
    
    print(f"\nTotale righe elaborate: {len(timeslaps)}")
    
    # ===== FUNZIONE HELPER PER CONVERTIRE TIMESTAMP =====
    def timestamp_to_seconds(timestamp):
        """Converte timestamp da formato MM:SS o H:MM:SS a secondi"""
        parti = timestamp.split(':')
        if len(parti) == 3:  # Formato H:MM:SS
            ore = int(parti[0])
            minuti = int(parti[1])
            secondi = int(parti[2])
            return ore * 3600 + minuti * 60 + secondi
        elif len(parti) == 2:  # Formato MM:SS
            minuti = int(parti[0])
            secondi = int(parti[1])
            return minuti * 60 + secondi
        else:
            raise ValueError(f"Formato timestamp non valido: {timestamp}")
    
    # ===== CREA FINESTRA PROGRESSO =====
    progress_window = tk.Toplevel(barr)
    progress_window.title("Progresso Doppiaggio")
    progress_window.geometry("500x180")
    progress_window.resizable(False, False)
    
    status_label = tk.Label(progress_window, text="Inizializzazione...", font=("Arial", 10))
    status_label.pack(pady=10)
    
    progress_bar = ttk.Progressbar(progress_window, length=450, mode='determinate')
    progress_bar.pack(pady=10)
    
    info_label = tk.Label(progress_window, text="0% completato - Tempo stimato: Calcolo...", font=("Arial", 9))
    info_label.pack(pady=5)
    
    # Label processi attivi
    processes_label = tk.Label(progress_window, text="Processi attivi: 0/4", font=("Arial", 9), fg="blue")
    processes_label.pack(pady=5)
    
    progress_window.update()
    
    # Crea directory output
    output_dir = os.path.join(dir_name, "clips")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    i = 0
    clip_counter = 0
    tempo_precedente = 0
    start_time = time.time()
    clips_processed = 0
    
    # ===== GESTIONE PROCESSI PARALLELI =====
    active_processes = []  # Lista processi in background attivi
    MAX_PROCESSES = 4
    VRAM_THRESHOLD_GB = 2.0  # GB minimi necessari per avviare nuovo processo
    
    # Estrai i codici lingua
    codice_originale = lingua_originale.get().split('(')[-1].rstrip(')')
    codice_traduzione = lingua_traduzione.get().split('(')[-1].rstrip(')')
    val_exaggeration = exaggeration.get()
    val_cfg = cfg_weight.get()

    while i < len(timeslaps) or len(active_processes) > 0:
        # ===== PULISCI PROCESSI COMPLETATI =====
        completed_processes = [p for p in active_processes if p.completed]
        for proc in completed_processes:
            active_processes.remove(proc)
            
            if proc.success:
                # Fase di composizione video (NON in background)
                print(f"\n[COMPOSIZIONE] Finalizzo clip {proc.clip_counter}")
                
                try:
                    # Ricarica la clip video
                    clip = Video.subclipped(proc.tempo_precedente, proc.tempo_finale)
                    
                    # Combina video con audio finale
                    audio_clip = AudioFileClip(proc.audio_finale_path)
                    clip_finale = clip.with_audio(audio_clip)
                    
                    # Salva il video finale
                    output_path = os.path.join(output_dir, f"clip{proc.clip_counter}.mp4")
                    clip_finale.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
                    
                    print(f"[COMPOSIZIONE] Clip {proc.clip_counter} salvata!")
                    
                    audio_clip.close()
                    del clip_finale
                    del clip
                    
                    # Pulisci file temporanei
                    temp_audio_path = os.path.join(output_dir, f"temp_audio_{proc.clip_counter}.wav")
                    if os.path.exists(temp_audio_path):
                        os.remove(temp_audio_path)
                    if os.path.exists(proc.voce_path):
                        os.remove(proc.voce_path)
                    if os.path.exists(proc.accompagnamento_path):
                        os.remove(proc.accompagnamento_path)
                    if os.path.exists(proc.audio_doppiato_path):
                        os.remove(proc.audio_doppiato_path)
                    if os.path.exists(proc.audio_finale_path):
                        os.remove(proc.audio_finale_path)
                        
                except Exception as e:
                    print(f"[COMPOSIZIONE] ERRORE clip {proc.clip_counter}: {e}")
            
            clips_processed += 1
        
        # ===== AGGIORNA UI =====
        if i < len(timeslaps):
            progress_percentage = (i / len(timeslaps)) * 100
        else:
            progress_percentage = 100
            
        progress_bar['value'] = progress_percentage
        
        if clips_processed > 0:
            elapsed_time = time.time() - start_time
            avg_time_per_clip = elapsed_time / clips_processed
            clips_remaining = len(timeslaps) - i
            estimated_time = avg_time_per_clip * clips_remaining
            mins, secs = divmod(int(estimated_time), 60)
            time_str = f"{mins}m {secs}s"
        else:
            time_str = "Calcolo..."
        
        status_label.config(text=f"Elaborazione clip {clip_counter + 1}/{len(timeslaps)}")
        info_label.config(text=f"{progress_percentage:.1f}% completato - Tempo: {time_str}")
        processes_label.config(text=f"Processi attivi: {len(active_processes)}/{MAX_PROCESSES}")
        progress_window.update()
        
        # ===== ELABORA PROSSIMA CLIP =====
        if i >= len(timeslaps):
            time.sleep(0.5)  # Attendi completamento processi
            continue
        
        print(f"\n{i}: {timeslaps[i]} -> {battute[i][:60]}")
        
        # Estrai timestamp usando la funzione helper
        try:
            tempo_iniziale = timestamp_to_seconds(timeslaps[i])
        except ValueError as e:
            print(f"ERRORE: {e}")
            i += 1
            continue
        
        battuta_clean = battute[i].strip()
        
        # Verifica se è solo musica/suoni
        is_solo_musica = battuta_clean == '[Música]' or battuta_clean == '[Music]' or battuta_clean == '[Musica]'
        is_solo_suono = (
            is_solo_musica or battuta_clean == '' or
            (battuta_clean.startswith('[') and battuta_clean.endswith(']') and len(battuta_clean) < 20) or
            battuta_clean == '[ __ ]'
        )
        
        if '[Música]' in battuta_clean and len(battuta_clean) > 15:
            is_solo_suono = False
        
        # ===== GESTIONE CLIP MUSICA/SUONI (NON BACKGROUND) =====
        if is_solo_suono:
            j = i
            while j < len(timeslaps):
                battuta_successiva = battute[j].strip()
                is_suono_successivo = (
                    battuta_successiva == '[Música]' or battuta_successiva == '[Music]' or
                    battuta_successiva == '[Musica]' or battuta_successiva == '' or
                    (battuta_successiva.startswith('[') and battuta_successiva.endswith(']') and len(battuta_successiva) < 20) or
                    battuta_successiva == '[ __ ]'
                )
                if '[Música]' in battuta_successiva and len(battuta_successiva) > 15:
                    is_suono_successivo = False
                if not is_suono_successivo:
                    break
                j += 1
            
            if j < len(timeslaps):
                try:
                    tempo_finale = timestamp_to_seconds(timeslaps[j])
                except ValueError as e:
                    print(f"ERRORE: {e}")
                    i += 1
                    continue
            else:
                tempo_finale = Video.duration
            
            if tempo_finale - tempo_precedente < 0.1:
                print(f"Clip {clip_counter} saltata (durata troppo breve)")
                tempo_precedente = tempo_finale
                i = j if j < len(timeslaps) else i + 1
                continue
            
            output_path = os.path.join(output_dir, f"clip{clip_counter}.mp4")
            if os.path.exists(output_path):
                print(f"Clip {clip_counter} già esistente")
                tempo_precedente = tempo_finale
                clip_counter += 1
                clips_processed += 1
                i = j
                continue
            
            # ELABORAZIONE IMMEDIATA (NO BACKGROUND)
            print(f"[DIRETTO] Salvataggio clip musica {clip_counter}")
            clip = Video.subclipped(tempo_precedente, tempo_finale)
            clip.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
            print(f"[DIRETTO] Clip {clip_counter} salvata")
            del clip
            
            tempo_precedente = tempo_finale
            clip_counter += 1
            clips_processed += 1
            i = j
        
        # ===== GESTIONE CLIP CON DOPPIAGGIO (BACKGROUND) =====
        else:
            if i + 1 < len(timeslaps):
                try:
                    tempo_finale = timestamp_to_seconds(timeslaps[i + 1])
                except ValueError as e:
                    print(f"ERRORE: {e}")
                    i += 1
                    continue
            else:
                tempo_finale = Video.duration
            
            # Verifica durata minima della clip (almeno 1 secondo per il doppiaggio)
            durata_clip = tempo_finale - tempo_precedente
            if durata_clip < 1.0:
                print(f"Clip {clip_counter} saltata (durata troppo breve: {durata_clip:.2f}s)")
                tempo_precedente = tempo_finale
                i += 1
                continue
            
            output_path_check = os.path.join(output_dir, f"clip{clip_counter}.mp4")
            if os.path.exists(output_path_check):
                print(f"Clip {clip_counter} già esistente")
                tempo_precedente = tempo_finale
                clip_counter += 1
                clips_processed += 1
                i += 1
                continue
            
            # ATTENDI SE TROPPI PROCESSI ATTIVI O VRAM INSUFFICIENTE
            while len(active_processes) >= MAX_PROCESSES or (vram_available and get_free_vram_gb() < VRAM_THRESHOLD_GB):
                print(f"[ATTESA] Processi: {len(active_processes)}/{MAX_PROCESSES}, VRAM: {get_free_vram_gb():.2f} GB")
                time.sleep(2)
                
                # Pulisci processi completati durante l'attesa
                completed = [p for p in active_processes if p.completed]
                for proc in completed:
                    active_processes.remove(proc)
                    if proc.success:
                        # Composizione video immediata
                        try:
                            clip_temp = Video.subclipped(proc.tempo_precedente, proc.tempo_finale)
                            audio_clip = AudioFileClip(proc.audio_finale_path)
                            clip_finale = clip_temp.with_audio(audio_clip)
                            output_path = os.path.join(output_dir, f"clip{proc.clip_counter}.mp4")
                            clip_finale.write_videofile(output_path, codec='libx264', audio_codec='aac', logger=None)
                            audio_clip.close()
                            del clip_finale, clip_temp
                        except:
                            pass
                    clips_processed += 1
                
                progress_window.update()
            
            # PREPARA DOPPIAGGIO IN BACKGROUND
            print(f"[PREP] Estrazione audio clip {clip_counter}")
            clip = Video.subclipped(tempo_precedente, tempo_finale)
            temp_audio_path = os.path.join(output_dir, f"temp_audio_{clip_counter}.wav")
            clip.audio.write_audiofile(temp_audio_path, codec='pcm_s16le', logger=None)
            del clip
            
            # Demucs
            print(f"[PREP] Separazione audio clip {clip_counter}")
            subprocess.run(['demucs', '--two-stems=vocals', '-o', output_dir, temp_audio_path], 
                          capture_output=True, text=True)
            
            demucs_folder = os.path.join(output_dir, 'htdemucs', f'temp_audio_{clip_counter}')
            voce_path_source = os.path.join(demucs_folder, "vocals.wav")
            accompagnamento_path_source = os.path.join(demucs_folder, "no_vocals.wav")
            voce_path = os.path.join(output_dir, f"vocals_{clip_counter}.wav")
            accompagnamento_path = os.path.join(output_dir, f"no_vocals_{clip_counter}.wav")
            
            if not os.path.exists(voce_path_source) or not os.path.exists(accompagnamento_path_source):
                print(f"[PREP] ERRORE: File Demucs mancanti per clip {clip_counter}")
                i += 1
                clip_counter += 1
                continue
            
            shutil.move(voce_path_source, voce_path)
            shutil.move(accompagnamento_path_source, accompagnamento_path)
            
            htdemucs_path = os.path.join(output_dir, 'htdemucs')
            if os.path.exists(htdemucs_path):
                shutil.rmtree(htdemucs_path)
            
            # Pulisci battuta
            battuta_pulita = re.sub(r'\[Música\]|\[Music\]|\[Musica\]|\[\s*__\s*\]', '', battute[i])
            battuta_pulita = re.sub(r'\[[^\]]{0,20}\]', '', battuta_pulita)
            battuta_pulita = re.sub(r'\s+', ' ', battuta_pulita).strip()
            
            # Verifica che ci sia testo sufficiente da doppiare (almeno 3 caratteri)
            if len(battuta_pulita) < 3:
                print(f"Clip {clip_counter} saltata (testo troppo corto: '{battuta_pulita}')")
                tempo_precedente = tempo_finale
                clip_counter += 1
                i += 1
                continue
            
            # Rileva offset voce
            voce_originale = AudioSegment.from_wav(voce_path)
            nonsilent_ranges = detect_nonsilent(voce_originale, min_silence_len=100, silence_thresh=-40)
            voice_start_offset_ms = nonsilent_ranges[0][0] if nonsilent_ranges else 0
            
            # AVVIA PROCESSO IN BACKGROUND
            proc = DubbingProcess(
                clip_counter, voce_path, accompagnamento_path, battuta_pulita,
                voice_start_offset_ms, output_dir, codice_originale, codice_traduzione,
                val_exaggeration, val_cfg, tempo_precedente, tempo_finale
            )
            proc.run()
            active_processes.append(proc)
            
            print(f"[BACKGROUND] Avviato processo clip {clip_counter} ({len(active_processes)}/{MAX_PROCESSES})")
            
            tempo_precedente = tempo_finale
            clip_counter += 1
            i += 1
    
    # CHIUDI VIDEO
    Video.close()
    
    # COMPLETAMENTO
    progress_bar['value'] = 100
    status_label.config(text="Completato!")
    info_label.config(text=f"100% - Totale clip: {clip_counter}")
    processes_label.config(text="Processi: 0/4")
    progress_window.update()
    progress_window.after(2000, progress_window.destroy)
    
    print(f"\n✓ Totale clip create: {clip_counter}")

crea_clips= tk.Button(frame_button,text="5> Create Clips",command=estrai_clips)
crea_clips.grid(row=1,column=2,padx=2)
from tkinter import ttk

lab3 = tk.Label(frame_button, text='Ling. Originale')
lab3.grid(row=0, column=3)
lab4 = tk.Label(frame_button, text='Ling. Traduzione')
lab4.grid(row=0, column=4)

# Lista completa delle lingue supportate
lingue_supportate = [
    'Arabic (ar)',
    'Danish (da)',
    'German (de)',
    'Greek (el)',
    'English (en)',
    'Spanish (es)',
    'Finnish (fi)',
    'French (fr)',
    'Hebrew (he)',
    'Hindi (hi)',
    'Italian (it)',
    'Japanese (ja)',
    'Korean (ko)',
    'Malay (ms)',
    'Dutch (nl)',
    'Norwegian (no)',
    'Polish (pl)',
    'Portuguese (pt)',
    'Russian (ru)',
    'Swedish (sv)',
    'Swahili (sw)',
    'Turkish (tr)',
    'Chinese (zh)'
]

lingua_originale = ttk.Combobox(frame_button, values=lingue_supportate, width=15)
lingua_originale.grid(row=1, column=3, padx=2)
lingua_originale.set('Spanish (es)')  # Valore predefinito

lingua_traduzione = ttk.Combobox(frame_button, values=lingue_supportate, width=15)
lingua_traduzione.grid(row=1, column=4, padx=2)
lingua_traduzione.set('Italian (it)')  # Valore predefinito

# Label per exaggeration
lab5 = tk.Label(frame_button, text='Exaggeration')
lab5.grid(row=0, column=5)

# Combobox exaggeration con valori da 0.1 a 1.0
valori_exaggeration = ['Auto'] + [f'{i/10:.1f}' for i in range(1, 11)]  # 0.1, 0.2, ..., 1.0
exaggeration = ttk.Combobox(frame_button, values=valori_exaggeration, width=10)
exaggeration.grid(row=1, column=5, padx=2)
exaggeration.set('0.5')  # Valore predefinito

# Label per cfg_weight
lab6 = tk.Label(frame_button, text='CFG Weight')
lab6.grid(row=0, column=6)

# Combobox cfg_weight con valori da 0.1 a 1.0
valori_cfg = ['Auto'] + [f'{i/10:.1f}' for i in range(1, 11)]  # 0.1, 0.2, ..., 1.0
cfg_weight = ttk.Combobox(frame_button, values=valori_cfg, width=10)
cfg_weight.grid(row=1, column=6, padx=2)
cfg_weight.set('0.5')  # Valore predefinito

from tkinter import messagebox

def f_rendering():
    global path_file
    dir = "./clips"
    if path_file and os.path.exists(path_file):
                # Cerca il file clip_0 con diverse estensioni
                estensione_clip0 = None
                for ext in ['.mp4', '.mkv', '.mov']:
                    filepath = os.path.join(dir, f'clip0{ext}')
                    if os.path.exists(filepath):
                        estensione_clip0 = ext
                        break
                
                if estensione_clip0 is None:
                    print("Nessun file clip0 trovato")
                    return
                
                # askquestion restituisce 'yes' o 'no' come stringhe
                risp = messagebox.askquestion("Conferma", 
                                            "Rimuovi i files temporanei differenti dalle clips?")
                
                if risp == 'yes':
                    for f in os.listdir(dir):
                        filepath = os.path.join(dir, f)
                        if os.path.isfile(filepath) and not f.startswith('clip'):
                            os.remove(filepath)
                
                time.sleep(2)
                
                # Leggi tutti i file clip presenti e ordinali
                arraysclips = []
                for f in os.listdir(dir):
                    if f.startswith('clip') and f.endswith(estensione_clip0):
                        arraysclips.append(os.path.join(dir, f))

                # Ordina per numero usando solo il nome del file
                arraysclips.sort(key=lambda x: int(os.path.basename(x).replace('clip', '').split('.')[0]))

                print(f"clips trovate: {len(arraysclips)}")
                print(f"clips: {arraysclips}")

                # Estrai l'audio da ogni clip
                audio_files = []
                for i, c in enumerate(arraysclips):
                    audio_output = os.path.join(dir, f"audio_{i}.wav")
                    subprocess.run([
                        "ffmpeg", "-i", c,
                        "-vn",  # no video
                        "-acodec", "pcm_s16le",  # codec audio WAV
                        "-ar", "44100",  # sample rate
                        "-ac", "2",  # stereo
                        "-y",  # sovrascrivi se esiste
                        audio_output
                    ])
                    audio_files.append(audio_output)

                # Crea file di lista per concatenazione
                list_file = os.path.join(dir, "audio_list.txt")
                with open(list_file, 'w') as f:
                    for audio in audio_files:
                        # Usa percorso assoluto e sostituisci backslash con forward slash
                        abs_path = os.path.abspath(audio).replace('\\', '/')
                        f.write(f"file '{abs_path}'\n")

                # Concatena tutti gli audio
                audio_concatenato = os.path.join(dir, "audioconcatenato.wav")
                subprocess.run([
                    "ffmpeg", "-f", "concat",
                    "-safe", "0",
                    "-i", list_file,
                    "-c", "copy",
                    "-y",
                    audio_concatenato
                ])

                print(f"Audio concatenato salvato in: {audio_concatenato}")
                
                # Unisci video originale con audio concatenato usando GPU NVIDIA
                output_file = os.path.join(dir, "video_finale.mp4")

                # Crea finestra progress bar
                progress_window = tk.Toplevel(window)
                progress_window.title("Rendering in corso...")
                progress_window.geometry("400x100")

                progress_label = tk.Label(progress_window, text="Encoding video...")
                progress_label.pack(pady=10)

                progress_bar = ttk.Progressbar(progress_window, length=300, mode='indeterminate')
                progress_bar.pack(pady=10)
                progress_bar.start()

                window.update()

                # Funzione per encoding
                def encode_video():
                    subprocess.run([
                        "ffmpeg",
                        "-hwaccel", "cuda",
                        "-i", path_file,
                        "-i", audio_concatenato,
                        "-map", "0:v:0",
                        "-map", "1:a:0",
                        "-c:v", "h264_nvenc",
                        "-preset", "p4",
                        "-cq", "23",
                        "-c:a", "aac",
                        "-b:a", "128k",
                        "-movflags", "+faststart",
                        "-y",
                        output_file
                    ])
                    
                    progress_bar.stop()
                    progress_window.destroy()
                    print(f"Video finale salvato in: {output_file}")
                    messagebox.showinfo("Completato", f"Rendering completato!\n{output_file}")

                # Avvia encoding in thread separato
                import threading
                thread = threading.Thread(target=encode_video)
                thread.start()
                
    else:
        messagebox.showinfo("Errore", "Carica file Film Originale: press Button 3>")


rendering = tk.Button(frame_button, text='6> Rendering', command=f_rendering)
rendering.grid(row=2, column=2, pady=3)

window.mainloop()


