Hi!


This is standalone program that ties your Spotify status to Discord rich presence, allowing for more customisation.

It can also function as a quasi-addon to my Spotify streaming history analyser, giving you more information inside Discord activity (total playtime, total playtime per active song, etc) 


https://elleffnotelf.com



```
How to use:

    1. Create a Spotify App in the Developer Dashboard at https://developer.spotify.com/dashboard 
        (information doesn't matter, just enter whatever you'd like - do read step 3 regarding URI, though)

    2. Copy your Client ID and Client Secret keys and a redirect URI to the main file in their respective fields
        Note that the URI doesn't really matter, it just has to match in the file and the dashboard 
        If unsure, just use "http://127.0.0.1:" and choose a 4-digit port, e.g: "4444" or "6969"

    3. Run the tool


    If you'd like more stats, you'll need to use this as tool inside the streaming history analyser: 

    1. Place this folder inside the streaming history analyser
        Should look like
            Spotify Analyzer |
                Data
                DSI
                spotify.py
                README.md

    2. Make sure to run the streaming analyser at least once, following its guide, to generate data for this tool to work off of

    

$$$$$$$$\ $$\       $$\       
$$  _____|$$ |      $$ |      
$$ |      $$ |      $$ |      
$$$$$\    $$ |      $$ |      
$$  __|   $$ |      $$ |      
$$ |      $$ |      $$ |      
$$$$$$$$\ $$$$$$$$\ $$$$$$$$\ 
\________|\________|\________|
```
