#!/bin/sh

rm */*.ts
rm frames.txt 
for f in $(ls */*.mp4); do
    FRAMES=`ffmpeg -i $f -c copy -bsf:v h264_mp4toannexb -f mpegts $f.ts 2>&1 | grep "frame=" | awk '{print $2}'`
    echo $f $FRAMES
    echo $f $FRAMES >> frames.txt
done

CONCAT=$(echo $(ls */*.ts) | sed -e "s/ /|/g")

ffmpeg -i "concat:$CONCAT" -c copy -bsf:a aac_adtstoasc pup.mp4

rm */*.ts

echo "Done"

