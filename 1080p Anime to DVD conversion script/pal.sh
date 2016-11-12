#!/bin/bash

# 1080p Anime with ASS Subtitles to DVD converter script.
# Written by Robert Ian Hawdon (https://robertianhawdon.me.uk) 2016
# Tested on Ubuntu 16.04
# Requires ffmpeg

#######
# PAL #
#######

# Resize video to 576p and speed up playback to 25 FPS.
ffmpeg -i "subtitled.mkv" -vf "setpts=N/(25*TB),scale=720:576" -b:v 4100k -f vob -target pal-dvd dvd-video25.mpg

# Extract audio from original MKV with timings from original file.
ffmpeg -i ${VIDEO} -af "aresample=48000:async=1" -map 0:a audio.flac

# DVD encode audio (ac3) speeding up from 23.976 FPS to 25 FPS (PAL 4% Speed up).
ffmpeg -i audio.flac -af "asetpts=(23976/25000)*PTS,aresample=48000:async=1:min_comp=0.01:comp_duration=1:max_soft_comp=100000000:min_hard_comp=0.3" -target pal-dvd dvd-audio25.ac3

# Mux video and audio files with NAV Packets - Fully DVD complient.
ffmpeg -i dvd-video25.mpg -i dvd-audio25.ac3 -vcodec copy -acodec copy -f vob -target pal-dvd dvd-pal-25.mpg

