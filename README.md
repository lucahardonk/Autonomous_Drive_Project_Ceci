### Diagramma fisico del sistema

Questo schema mostra il collegamento fisico tra i principali componenti del veicolo:<br>
🔋 Batteria (12V) – alimenta l’intero sistema.<br>
⚙️ Modulo DC-DC (12V → 6V) – riduce la tensione da 12V a 6V.<br>
🧠 Scheda Arduino – alimentata a 6V tramite il modulo DC-DC.<br>
🛞 Driver dei motori – alimentati direttamente dalla batteria a 12V.<br>
⚡ Encoder – forniscono il feedback di rotazione per il controllo dei motori.<br>
🔁 Servo motore – alimentato a 6V, gestisce la direzione del veicolo.<br>
<br>
![](physical_diagram.png)


## 🚗 Autonomous Drive Project

Il progetto **Autonomous Drive** ha l’obiettivo di realizzare una piattaforma sperimentale per la **guida autonoma** in scala ridotta, basata su **Arduino UNO R4 WiFi**.  
Attualmente, il sistema può essere controllato **manualmente** tramite una **web app** o con un **steering wheel fisico**, che consentono di gestire in tempo reale i movimenti del veicolo e di monitorarne lo stato.

---

### 🔧 Struttura del progetto

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

---

### ⚡ Obiettivo

In questa fase il veicolo è **a controllo manuale**, ma il progetto è pensato per essere esteso con funzioni di **guida autonoma** basate su sensori e algoritmi di controllo.
