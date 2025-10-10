# 📚 Indice

- [🔧 Struttura del progetto](#-struttura-del-progetto)
- [📁 Struttura dettagliata dei file](#-struttura-dettagliata-dei-file)
- [🚀 Installazione e avvio](#-installazione-e-avvio)
- [🧩 Diagramma fisico del sistema](#-diagramma-fisico-del-sistema)
- [👤 Autori](#-autori)

# 🚗 Autonomous Drive Project

Il progetto **Autonomous Drive** ha l’obiettivo di realizzare una piattaforma sperimentale per la **guida autonoma** in scala ridotta, basata su **Arduino UNO R4 WiFi**.  
Attualmente, il sistema può essere controllato **manualmente** tramite una **web app** o con un **steering wheel fisico**, che consentono di gestire in tempo reale i movimenti del veicolo e di monitorarne lo stato.


## 🔧 Struttura del progetto

- **🧠 `autonomous_drive_firmware/`**  
  Contiene il firmware per **Arduino**, scritto in C/C++.  
  Si occupa della gestione dei componenti principali:  
  - Lettura degli **encoder** per monitorare la velocità e la posizione delle ruote.  
  - Controllo dei **motori DC** e del **servo sterzo**.  
  - Comunicazione Wi-Fi con la web app per ricevere comandi di guida tramite un API endpoint.  

- **⚙️ `autonomous_drive_hardware_steer/`**  
  Contiene il codice Python per la gestione dello **sterzo hardware**.  
  Il modulo gestisce:  
  - L' **endpoint** dedicato alla trasmissione dei comandi di direzione.  
  - La frequenza di aggiornamento (50 Hz) e la stabilità del segnale.  

- **🌐 `autonomous_drive_webapp/`**  
  Include l’interfaccia web sviluppata in **HTML, CSS e JavaScript**.  
  L’app permette di:  
  - Inviare comandi manuali di **avanti, indietro, destra e sinistra**.  
  - Monitorare lo stato del veicolo in tempo reale.  
  - Interagire con Arduino tramite connessione Wi-Fi.


### ⚡ Obiettivo

In questa fase il veicolo è **a controllo manuale**, ma il progetto è pensato per essere esteso con funzioni di **guida autonoma** basate su sensori e algoritmi di controllo.

---



## 📁 Struttura dettagliata dei file

Questa sezione descrive nel dettaglio i file che compongono il progetto e il loro ruolo all’interno del sistema.


### 🧠 `autonomous_drive_firmware/`

Contiene il firmware principale scritto in **C/C++** per **Arduino UNO R4 WiFi**.  
È responsabile della logica di controllo del veicolo e della comunicazione con la web app.

- **`Encoder.h` / `Encoder.cpp`**  
  Gestiscono la lettura degli encoder collegati ai motori, fornendo velocità e posizione angolare delle ruote.

- **`Motor.h` / `Motor.cpp`**  
  Implementano le funzioni per il controllo dei motori DC: direzione, potenza e gestione della velocità.

- **`Sterzo.h` / `Sterzo.cpp`**  
  Gestiscono il controllo del **servo motore** per la sterzata del veicolo.

- **`WebControl.h` / `WebControl.cpp`**  
  Si occupano della comunicazione Wi-Fi tra la scheda Arduino e la web app tramite l'endpoint.

- **`autonomous_drive_firmware.ino`**  
  File principale dell’applicazione Arduino: inizializza i moduli, imposta la connessione Wi-Fi e coordina l’esecuzione del programma.


### ⚙️ `autonomous_drive_hardware_steer/`

Contiene il file Python per la gestione hardware dello sterzo.  

- **`main.py`**  
  Gestisce l' **endpoint** di comunicazione con la scheda Arduino, mantenendo la frequenza di aggiornamento a **50 Hz**.  
  Si occupa della trasmissione stabile dei comandi di sterzo e della gestione dei segnali hardware.


### 🌐 `autonomous_drive_webapp/`

Contiene l’interfaccia utente per il controllo remoto del veicolo, sviluppata con **HTML**, **CSS** e **JavaScript**.

- **`index.html`**  
  Struttura principale della web app: pulsanti di controllo, area di stato e interfaccia grafica.

- **`style.css`**  
  Definisce il layout e lo stile dell’interfaccia (colori, pulsanti, spaziature).

- **`script.js`**  
  Contiene la logica di controllo lato client.  
  Invia comandi di movimento alla scheda Arduino e aggiorna lo stato del veicolo in tempo reale.

---


## 🚀 Installazione e avvio

1. **Caricare il firmware Arduino**
   - Apri `autonomous_drive_firmware.ino` in Arduino IDE.  
   - Seleziona la scheda **Arduino UNO R4 WiFi**.  
   - Carica il codice sulla scheda.

2. **Avviare il modulo di sterzo hardware**
   - Apri una console nella cartella `autonomous_drive_hardware_steer/`.  
   - Esegui:  
     ```bash
     python3 main.py
     ```

3. **Aprire la web app**
   - Apri `index.html` in un browser compatibile (Chrome, Edge, Firefox).  
   - Controlla che il dispositivo Arduino sia connesso alla stessa rete Wi-Fi.

---


## 🔌 Diagramma fisico del sistema

Questo schema mostra il collegamento fisico tra i principali componenti del veicolo:<br>
🔋 Batteria (12V) – alimenta l’intero sistema.<br>
⚙️ Modulo DC-DC (12V → 6V) – riduce la tensione da 12V a 6V.<br>
🧠 Scheda Arduino – alimentata a 6V tramite il modulo DC-DC.<br>
🛞 Driver dei motori – alimentati direttamente dalla batteria a 12V.<br>
⚡ Encoder – forniscono il feedback di rotazione per il controllo dei motori.<br>
🔁 Servo motore – alimentato a 6V, gestisce la direzione del veicolo.<br>
<br>
![](physical_diagram.png)





---
## 👤 Autori

Progetto realizzato da **Cecilia Cavosi** e **Luca Hardonk**.
