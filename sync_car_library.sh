#!/bin/bash
SRC=~/Documents/Projects/Autonomous_Drive_Project_Ceci/car_library/
DST=/mnt/c/Users/lucah/Documents/Arduino/libraries/car_library/

echo "🔄 Syncing car_library to Arduino libraries..."
rsync -av --delete "$SRC" "$DST"

echo "✅ Sync complete!"
