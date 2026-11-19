<br/>

**DSI** (*Discord Spotify Integration*) is a small, locally run program that adds a customisable Spotify listening activity, to replace the default Spotify connection. <br/>

<br/>

**DSI** is a lightweight, Python/C++ program with minimal resource usage. <br/>

<br/>

It's easy to run, even easier to configure and features a ton of vast customisation options. <br/>

<br/>

**But why?** <br/>

- If you're someone that likes to see more, different, bigger numbers. <br/>

- If you'd like to customise your activity fields to your heart's content. <br/>

- Unlike the default Spotify behavior, this uses the Activity method, which means it doesn't enter an "away" state and hide itself. <br/>

- Using the Activity also means you can disable it on a per-server level in Discord's Activity Privacy. <br/>

- If you prefer to hide certain songs, you can blacklist individual songs and display your favorites instead. *(>v0.5.2.0537)* <br/>

- Want to occasionally go private? There's an option to pause Rich Presence updating, so you can jam out in peace. *(>v0.11.19.1046)* <br/>

## Download
### [Download latest](https://github.com/EllEff-Git/Discord-Spotify-Integration/releases/latest/download/DSI-Setup.exe)

<br>

<br/>

*Note that the "Spotify Activity" text is determined by your Discord Application's name, and is not set in stone* <br/>

*The pictures are purely demonstrative, and you can set as many large pictures as you'd like, or let Spotify provide the song cover (the small, corner picture only supports one).* <br/>

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


Installation is as easy as unzipping, and the total setup shouldn't take more than 5 minutes. Just head over to Releases, download the latest zip, extract and run the included setup executable. The configuration files are placed in the Local AppData folder, so if you ever wish to uninstall/move the installation, you won't lose your settings. <br/>

For a full breakdown on the prerequisites (Discord/Spotify Developer applications), head to: <br/> 
https://elleffnotelf.com/guides/discord-spotify-integration/. <br/>

<br/>

The basic loop is: a Python script requests data from a linked Spotify account, sends the formatted information to a C++ program, which updates the Discord activity. <br/>

<br/>

To display more information inside your Discord activity (playtime per song, total playcount and tons more), you'll need to use [Spotify Analyser](https://github.com/EllEff-Git/Spotify-Analyzer) (SHA(A)) to generate the necessary files that DSI uses to display statistics. <br/>

*The program is designed and mainly tested as an "addon", if there are issues using it without Spotify Analyser, they may get fixed slower. Highly recommended to use with SHA(A)* <br/>

<br/>

If using DSI with my [Spotify Browser Overlay](https://github.com/EllEff-Git/SBO), you can launch DSI first to disable SBO's own API logic, reducing calls to literally half, and allows SBO to access all of DSI's data *(if using DSI with SHA)*.

*Requires "Enable data hosting" (>v0.8.5.1106)* <br/>

<br/>

Quick note on Spotify's URIs: <br/>
Spotify assigns songs URIs (Uniform Resource Identifier) on a per-market basis, meaning sometimes, you may stumble across the same song from 2+ different markets. They look something like: 'spotify:track:51EC3I1nQXpec4gDk0mQyP'. <br/>
While they're functionally same, they'll have different URIs. The program performs "mapping", where it collects the URIs from songs you listen to, and turns them into keys, when you run the included URImap program. <br/>

*(Basically, they'll look like: "URI:URI2", and the program can check for both, if the first one doesn't match CSV data). This is only relevant if using with SHA, otherwise, there's nothing to do with the URIs* <br/>