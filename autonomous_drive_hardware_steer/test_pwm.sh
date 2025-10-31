#!/bin/bash

IP="192.168.1.162"
PORT=9085

# Lista dei PWM da testare
PWMS=(0 30 60 90 120 150 180 210 240 255)

# Intervallo tra i comandi (in secondi)
INTERVAL=20

while true; do
  echo "🚗 Nuovo ciclo di test $(date)"
  
  for pwm in "${PWMS[@]}"; do
    json="{\"LPwm\":0, \"RPwm\":$pwm, \"D\":1, \"S\":0}"
    echo -n "$json" | nc -w1 -u $IP $PORT
    echo "Inviato: $json"

    # Countdown visivo dei secondi
    for ((i=INTERVAL; i>0; i--)); do
      echo -ne "⏱️  Attesa: $i sec\r"
      sleep 1
    done
    echo ""
  done

  echo "✅ Ciclo completato — riparto tra 3 secondi..."
  sleep 3
  echo ""
done
