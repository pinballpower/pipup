#!/bin/bash

rm */*.ts
rm metadata.txt
rm chapters.txt
rm metadata.txt
rm fileinfo.txt
rm tmp.mp4
rm pupvido.mp4
END=-1
for f in $(ls */*.mp4); do
    START=$((END+1))
    FRAMES=`ffmpeg -i $f -c copy -bsf:v h264_mp4toannexb -f mpegts $f.ts 2>&1 | grep "frame=" | awk '{print $2}'`
    DURATION=`ffprobe -i $f -show_format 2>/dev/null | grep duration | awk -F= '{print $2}'`
    MILLISECONDS=`echo $DURATION \* 1000 | bc | awk -F. '{print $1}'`
    END=$((START+MILLISECONDS))
    echo $f $FRAMES $DURATION $MILLISECONDS $START $END
    echo $f $FRAMES $DURATION $MILLISECONDS $START $END >> fileinfo.txt
    echo >> chapters.txt
    echo "[CHAPTER]" >> chapters.txt
    echo "TIMEBASE=1/1000" >> chapters.txt
    echo "START=$START" >> chapters.txt
    echo "END=$END" >> chapters.txt
    echo "title=$f" >> chapters.txt
done

CONCAT=$(echo $(ls */*.ts) | sed -e "s/ /|/g")

ffmpeg -i "concat:$CONCAT" -c copy -bsf:a aac_adtstoasc tmp.mp4
ffmpeg -i tmp.mp4 -f ffmetadata metadata.txt
cat chapters.txt >> metadata.txt
ffmpeg -i tmp.mp4 -i metadata.txt -map_metadata 1 -codec copy pupvideo.mp4

rm */*.ts
rm tmp.mp4

echo "Done"

