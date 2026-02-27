#!/bin/bash

set -euo pipefail

# Created Fab 21, 2026
# Download the in.webm using the following command:
# yt-dlp "bestvideo+bestaudio" 'https://www.youtube.com/watch?v=ky49LM3FOv4'

# Print video time in seconds:
# ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 in.webm

echo "1. Extract segments from in.webm..."
ffmpeg -ss 02:50:04 -to 02:55:21 -i in.webm -c copy 10_4-4_IrateEight.webm -y
ffmpeg -ss 00:32:39 -to 00:35:07 -i in.webm -c copy 09_1-K_SwingerFlinger.webm -y
ffmpeg -ss 02:07:52 -to 02:10:43 -i in.webm -c copy 08_3-K_Precarious_Pendulums.webm -y
ffmpeg -ss 04:48:42 -to 04:52:17 -i in.webm -c copy 07_6-8_MeltdownMayhem.webm -y
ffmpeg -ss 03:59:28 -to 04:02:14 -i in.webm -c copy 06_5-K_PlatformProblems.webm -y
ffmpeg -ss 03:06:26 -to 03:08:10 -i in.webm -c copy 05_4-K_SpinningSpines.webm -y
ffmpeg -ss 05:07:43 -to 05:09:38 -i in.webm -c copy 04_7-1_LevitationStation.webm -y
ffmpeg -ss 04:52:54 -to 04:55:56 -i in.webm -c copy 03_6-K_SlippySpikes.webm -y
ffmpeg -ss 01:19:39 -to 01:21:41 -i in.webm -c copy 02_2-K_Bopropolis.webm -y
ffmpeg -ss 05:12:59 -to 05:15:14 -i in.webm -c copy 07-3_CrazyClouds.webm -y

echo "2. Create the temporary concatenation list"
rm -f inputs.txt
touch inputs.txt
echo "file '10_4-4_IrateEight.webm'" >> inputs.txt
echo "file '09_1-K_SwingerFlinger.webm'" >> inputs.txt
echo "file '08_3-K_Precarious_Pendulums.webm'" >> inputs.txt
echo "file '07_6-8_MeltdownMayhem.webm'" >> inputs.txt
echo "file '06_5-K_PlatformProblems.webm'" >> inputs.txt
echo "file '05_4-K_SpinningSpines.webm'" >> inputs.txt
echo "file '04_7-1_LevitationStation.webm'" >> inputs.txt
echo "file '03_6-K_SlippySpikes.webm'" >> inputs.txt
echo "file '02_2-K_Bopropolis.webm'" >> inputs.txt
echo "file '07-3_CrazyClouds.webm'" >> inputs.txt

echo "3. Create the Metadata file for Chapters"
echo "Creating chapter metadata..."
cat <<EOF > metadata.txt
;FFMETADATA1
title=Donkey Kong Country Tropical Freeze - Hardest 10 Levels

[CHAPTER]
TIMEBASE=1/1
START=0
END=321
title=4-4: Irate Eight

[CHAPTER]
TIMEBASE=1/1
START=321
END=470
title=1-K Swinger Flinger

[CHAPTER]
TIMEBASE=1/1
START=470
END=645
title=3-K: Precarious Pendulums

[CHAPTER]
TIMEBASE=1/1
START=645
END=861
title=6-8: Meltdown Mayhem

[CHAPTER]
TIMEBASE=1/1
START=861
END=1031
title=5-K: Platform Problems

[CHAPTER]
TIMEBASE=1/1
START=1031
END=1138
title=4-K: Spinning Spines

[CHAPTER]
TIMEBASE=1/1
START=1138
END=1255
title=7-1: Levitation Station

[CHAPTER]
TIMEBASE=1/1
START=1257
END=1441
title=6-K: Slippy Spikes

[CHAPTER]
TIMEBASE=1/1
START=1441
END=1564
title=2-K: Bopropolis

[CHAPTER]
TIMEBASE=1/1
START=1564
END=1697
title=7-3: Crazy Clouds
EOF

echo "4. Join segments and adding chapters into out.mkv..."
ffmpeg -f concat -safe 0 -i inputs.txt -i metadata.txt -map_metadata 1 -c copy out.mkv -y

echo 'SUCCESS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
