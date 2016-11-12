#!/bin/bash

# 1080p Anime with ASS Subtitles to DVD converter script.
# Written by Robert Ian Hawdon (https://robertianhawdon.me.uk) 2016
# Tested on Ubuntu 16.04
# Requires ffmpeg, mencoder

########
# NTSC #
########

# Resize video to 480p at 23.976 FPS.
mencoder -ovc lavc -of mpeg -mpegopts format=dvd:tsaf -vf scale=720:480 -lavcopts vcodec=mpeg2video:vbitrate=4100:keyint=18:vstrict=0:aspect=16/9 -ofps 24000/1001 -o dvd-video.mpg "subtitled.mkv"

# DVD encode audio (ac3).
ffmpeg -i audio.flac -af "aresample=48000:async=1" -target ntsc-dvd dvd-audio.ac3

# Mux video and audio files with NAV Packets at 23.976 FPS - Fully DVD complient.
ffmpeg -i dvd-video.mpg -i dvd-audio.ac3 -vcodec copy -acodec copy -f vob -target ntsc-dvd -r 24000/1001 dvd-ntsc-23.976.mpg
