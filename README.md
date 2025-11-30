Markdown

# 🎬 Doppiatore-Film-IA

**Traduci ogni tuo film preferito in tutte le lingue sfruttando la potenza della tecnologia di Chatterbox!**

Questo progetto ti permette di prendere un video (ad esempio, un film o un cortometraggio) e doppiarlo automaticamente in qualsiasi lingua, preservando la sincronizzazione delle labbra e il tono di voce, grazie al framework AI di `chatterbox`.

---

## 🚀 Installazione e Configurazione

Segui attentamente i passaggi di seguito per configurare l'ambiente di lavoro.

### 1. Clonazione del Repository

Clona il progetto nella tua macchina locale usando Git:

```bash
git clone [https://github.com/asprho-arkimete/Doppiatore-Film-IA.git](https://github.com/asprho-arkimete/Doppiatore-Film-IA.git)
2. Creazione e Attivazione dell'Ambiente Conda
⚠️ ATTENZIONE: È molto importante usare Python 3.11 e Conda per questo progetto. L'uso di python -m venv potrebbe causare malfunzionamenti.

Crea l'ambiente Conda:

Bash

conda create -yn chatterbox python=3.11
Attiva l'ambiente virtuale appena creato:

Bash

conda activate chatterbox
3. Installazione dei Pacchetti
A. Installazione di chatterbox-tts
Installa la libreria principale di Chatterbox:

Bash

pip install chatterbox-tts
B. Installazione delle Dipendenze del Progetto
Entra nella directory del progetto:

Bash

cd Doppiatore-Film-IA 
# O cd chatterbox, a seconda di come è strutturata la tua cartella dopo la clonazione
Installa il pacchetto chatterbox in modalità modificabile (editable mode) e tutte le librerie aggiuntive richieste:

Bash

pip install -e .
# Installa tutte le altre dipendenze necessarie dal file dei requisiti (se presente)
# pip install -r requisiti.txt  # Rimuovi il commento se hai un file 'requisiti.txt'
🔎 Approfondimento: Se vuoi saperne di più sul progetto principale, visita la repository ufficiale di Chatterbox: https://github.com/resemble-ai/chatterbox

⚙️ Istruzioni per l'Uso (Interfaccia Grafica)
Una volta installate tutte le dipendenze, puoi lanciare lo script principale e seguire l'ordine numerato dei bottoni per doppiare il tuo video.

Lancia il file principale:

Bash

python downloader.py
All'apertura dell'interfaccia, segui l'ordine numerato dei bottoni:

Apri il sito web e scarica il Film da Youtube:

Usa questo strumento per scaricare il video desiderato da YouTube (con la massima risoluzione disponibile).

Se il tuo video non è su YouTube, caricalo per ottenere la trascrizione delle battute e i timestamp.

Incolla la trascrizione del video:

Copia e incolla il testo della trascrizione del video nella TextBox appropriata.

Carica il video scaricato!

Carica il file video che hai scaricato al Passaggio 1.

Ridimensiona e Crea Trascrizione:

Premi questo bottone per ridimensionare il file video a una risoluzione inferiore (necessario per velocizzare l'elaborazione) e per creare il file di testo della trascrizione.

Crea le clips Tradotte:

Questo passaggio genera le singole clip audio tradotte e doppiate.

Nota: Se la cartella clips non esiste, verrà creata automaticamente all'interno della cartella di lavoro (\chatterbox).

Rendering Finale:

Una volta completata la creazione di tutte le clip, premi questo bottone.

Il sistema unirà le clip doppiate al video originale ad alta risoluzione (scaricato inizialmente), sostituendo la traccia audio e generando il tuo film doppiato finale.

✨ Esempio di un Film Doppiato
Ecco un esempio del risultato finale:

Film Doppiato: "https://www.youtube.com/watch?v=ncscIeLjGSE"


Posso fare altro per aiutarti con la documentazione o il codice del progetto?



