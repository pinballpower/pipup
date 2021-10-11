# Research

## Video player

One of the major challenges was it to find a video player than can seamless play and loop multiple videos. Unfortunately that wasn't easy to do:

### omxplayer

omxplayer needs some time to start a new video playback. Another problem is that it can't seamless loop a video. 
The idea therefore was to use one bug video file and just seek within this file. However, the DBus interface isn't performant enough
to do this on an exact frame. 

## VLC

Most of the problems are the same with VLC. The socket interface performs a bit better, but I wasn't able to implement looping on exact frames

## hello_video

This is a very trivial and minimalistic video player, develped as a simple demeonstration how to use the hardware video decoder of the Raspberry Pi. 
It can't deal with container format, but requires a native H264 data stream. Adafruit has expanded it to support seamless looping.
One crucial feature that's required for background video is a pause/resume funtionality. This was missing. 
This has been implemented by me now: [https://github.com/pinballpower/pi_hello_video](https://github.com/pinballpower/pi_hello_video)

