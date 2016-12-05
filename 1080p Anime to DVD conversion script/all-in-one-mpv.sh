#!/bin/bash

# 1080p Anime with ASS Subtitles to DVD converter script.
# Written by Robert Ian Hawdon (https://robertianhawdon.me.uk) 2016
# Tested on Ubuntu 16.04
# Requires awk, mkvtoolnix, ffmpeg, mencoder, mpv

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
mpv "fixed-subs.mkv" -o "subtitled.mp4" --sid 2 --sub-ass --mc 0 --no-audio --ovc=libx264 --ovcopts=crf=15,subq=4,level=-1,threads=auto

# Extract audio from original MKV with timings from original file.
ffmpeg -i ${VIDEO} -af "aresample=48000:async=1" -map 0:a audio.flac

# Remove subtitle files and large temporary MKV file.
rm subrip-garbled.ass subrip.ass fixed-subs.mkv

#######
# PAL #
#######

# Resize video to 576p and speed up playback to 25 FPS.
ffmpeg -i "subtitled.mp4" -vf "setpts=N/(25*TB),scale=720:576" -b:v 4100k -f vob -target pal-dvd dvd-video25.mpg

# DVD encode audio (ac3) speeding up from 23.976 FPS to 25 FPS (PAL 4% Speed up).
ffmpeg -i audio.flac -af "asetpts=(23976/25000)*PTS,aresample=48000:async=1:min_comp=0.01:comp_duration=1:max_soft_comp=100000000:min_hard_comp=0.3" -target pal-dvd dvd-audio25.ac3

# Mux video and audio files with NAV Packets - Fully DVD complient.
ffmpeg -i dvd-video25.mpg -i dvd-audio25.ac3 -vcodec copy -acodec copy -f vob -target pal-dvd dvd-pal-25.mpg

########
# NTSC #
########

# Resize video to 480p at 23.976 FPS.
mencoder -ovc lavc -of mpeg -mpegopts format=dvd:tsaf -vf scale=720:480 -lavcopts vcodec=mpeg2video:vbitrate=4100:keyint=18:vstrict=0:aspect=16/9 -ofps 24000/1001 -o dvd-video.mpg "subtitled.mp4"

# DVD encode audio (ac3).
ffmpeg -i audio.flac -af "aresample=48000:async=1" -target ntsc-dvd dvd-audio.ac3

# Mux video and audio files with NAV Packets at 23.976 FPS - Fully DVD complient.
ffmpeg -i dvd-video.mpg -i dvd-audio.ac3 -vcodec copy -acodec copy -f vob -target ntsc-dvd -r 24000/1001 dvd-ntsc-23.976.mpg
