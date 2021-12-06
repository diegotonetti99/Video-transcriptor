#!/usr/bin/env sh

IN=$1
THRESH=$2
DURATION=$3
DEST=$4

ffmpeg -hide_banner -vn -i $IN -af "silencedetect=n=${THRESH}dB:d=${DURATION}" -f null - 2>&1 | grep "silence_end" | awk '{print $5 " " $8}' > $DEST

#ffmpeg -hide_banner -vn -i $IN $THRESH $DURATION -f null -2>&1 | grep "silence_end" | awk {'print $5 " " $8'} > $DEST