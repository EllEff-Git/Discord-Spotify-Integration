<br/>

**DSI** (*Discord Spotify Integration*) is a program that adds a customisable activity to Discord, displaying Spotify activity. <br/>

<br/>

**DSI** is a lightweight, terminal-based program with effectively no resource requirements (less than a blank Chrome tab). <br/>

<br/>

It's easy to run, even easier to configure and features over a dozen simple, but vast customisation options. <br/>

<br/>

**But why?** <br/>

- If you're someone that likes to see more, different, bigger numbers. <br/>

- If you'd like to customise your activity fields to your heart's content. <br/>

- Unlike the default Spotify behavior, this uses the Activity method, which means it doesn't enter an AFK state and disable the view. <br/>

- Using the Activity also means you can disable it on a per-server level in Discord's Activity Privacy <br/>

<br/>

*Note that the "Spotify Activity" string is determined by your Discord Application's name, and the "Activity" part is not set in stone* <br/>

*The pictures are also purely examples, and you can set as many large pictures as you'd like (the small corner one only supports one, (for now?)).* <br/>

<br/>

**Examples:** <br/>

Default look out of the box: <br/>
![Imgur Image](https://i.imgur.com/PMFPi4c.png)

Custom text fields before and after the song state: <br/>
![Imgur Image](https://i.imgur.com/GJkvrZa.png)

Paused state and total stats: <br/>
![Imgur Image](https://i.imgur.com/RHY6H1Y.png)

No album name, mix of total and per-song stats, shuffle state: <br/>
![Imgur Image](https://i.imgur.com/ftXcR2I.png)

Fully custom fields in both state and details, repeat state: <br/>
![Imgur Image](https://i.imgur.com/UR8B7YH.png)


<br/>


Installation is as easy as unzipping, and the total setup shouldn't take more than 5 minutes. <br/>

<br/>

The basic function loop is a Python script which requests data from a linked Spotify account, writing the relevant, formatted fields to a text file, which is read by a C++ program and pushed to Discord's activity field. <br/>

<br/>

Once started, the program automatically re-authenticates with both Discord and Spotify, allowing you to keep it open for as long as you want. <br/>

<br/>

To access more information inside Discord activity (total playtime, total playtime per current song, total playcount and more), you'll need to use [Spotify Analyser](https://github.com/EllEff-Git/Spotify-Analyzer) and install DSI as an "addon" (DSI will run fully independently, but will use the CSV data from Spotify Analyser). <br/>

<br/>

Quick note on Track URIs: <br/>
Spotify assigns URIs on a per-market basis, meaning sometimes, you may stumble across the same song from 2 different markets. <br/>
While they're functionally same, they'll have different Track URIs. This obviously makes it impossible to check for, unless... <br/>
The program allows for "mapping", where it collects the Track URIs from songs you listen to, and turns them into keys when you run the included URImap program. <br/>
(Basically, they'll look like: "URI:URI2", and the program can check for both keys, if the first doesn't match records) <br/>

<br/>

For further information, installation and instructions: <br/>
https://elleffnotelf.com/guides/Discord-Spotify-Integration <br/>

<br/>

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