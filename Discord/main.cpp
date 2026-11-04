#define DISCORDPP_IMPLEMENTATION

#define WIN32_LEAN_AND_MEAN
#include <winsock2.h>
#include <ws2tcpip.h>
#include <Windows.h>

#include "discordpp.h"
#include <iostream>
#include <fstream>
#include <thread>
#include <atomic>
#include <string>
#include <functional>
#include <csignal>
#include <chrono>
#include <limits.h>
#include <codecvt>
#include <cstdint>
#include <vector>
#include "json.hpp"

#pragma comment(lib, "Ws2_32.lib")
using json = nlohmann::json;



// version number (Y.MM.DD.HHMM)
std::string DSIDver = "v0";

// the Discord Application ID
std::uint64_t APPLICATION_ID = 0;

// the small corner image name/URL
std::string SmallImage = "";

// an album fallback string (if song + album is too long)
std::string albumFallback = "An Album";

// initialises bools for image(s) failing
// this is not common, but prevents more than 1 failure
// large image failure state
std::atomic<bool> LargeImageFail = false;
// small image failure state
std::atomic<bool> SmallImageFail = false;

// the previous pause state (to compare)
std::atomic<bool> pauseStateOld = false;
// whether the playback stop has been acknowledged (C++ -> Python)
std::atomic<bool> pauseAcknowledged = false;

// a timestamp for checking when the RPC was last updated
std::uint64_t lastUpdate = 0;
// a timestamp for current time
std::uint64_t currentTime = 0;

// the track ID (given by Python, just a counter, basically)
std::uint64_t trackID = 0;
// the previous track ID (to compare)
std::uint64_t oldTrackID = 0;

// flag to control application run state
std::atomic<bool> running = true;
// flag to control rich presence update prints
std::atomic<bool> rpcUpdated = false;

// signal handler to stop the application
void signalHandler(int signum) {
    running.store(false);
}

// function used later to trim any potentially long fields, to fit Discord's max of 128 UTF-16 units
std::string utfTrim(const std::string& input, size_t maxUnits = 113) {
    // if the whole string is empty, falls back to default
    if (input.empty()) return "Listening to Spotify // Data via DSI";

    // converter takes UTF-8 and turns into UTF-16
    std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;

    // utf16 stores the field as as UTF-16 ()
    std::wstring utf16;

    // attempts to turn the string into UTF-16
    try {
        utf16 = converter.from_bytes(input);
    } 
    // if it fails, uses fallback string
    catch (...) {
        return "Listening to Spotify // Data via DSI";
    }

    // variable to count units
    size_t units = 0;
    // variable to store the trimmed name
    std::wstring trimmed;

    // function that checks for invisible characters *inside* the string (previously was only start/end)
    auto isInvisible = [](wchar_t c) {
    return c == L'\t' || c == L'\r' || c == 0x200B || c == 0xFEFF;
    };

    // goes through every character in the string
    for (size_t i = 0; i < utf16.size(); ++i) {
        wchar_t wc = utf16[i];

        // if the current character is an "invisible" one, skips that character (won't get added to trimmed string)
        if (isInvisible(wc)) continue;

        // sets how many UTF-16 units are used
        size_t unitsNeeded = 1;

        // goes through "surrogate pairs" (emojis, etc)
        // looks for valid pairs (high + low)
        if (wc >= 0xD800 && wc <= 0xDBFF) {
            // if the character + 1 is less than the string's size
            if (i + 1 < utf16.size()) {
                // gets the next unit
                wchar_t low = utf16[i + 1];
                // checks if the next unit is a low surrogate
                if (low >= 0xDC00 && low <= 0xDFFF) {
                    unitsNeeded = 2;
                } else {
                    // not a low surrogate = not valid pair, skip
                    break; 
                }
            } else {
                // high at the end, skip
                break;
            }
        }

        // if adding this pair to the string would go over the max, skips
        if (units + unitsNeeded > maxUnits) break;

        // adds the high surrogate to the final string
        trimmed += wc;
        // if there's a valid pair (meaning it used 2 units)
        if (unitsNeeded == 2) {
            // adds the low surrogate, too
            trimmed += utf16[++i];
        }

        // adds the numbers up
        units += unitsNeeded;
    } // for loop close

    // makes sure the string fits discord requirements (2 =< x =< 128 characters)
    if (units < 2) {
        // if it's not, uses fallback string
        trimmed = L"Listening to Spotify // Data via DSI";
    }

    // tries to convert back to utf-8 (which is what Discord wants the text in, for some damn reason)
    try {
        return converter.to_bytes(trimmed);
    }
    // if it fails, reverts back to fallback string 
    catch (...) {
        return "Listening to Spotify // Data via DSI";
    }
}

// function to read a Python packet and return validity as a boolean
bool ReadExact(HANDLE pipe, void* buffer, DWORD size) {
    // how many bytes have been read
    DWORD readSoFar = 0;

    // while there's bytes still left to read
    while (readSoFar < size) {
        // how many bytes are read this loop
        DWORD bytesRead = 0;
        // reads the packet
        if (!ReadFile(
            // passed pipe argument
            pipe,
            // buffer size
            static_cast<char*>(buffer) + readSoFar,
            // bytes left
            size - readSoFar,
            // bytes read in loop
            &bytesRead,
            nullptr
        )) {
            // fail
            return false;
        }

        // pipe closed
        if (bytesRead == 0) {
            // fail
            return false;
        }

        // adds the read bytes to the total
        readSoFar += bytesRead;
    }
    // done
    return true;
}


// main function
int main() {

    // gets the path to LOCALAPPDATA
    std::filesystem::path localAppData = std::getenv("LOCALAPPDATA");

    // sets the path for each file this program accesses
    // discordIDs.json contains the Discord Application ID and small picture name/link (written once by DSI at start)
    std::filesystem::path idDir = localAppData / "DSI" / "discordIDs.json";
    // token.txt is used to (re-)authenticate with Discord without needing to sign in every time
    std::filesystem::path tokenDir = localAppData / "DSI" / "token.txt";

    // makes sure the output console prints in UTF-8 encoding (allows for non-ANSI alphabet, special characters, etc)
    SetConsoleOutputCP(CP_UTF8);

    // empty strings to hold info
    std::string AppID, SIMG;

    // opens the discordIDs.json file
    std::ifstream file(idDir);

    // if the file isn't open
    if (!file) {
        // user inform on error
        std::cerr << "Unable to open Discord configuration: " << idDir << std::endl;
        // stops
        return 1;
    }

    // loads the file as "config"
    json config = json::parse(file);

    // grabs all the required variables
    AppID = config["Discord Application ID"];
    SIMG = config["Small Image Filename"];
    albumFallback = config["Album Fallback"];
    DSIDver = config["Version"];

    // replaces placeholder image key with the one from the JSON (name or URL)
    SmallImage = SIMG;

    // tries to replace the temp variable APPLICATION_ID with AppID (the "real" (live) number from the JSON)
    try {
        APPLICATION_ID = std::stoull(AppID);
    }
    // if it fails for any reason
    catch (...) {
        // sends error message
        std::cerr << "Invalid Application ID" << std::endl;
        // return 1 = stop
        return 1;
    }

    // something something Discord's handler
    std::signal(SIGINT, signalHandler);

    // informs when DSI has successfully launched
    std::cout << "Discord RPC started via DSIdiscord " << std::endl;

    // creates a Discord Client
    auto client = std::make_shared<discordpp::Client>();

    // sets up logging callback
    client->AddLogCallback([](auto message, auto severity) {
      // std::cout << "[" << EnumToString(severity) << "] " << message << std::endl;
    }, discordpp::LoggingSeverity::Info);

    // flag for the RPC being active
    std::atomic<bool> RPCrunning = false;

    // sets up status callback to check client connection
    client->SetStatusChangedCallback([client, &RPCrunning](discordpp::Client::Status status, discordpp::Client::Error error, int32_t errorDetail) {

      // if discord succeeds at finding client, gets ready to change activity info
      if (status == discordpp::Client::Status::Ready) {

        // ensures the RPC isn't already active, sets to true if not and runs
        if (!RPCrunning.exchange(true)) {

            // updates lastUpdate once to prevent required update right away
            lastUpdate = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

            // updates user via stdout
            std::cout << "Loading Discord Status" << std::endl;

            // starts a new thread
            std::thread([client]() {

            // an object that contains the last values of each variable
            struct PlaybackData {
                // song name
                std::string songName = "Loading";
                // album name
                std::string albumName = "An album";
                // song details (track plays, custom text...)
                std::string songStuff = "Discord Spotify Integration";

                // main image url/name
                std::string LargeImage = "";
                // the bottom text/what's shown on large image hover
                std::string LargeText = "DSI";
                // the text to show on the small image hover
                std::string SmallText = "Spotify";

                // large image/bottom text link
                std::string SpotifyURL = "https://github.com/EllEff-Git/Discord-Spotify-Integration";
                // small picture link (the picture is set separately, doesn't change per cycle)
                std::string SmallURL = "https://discord.gg";

                // starting UNIX timestamp
                int64_t unixStart = 0;
                // ending UNIX timestamp
                int64_t unixEnd = 0;
                // the track number
                int64_t trackID = 0;

                // current Spotify playback state (is API sending data or is Spotify fully closed)
                bool playbackState = false;
                // is Spotify playback paused (API is up, sending data, but paused)
                bool pauseState = false;
            };

            // a reference to the data structure
            PlaybackData currentData;

            // gets the STDIN from python
            HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
            // byte count variable
            DWORD byteCount = 0;

            // starts a loop to refresh info
            while (running) {

                // a boolean to check if an update is required due to timer
                bool requiredUpdate = false;
                // a boolean to check song status
                bool songChanged = false;
                // a boolean to check pause state change
                bool pauseChanged = false;

                // updates current time to match, well, current time
                currentTime = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

                // checks if the last time RPC was updated was more than 15 seconds ago
                if ((lastUpdate + 15) < currentTime) {
                    // changes the requiredUpdate to true to trigger an update
                    requiredUpdate = true;
                }

                // boolean to check if Python has sent a new packet
                bool newPythonPacket = PeekNamedPipe(hStdin, nullptr, 0, nullptr, &byteCount, nullptr);

                // if there *is* a new packet from Python in stdin and it's a full packet
                if (newPythonPacket && byteCount >= sizeof(uint32_t)) {

                    // the stdin byte size variable
                    uint32_t stdinSize = 0;
                    // stdin read byte size variable
                    DWORD readSize = 0;

                    // checks the packet to ensure it's available (checks the size of the packet, ensures the whole thing is actually received first)
                    bool packetReady = PeekNamedPipe(hStdin, &stdinSize, sizeof(stdinSize), &readSize, nullptr, nullptr);

                    // if the packet is ready to be read
                    if (packetReady && readSize == sizeof(stdinSize)) {
                        
                        // the packet size gets stored
                        uint32_t packetSize = ntohl(stdinSize);
                        // a max size for the packet (X * bytes), currently set to 1MB, doesn't really matter, generally ~1KB (1000 Bytes)
                        constexpr uint32_t maxSize = 1024 * 1024;

                        // ensures the packet size (has to have *a* size, can't be above max)
                        if ((packetSize > 0) && (packetSize <= maxSize) && (byteCount >= (sizeof(uint32_t) + packetSize))) {

                            // how much of the header has been consumed (eaten)
                            uint32_t headerEaten = 0;

                            // checks the packet's header contents via helper (consumes)
                            if (!ReadExact(hStdin, &headerEaten, sizeof(headerEaten))) {
                                // couldn't read the packet, waits 500ms
                                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                                // resets loop
                                continue;
                            }

                            // makes a read buffer (consumes)
                            std::vector<char> buffer(packetSize);
                            
                            // checks the packet's contents via helper (uses the consumed packet)
                            if (!ReadExact(hStdin, buffer.data(), packetSize)) {
                                // couldn't read the packet, waits 500ms
                                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                                // resets loop
                                continue;
                            }

                            // forms a string packet from the buffer (packet)
                            std::string packet(buffer.begin(), buffer.end());
                            // data packets are JSON (dictionaries)
                            json data;

                            // packet is empty (shouldn't happen)
                            if (packet.empty()) {
                                // waits 500ms
                                std::this_thread::sleep_for(std::chrono::milliseconds(500));
                                // resets loop
                                continue;
                            }

                            // packet read in try to prevent blow up
                            try {
                                // parses the received packet into a dictionary form 
                                data = json::parse(packet);
                            }
                            // if it blows up
                            catch (const json::exception& e) {
                                // sends error message
                                std::cerr << "Error with DSI data:" << e.what() << std::endl;
                                // waits a couple seconds (hopefully new, not broken packet arrives)
                                std::this_thread::sleep_for(std::chrono::seconds(3));
                                // reset loop
                                continue;
                            }

                            // tries to reassign all the variables from the data packet
                            try {
                                // grabs the boolean that represents whether the playback is currently on or not
                                bool newPlaybackState = data["Playback State"].get<bool>();

                                // if the stored playback state doesn't match the new one
                                if (newPlaybackState != currentData.playbackState) {
                                    // overrides the pause change bool (it doesn't have any impact on the program, easiest bool to force an update)
                                    pauseChanged = true;
                                    // sets the current data to match new playback state (if this is from True -> False, it gets overwritten with the next check)
                                    currentData.playbackState = newPlaybackState;
                                }
                                
                                // if playback is cut from Spotify (stopped playing)
                                if (currentData.playbackState == false && pauseAcknowledged == false) {
                                    // sends a message, if it hasn't been sent yet (prevents spam/Python side UI bugs)
                                    std::cout << "Paused Discord RPC" << std::endl;
                                    // sets the boolean to true so it doesn't get re-sent
                                    ::pauseAcknowledged = true;
                                    // clears the currently active Discord Rich Presence (activity)
                                    client->ClearRichPresence();
                                    // waits a few seconds
                                    std::this_thread::sleep_for(std::chrono::seconds(3));
                                    // reset loop
                                    continue;
                                }
                                // if playback is cut, and the pause has been sent to Python
                                else if (currentData.playbackState ==  false && pauseAcknowledged == true) {
                                    // waits a few seconds
                                    std::this_thread::sleep_for(std::chrono::seconds(3));
                                    // reset loop
                                    continue;
                                }

                                // a packet sent to reset image bools manually
                                bool imageFlag = data["Reset Images"].get<bool>();
                                // request to reset the image flags
                                if (imageFlag) {
                                    // sets both image fail states to false
                                    ::LargeImageFail = false;
                                    ::SmallImageFail = false;
                                    // reset loop (this packet doesn't contain anything else, just the state and image flags)
                                    continue;
                                }

                                // variables get grabbed from packet (ensures they use the correct type)
                                currentData.songName = data["Song"].get<std::string>();
                                currentData.albumName = data["Album"].get<std::string>();
                                currentData.songStuff = data["State"].get<std::string>();
                                currentData.LargeImage = data["Large Image"].get<std::string>();
                                currentData.LargeText = data["Large Text"].get<std::string>();
                                currentData.SmallText = data["Small Text"].get<std::string>();
                                currentData.SpotifyURL = data["Spotify URL"].get<std::string>();
                                currentData.SmallURL = data ["Small URL"].get<std::string>();
                                currentData.unixStart = data["UNIX Start"].get<int64_t>();
                                currentData.unixEnd = data["UNIX End"].get<int64_t>();
                                currentData.pauseState = data["Pause"].get<bool>();
                                currentData.trackID = data["Track ID"].get<int64_t>();
                            }
                            // if it fails
                            catch(const std::exception& e) {
                                // sends error message
                                std::cerr << "Error with DSI data:" << e.what() << std::endl;
                                // waits a couple seconds
                                std::this_thread::sleep_for(std::chrono::seconds(2));
                                // reset loop
                                continue;
                            }

                            // checks if the song has changed since the last update (trackIDs don't match)
                            // if it has, changes songChanged to true - this ensures the song changing or being paused gets caught
                            if (currentData.trackID != oldTrackID) {
                                // sets the old value to match new
                                oldTrackID = currentData.trackID;
                                // sets the boolean to true so the next check goes through
                                songChanged = true;
                            }
                            // checks if the song has been paused since last check
                            // if it has (the pause state is not the previous state (meaning it goes from pause -> unpause or vice versa))
                            if (currentData.pauseState != pauseStateOld.load()) {
                                // sets the boolean to true so the next check goes through
                                pauseChanged = true;
                                // updates the previous pause state to match current
                                pauseStateOld.store(currentData.pauseState);
                            }

                            // these 2 checks are done to see if the album should be left in or dropped to keep the string integrity
                            // checks if the length of the songName (details) field *with* album is eq or less than 103 (cap of 108 for that field)
                            if ((currentData.songName + currentData.albumName).length() <= 103) {
                                currentData.songName = currentData.songName + " " + currentData.albumName;
                            }
                            // checks if the length of the songName (details) field *with* fallback string is eq or less than 108 (cap of 108 for that field)
                            else if ((currentData.songName + albumFallback).length() <= 108) {
                                currentData.songName = currentData.songName + " " + albumFallback;
                            }
                        } // packet size check close
                    } // packet ready check close
                } // new packet arrived check close

                // only pushes the update if everything is fine, and the song has changed/paused/update is required
                // I found that if no update is pushed for a longer period of time, Discord may just lose the status completely and drop it
                if (songChanged || pauseChanged || requiredUpdate) {

                    // if the update isn't a timer-based one (meaning something has "actually changed")
                    if (songChanged || pauseChanged) {
                        // updates the rpc update boolean to ensure it prints rpc status
                        rpcUpdated = false;
                    }

                    // ensures the fields doesn't exceed the character limit (128 is what Discord claims, 108 is pretty safe)
                    currentData.songName = utfTrim(currentData.songName);
                    currentData.songStuff = utfTrim(currentData.songStuff);
                    currentData.LargeText = utfTrim(currentData.LargeText);
                    currentData.SmallText = utfTrim(currentData.SmallText);

                    // sets up rich presence details
                    discordpp::Activity activity;

                    // sets the rich presence to "Listening to:"
                    activity.SetType(discordpp::ActivityTypes::Listening);
                    // sets the "state" (song playtime, count, etc) - in games, equivalent is "Playing solo/duo..."
                    activity.SetState(currentData.songStuff);
                    // sets the "details" (song name) - in games, equivalent is "Competitive"
                    activity.SetDetails(currentData.songName);
                    // stateURL only works when a party size is set - which isn't available with this program
                    // activity.SetStateUrl("https://discord.com");

                    // sets up the rich presence assets (pictures)
                    discordpp::ActivityAssets assets;

                    // Large Image is the main picture
                    // if the field is still empty, doesn't push it through (will cause a fail otherwise)
                    if (currentData.LargeImage.empty() || currentData.LargeImage[0] == ' ') {
                        // if it hasn't been registered yet
                        if (!LargeImageFail) {
                            // user inform
                            std::cout << "Large Image is empty or faulty" << std::endl;
                        }
                    }
                    // not empty
                    else {
                        // if the large image has failed once, doesn't try to push a new one
                        if (LargeImageFail) {}
                        // if the field isn't empty or "faulty" on the first go (or hasn't failed yet)
                        else {
                            // sets the image from Python data
                            assets.SetLargeImage(currentData.LargeImage);
                        }
                    }

                    // Large text appears on hovering the large image (and under the song info)
                    assets.SetLargeText(currentData.LargeText);
                    // Large URL is the Spotify link to the selected type (Artist, Song, Album, Playlist) of the currently playing track
                    assets.SetLargeUrl(currentData.SpotifyURL);

                    // Small URL is the link when you click the smaller picture
                    assets.SetSmallUrl(currentData.SmallURL);

                    // Small Image is the circle in the corner of Large Image, text is on hover
                    // if the field is still empty, doesn't push it through (will cause a fail otherwise)
                    if (SmallImage.empty() || SmallImage[0] == ' ') {
                        // if it hasn't been registered yet
                        if (!SmallImageFail) {
                            // user inform
                            std::cout << "Small Image is empty or faulty" << std::endl;
                        }
                    }
                    // not empty
                    else {
                        // if the small image has failed once, doesn't try to push a new one
                        if (SmallImageFail) {}
                        // if the field isn't empty or "faulty" on the first go (or hasn't failed yet)
                        else {
                            // sets the image from file variable
                            assets.SetSmallImage(SmallImage);
                        }
                    }
                    // Small text is the text that appears when you hover over the small picture
                    assets.SetSmallText(currentData.SmallText);

                    // pushes assets to "activity"
                    activity.SetAssets(assets);

                    // sets up the rich presence timestamps
                    discordpp::ActivityTimestamps timestamps;

                    // sets the song's start time (in UNIX timestamp)
                    timestamps.SetStart(currentData.unixStart);
                    // sets the song's end time (in UNIX timestamp)
                    timestamps.SetEnd(currentData.unixEnd);
                    // pushes timestamps to "activity"
                    activity.SetTimestamps(timestamps);

                    // updates user rich presence/activity with formed info
                    client->UpdateRichPresence(activity, [](discordpp::ClientResult result) {

                        // if it goes through fine
                        if (result.Successful()) {

                            // updates the last update timestamp to match system time
                            lastUpdate = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

                            // checks if rpc has been updated already, only prints if not
                            if (!rpcUpdated) {
                                // updates user
                                std::cout << "Rich Presence updated" << std::endl;
                                // sets the bool to true, to prevent double-prints
                                rpcUpdated = true;
                            }

                            // sets the pause acknowledge boolean to false, since the RPC has now been successfully updated -> next fail is a "real" fail
                            ::pauseAcknowledged = false;
                        }
                        // if it fails to push user RPC update
                        else {
                            // sets the update boolean to false
                            rpcUpdated = false;
                            
                            // if the error message contains "connection error"
                            if ((result.Error().find("Connection failed")!=std::string::npos)) {
                                // sends generic connection error (this is more or less your connection -> Discord (sometimes their API, rare))
                                std::cout << "Rich Presence update failed: Issue connecting to Discord API" << std::endl;
                                // sets both picture fail states to false (not the cause)
                                ::SmallImageFail = false;
                                ::LargeImageFail = false;
                            }
                            // if the error message contains "LargeImage"
                            else if ((result.Error().find("LargeImage")!=std::string::npos) && !LargeImageFail) {
                                // large image error inform
                                std::cout << "Rich Presence update failed: Large Image error" << std::endl;
                                // sets the fail states
                                ::LargeImageFail = true;
                                ::SmallImageFail = false;
                            }
                            // if the error message contains "SmallImage"
                            else if ((result.Error().find("SmallImage")!=std::string::npos) && !SmallImageFail) {
                                // small image error inform
                                std::cout << "Rich Presence update failed: Small Image error" << std::endl;
                                // sets the fail states
                                ::SmallImageFail = true;
                                ::LargeImageFail = false;
                            }
                            // if the error is an empty external asset error
                            // this is usually an issue with the Discord -> Spotify image grab (nothing you can do)
                            // *typically* this means that Discord auth expired and needs to reconnect (roughly a weekly thing), Python has inform to advise for that
                            else if ((result.Error().find("external assets")!=std::string::npos)) {
                                // asset error user inform
                                std::cout << "Rich Presence update failed: Discord API asset error" << std::endl;
                                // sets both picture fail states to false (likely not the cause)
                                ::SmallImageFail = false;
                                ::LargeImageFail = false;
                            }
                            // if the error is something else
                            else {
                                // generic issue with error included
                                std::cerr << "Rich Presence update failed:" << result.Error() << std::endl;
                                // sets both picture fail states to false (likely not the cause)
                                ::SmallImageFail = false;
                                ::LargeImageFail = false;
                            }
                        } // else close
                        
                    }); // UpdateRichPresence close

                } // if there's a change/update requirement close

                // if the song/pause hasn't changed and 15s hasn't passed
                else {
                    // pauses the thread for a bit (prevents crazy CPU spikes)
                    std::this_thread::sleep_for(std::chrono::seconds(2));
                    // goes back to start of loop
                    continue;
                }
                
                // pauses the update loop for 2 seconds
                std::this_thread::sleep_for(std::chrono::seconds(2));
                
                } // while(running) close bracket

                // detaches itself from the main thread so as to not stop the discord communications updates
                }).detach(); // thread close bracket

            } // if !RPC check

        } // closes the "if status ready" check 

        // if the status for Discord client isn't ready for some reason (auth fail, something else?)
        else if (error != discordpp::Client::Error::None) {
            // user inform
            std::cerr << "Failed to connect to Discord\nCPPFAIL" << std::endl;
        }
    }); // client callback close bracket

// initializes variables for tokens and time
std::string savedAccessToken, savedRefreshToken;
int64_t savedExpiryTime = 0;

// reads the token.txt file
std::ifstream tknFile(tokenDir);
if (tknFile.is_open()) {
    std::getline(tknFile, savedAccessToken);
    std::getline(tknFile, savedRefreshToken);
    tknFile >> savedExpiryTime;
    tknFile.close();
}

// gets current time in UNIX
int64_t currentTime = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

// saves tokens in token.txt when called
auto saveToken = [tokenDir](const std::string& access, const std::string& refresh, int64_t expiry) {
    std::ofstream tknFile(tokenDir);
    if(tknFile.is_open()) {
        tknFile << access << "\n" << refresh << "\n" << expiry << "\n";
        tknFile.close();
    } else {
        std::cerr << "Failed to save token\nCPPFAIL" << std::endl;
    }
};

// starts Discord connection
auto connectWithToken = [&](const std::string& access) {
    client->UpdateToken(discordpp::AuthorizationTokenType::Bearer, access, [client](discordpp::ClientResult result) {
        // if the token is updated successfully
        if(result.Successful()) {
            // updates user
            std::cout << "Token loaded, connecting to Discord\n" << std::endl;
            // connects to the client with the token
            client->Connect();
        // if it's not
        } else {
            std::cerr << "Failed to update token\nCPPFAIL" << std::endl;
        }
    });
};

// if access token is found and not expired, uses it, otherwise makes a new one
if (!savedAccessToken.empty() && currentTime < savedExpiryTime) {

    // token is fine, uses it
    connectWithToken(savedAccessToken);
}
// if token is expired (or not found)
else {
    // token invalid/expired, reauthenticating
    auto codeVerifier = client->CreateAuthorizationCodeVerifier();

    // some authorisation stuff, didn't write this, thanks SDK!
    discordpp::AuthorizationArgs args{};
    args.SetClientId(APPLICATION_ID);
    args.SetScopes(discordpp::Client::GetDefaultPresenceScopes());
    args.SetCodeChallenge(codeVerifier.Challenge());

    // goes to auth the user
    client->Authorize(args, [&, client, codeVerifier](auto result, auto code, auto redirectUri) {
        if(!result.Successful()) {
            std::cerr << "Authentication error\nCPPFAIL" << std::endl;
            return;
        }

        // updates user on status
        std::cout << "Authorised Discord, exchanging token\n" << std::endl;

        // client sign-in
        client->GetToken(APPLICATION_ID, code, codeVerifier.Verifier(), redirectUri,
            [&, client](discordpp::ClientResult result,
                std::string accessToken,
                std::string refreshToken,
                discordpp::AuthorizationTokenType tokenType,
                int32_t expiresIn,
                std::string scope) {

            // not successful
            if(!result.Successful()) {
                // user inform
                std::cerr << "Failed to get access token\nCPPFAIL" << std::endl;
                // stop C++
                return;
            }
            // gets token expiration time by taking current system UNIX time and adding expiration length
            int64_t expiryTime = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now()) + expiresIn;

            // store both access token and refresh token + time
            saveToken(accessToken, refreshToken, expiryTime);
            // calls the connect with a new token
            connectWithToken(accessToken);

        }); // closes the GetToken method
      });
    } // closes the auth via Discord method

    // keeps running to allow program to receive events and callbacks
    while (running) {
        discordpp::RunCallbacks();
        // re-checks every 1 second (standard, set by Discord)
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }

    return 0;
}