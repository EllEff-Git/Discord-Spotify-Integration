<br/>
DSI (Discord Spotify Integration) is a program that adds a customisable activity to Discord, displaying Spotify activity. <br/>


DSI is a lightweight, terminal-based program with effectively no resource requirements (less than a blank Chrome tab). <br/>
It's easy to run, even easier to configure and features over a dozen simple, but vast customisation options. <br/>


But why? <br/>

If you're someone that likes to see more, different, bigger numbers. <br/>

If you'd like to customise your activity fields. <br/>

Unlike the default Spotify behavior, this uses the Activity method, which means it doesn't enter an AFK state and disable the view. <br/>

Maybe you just like to not show your Spotify status, you can just not run the program and it won't show. <br/>


Examples: <br/>

Note that the "Spotify Activity" string is determined by your Discord Application's name, and the "Activity" part is not set in stone <br/>

The pictures are also purely examples, and you can set as many large pictures as you'd like (the small corner one only supports one). <br/>


Default Behavior out of the box
![Imgur Image](https://i.imgur.com/PMFPi4c.png)

Custom text fields before and after the song state
![Imgur Image](https://i.imgur.com/GJkvrZa.png)

Paused state and total stats
![Imgur Image](https://i.imgur.com/RHY6H1Y.png)

No album name, mix of total and per-song stats, shuffle state
![Imgur Image](https://i.imgur.com/ftXcR2I.png)

Fully custom fields in both state and details, repeat state
![Imgur Image](https://i.imgur.com/UR8B7YH.png)


<br/>


Installation is as easy as unzipping a file, and the total setup shouldn't take more than 5 minutes. <br/>


The basic function loop is a Python script which requests data from a linked Spotify account, writing the relevant, formatted fields to a text file, which is read by a C++ program and pushed to Discord's activity field. <br/>


To access more information inside Discord activity (total playtime, total playtime per current song, total playcount and more), you'll need to use [Spotify Analyser](https://github.com/EllEff-Git/Spotify-Analyzer) and install DSI as an addon, of sorts (DSI will run fully independently, but will use the CSV data from Spotify Analyser). <br/>


For further information, installation and instructions: <br/>
https://elleffnotelf.com/guides/Discord-Spotify-Integration <br/>



```
$$$$$$$$\ $$\       $$\       
$$  _____|$$ |      $$ |      
$$ |      $$ |      $$ |      
$$$$$\    $$ |      $$ |      
$$  __|   $$ |      $$ |      
$$ |      $$ |      $$ |      
$$$$$$$$\ $$$$$$$$\ $$$$$$$$\ 
\________|\________|\________|
```