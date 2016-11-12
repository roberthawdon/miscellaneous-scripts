#!/bin/bash

# 1080p Anime with ASS Subtitles to DVD converter script.
# Written by Robert Ian Hawdon (https://robertianhawdon.me.uk) 2016
# Tested on Ubuntu 16.04
# Requires awk, mkvtoolnix, ffmpeg

###############
# Pre process #
###############

# Get MKV file name from command line arguments.
VIDEO=$1

# Extract subtitle track.
mkvextract tracks ${VIDEO} 2:subrip-garbled.ass

# Remove Byte Order Mark (BOM) from subtitle stream (Possible FFMPEG Bug).
awk 'NR==1{sub(/^\xef\xbb\xbf/,"")}{print}' subrip-garbled.ass > subrip.ass

# Add fixed subtitles to a new MKV file, cloned from the original.
mkvmerge -o fixed-subs.mkv ${VIDEO} subrip.ass

# Burn subtitles in to 1080p video (no audio) - This will take some time.
ffmpeg -i "fixed-subs.mkv" -map 0:v -vf "subtitles=fixed-subs.mkv" -map 0:s:1 -pix_fmt yuv420p10le -b:v 6000K subtitled.mkv

# Extract audio from original MKV with timings from original file.
ffmpeg -i ${VIDEO} -af "aresample=48000:async=1" -map 0:a audio.flac

# Remove subtitle files and large temporary MKV file.
rm subrip-garbled.ass subrip.ass fixed-subs.mkv

