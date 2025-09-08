# TubeMate


## Demo
<img src="https://github.com/xnigel/TubeMate/blob/main/demo/TubeMate_v01.01.00%20demo%200.png" width =250> <img src="https://github.com/xnigel/TubeMate/blob/main/demo/TubeMate_v01.01.00%20demo%201.png" width =250> <img src="https://github.com/xnigel/TubeMate/blob/main/demo/TubeMate_v01.01.00%20demo%202.png" width =250> 

<img src="https://github.com/xnigel/TubeMate/blob/main/demo/TubeMate_v01.01.00%20demo%203.png" width =250> <img src="https://github.com/xnigel/TubeMate/blob/main/demo/TubeMate_v01.01.00%20demo%204.png" width =250> <img src="https://github.com/xnigel/TubeMate/blob/main/demo/TubeMate_v01.01.00%20demo%205.png" width =250>

## Description
I created this app so my kids can listen to some relaxing music while doing homework or taking a walk outdoors. By converting the music locally, they don't need to rely on streaming, cell phones, or Wi-Fi. In this case, an old mp3 player or iPod comes in handy.

## Requirement
This program relies on a couple of libraries and plug-ins

1. `yt_dlp` (https://github.com/yt-dlp/yt-dlp)
    
    `yt-dlp` is a feature-rich command-line audio/video downloader with support for thousands of sites. The project is a fork of youtube-dl based on the now inactive youtube-dlc. 

    **Installing:**
    
    run the command in Win or Linux
    ```
    pip install yt_dlp
    ```
2. `ffmpeg` (https://ffmpeg.org/)
FFmpeg is a free and open-source software project that provides a vast suite of libraries and tools for handling video, audio, and other multimedia files and streams.

    **Installing:**
    
    Go to https://ffmpeg.org/download.html
    
    Select Win and then download gyan.dev ---> `ffmpeg-git-full.7z` (compiled for WinOS)
    
    After downloading the package, extract the package to `C:\ffmpeg\` for example. 
    
    Then add the `~\bin\` folder (containning `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe`) add your WinOS PATH.

## Execute the program
If you are an end user, you do not need to know anything about programming, reading source code, or modifying the code.
To use the program directly, you only need to do the following:
1. Download the *.exe file from https://github.com/xnigel/TubeMate/tree/main/dist
2. Place the TubeMate.exe to a local directory of your Win-PC
3. Run it and enter the correct password
4. Download your favorite Youtube music and save them locally.
5. Enjoy your music.

Thanks for using TubeMate.

