# Installation and configuration

## Clone from Github

Clone the software from Github:

```
git clone https://github.com/pinballpower/pipup
```

## Install required software

```
cd pipup/scripts
sudo ./install-packages
```

## Copy PUPPack data

Use the tool of your choice to copy the PUPPack video files to the Raspberry Pi (e.g. scp)

## Prepare videos

PiPUP requires the videos to be formated as plain H264 data streams without any container around it.
Therefore, you can't use the MP4 files from a PUPPack directly.
There's a simple script that converts all MP4 files to H264 data streams. Other formats are not 
supported today.

```
cd pipup/scripts
./convert-files-h264 <puppack-base-directory>
```

## Start server

Now you can start the server:

```
cd pipub/player
python3 pupserver264.py <puppack-base-directory> <screennumber>
```

## Test server

To test that the server does something, just send an event via the web API, e.g.

```
curl http://localhost:5000/trigger/<eventname>
```

You need to use an event from the PUP pack that's defined for the screen you're using.
