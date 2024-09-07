#!/bin/bash

# Define variables
ZIP_FILE="$1"
DEST_DIR="$2"
LOG_FILE="duplicate_files.txt"

# Ensure destination directory exists
mkdir -p "$DEST_DIR"

# Loop through all files in the ZIP archive
unzip -l "$ZIP_FILE" | awk '{print $4}' | while read -r FILE; do
    if [[ "$FILE" != "" && "$FILE" != *"/" ]]; then
        # Extract the file
        if [ -f "$DEST_DIR/$FILE" ]; then
            # If the file already exists, rename it
            BASE_NAME=$(basename "$FILE")
            DIR_NAME=$(dirname "$FILE")
            NEW_FILE="${BASE_NAME%.xml}_new.xml"
            unzip -o "$ZIP_FILE" "$FILE" -d "$DEST_DIR"
            mv "$DEST_DIR/$FILE" "$DEST_DIR/$DIR_NAME/$NEW_FILE"
            # Record the duplicate file in the log
            echo "$FILE" >> "$LOG_FILE"
            echo "Renamed $FILE to $NEW_FILE and logged."
        else
            # Extract the file normally if it doesn't exist
            unzip -o "$ZIP_FILE" "$FILE" -d "$DEST_DIR"
        fi
    fi
done
