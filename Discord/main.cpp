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
std::string DSIDver = "v0.5.6.1330";

// initialises the Discord Application ID
std::uint64_t APPLICATION_ID = 0;

// initialises a default small icon of nothing
std::string SmallImage = "";

// sets up an album fallback string
std::string albumFallback = "An Album";

// initialises bools for image(s) failing
// this is not common, but prevents more than 1 failure
// large image failure state
std::atomic<bool> LargeImageFail = false;
// small image failure state
std::atomic<bool> SmallImageFail = false;

// initialises the pause state that gets pulled from songdata.txt
std::atomic<bool> pauseState = false;
// stores the previous pause state
std::atomic<bool> pauseStateOld = false;

// initialises a timestamp for checking when the RPC was last updated
std::uint64_t lastUpdate = 0;
// initialises a timestamp for current time
std::uint64_t currentTime = 0;

// initialises a track ID variable
std::uint64_t trackID, oldTrackID = 0;

// flag to control application run state (starts as true to start running)
std::atomic<bool> running = true;

// flag to control rich presence update prints
std::atomic<bool> rpcUpdated = false;



// signal handler to stop the application
void signalHandler(int signum) {
    running.store(false);
}



// directory manager
std::string pathFinder() {
    char buffer[MAX_PATH];
    GetModuleFileNameA(NULL, buffer, MAX_PATH);
    std::string path(buffer);
    size_t pos = path.find_last_of("\\/");
    return (std::string::npos == pos) ? "" : path.substr(0, pos);
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



int main() {

    // gets the path to the current directory
    std::string cppDir = pathFinder();

    // sets the path for each file this program accesses
    // ids.txt contains the Discord Application ID and small picture name/link (written once by DSI at start)
    std::string idDir = cppDir + "\\" + "ids.txt";
    // songData.txt gets automatically updated by DSI with song name, time, custom fields, everything
    std::string sdDir = cppDir + "\\" + "songData.txt";
    // token.txt is used to (re-)authenticate with Discord
    std::string tokenDir = cppDir + "\\" + "token.txt";

    // makes sure the output console prints in UTF-8 encoding (allows for non-ANSI alphabet, special characters, etc)
    SetConsoleOutputCP(CP_UTF8);

    // opens ids.txt, stops the program if can't (can't run the program without AppID)
    std::ifstream file(idDir);
    if (!file.is_open()) {
        std::cerr << "Failed to open/read ids.txt" << std::endl;
        return 1;
    }

    // creates "line" (placeholder string) and lineNum (a counter)
    std::string line;
    int lineNum = 0;

    // creates empty strings to hold info later
    std::string AppID, SIMG;

    while (std::getline(file, line)) {
        // goes through and finds where the "=" sign is, then takes the part after it
        line = line.substr(line.find_first_not_of(" \t"), line.find_last_not_of(" \t") - line.find_first_not_of(" \t") + 1);
        size_t eqPos = line.find("=");
        if (eqPos != std::string::npos) {
            std::string value = line.substr(eqPos + 1);

            // checks if there's empty space
            if (!value.empty() && value[0] == ' ')
                // removes any empty space
                value.erase(0, 1);

            // the first line is AppID, replaces the empty string
            if (lineNum == 0) AppID = value;
            // second line is Small Image
            else if (lineNum == 1) SIMG = value;
            // third (last) line is the album fallback string
            else if (lineNum == 2) albumFallback = value;

            // adds 1 to lineNum so it moves to next line
            ++lineNum;
        }
    }

    // closes the ids.txt
    file.close();

    // replaces placeholder image key with the ones from ids.txt
    SmallImage = SIMG;

    // tries to replace the temp variable APPLICATION_ID with AppID (the "real" (live) number from ids.txt)
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
    std::cout << "Discord RPC started via DSIdiscord " << DSIDver << std::endl;

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

            // updates user
            std::cout << "Loading Discord Status" << std::endl;

            // starts a new thread just for updating some fields
            std::thread([client]() {

            // sets up a temp song name
            std::string songName = "Loading";

            // sets up a temp album name
            std::string albumName = "An Album";

            // initializes the song info
            std::string songStuff = "Discord Spotify Integration";

            // sets an empty large image name
            std::string LargeImage = "";
            // small image is set above, since it doesn't have a changing method, like large image does

            // the descriptions for the assets (hover elements)
            std::string LargeText = "Large Text";
            std::string SmallText = "Small Text";

            // placeholder URLs to pass (set to these because it helps debug, otherwise could be set to anything)
            std::string SpotifyURL = "https://youtube.com";
            std::string SmallURL = "https://twitter.com";

            // placeholder UNIX timestamps
            uint64_t unixStart = 0;
            uint64_t unixEnd = 0; // both set to 0, if the timestamps are missing in songData, falls back to displaying program uptime

            // gets the STDIN from python
            HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
            // byte count variable
            DWORD byteCount;

            // starts a loop to refresh info
            while (running) {

                // sets up a boolean to check if an update is required due to timer
                bool requiredUpdate = false;

                // sets up a boolean to check song status
                bool songChanged = false;

                // sets up a boolean to check pause state change
                bool pauseChanged = false;

                // updates current time to match, well, current time
                currentTime = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

                // checks if the last time RPC was updated was more than 15 seconds ago
                if ((lastUpdate + 15) < currentTime) {
                    // changes the requiredUpdate to true to trigger an update
                    bool requiredUpdate = true;
                }

                // the stdin byte size variable
                uint32_t stdinSize;

                // a boolean to check if the packet size is valid
                bool packetValid = ReadFile(hStdin, &stdinSize, sizeof(stdinSize), &byteCount, nullptr) || byteCount != sizeof(stdinSize);

                // checks if packet size is (in)valid
                if (!packetValid) {
                    // if it isn't, checks if the update is(n't) required yet
                    if (!requiredUpdate) {
                        // if that's not true either, waits for 250ms
                        std::this_thread::sleep_for(std::chrono::milliseconds(250));
                        // then resets to while start
                        continue;
                    }
                    // if the timer has passed the required update timer, it'll move on to the next part (re-sending old data to keep RPC up)
                }

                // if the packet is valid
                if (packetValid) {
                    
                    // variables for validation
                    uint32_t size = ntohl(stdinSize);
                    std::vector<char> buffer(size);

                    // checks the packet contents
                    if (!ReadFile(hStdin, buffer.data(), size, &byteCount, nullptr) || byteCount != size) {
                        // couldn't read the packet, waits
                        std::this_thread::sleep_for(std::chrono::milliseconds(250));
                        // resets
                        continue;
                    }

                    // grabs the packet from the sent buffer
                    std::string packet(buffer.begin(), buffer.end());

                    // parses the received packet into a json form 
                    json data = json::parse(packet);

                    // tries to reassign all the variables from the data packet
                    try {
                        // variables get grabbed from packet (ensures they use the correct type)
                        songName = data["Song"].get<std::string>();
                        albumName = data["Album"].get<std::string>();
                        songStuff = data["State"].get<std::string>();
                        LargeImage = data["Large Image"].get<std::string>();
                        LargeText = data["Large Text"].get<std::string>();
                        SmallText = data["Small Text"].get<std::string>();
                        SpotifyURL = data["Spotify URL"].get<std::string>();
                        SmallURL = data ["Small URL"].get<std::string>();
                        unixStart = data["UNIX Start"].get<int64_t>();
                        unixEnd = data["UNIX End"].get<int64_t>();
                        pauseState = data["Pause"].get<bool>();
                        trackID = data["Track ID"].get<int64_t>();
                    }
                    // if it fails
                    catch(const std::exception& e) {
                        // sends error message
                        std::cerr << "Error with Python packet:" << e.what() << std::endl;
                    }

                    // checks if the song has changed since the last update (trackIDs don't match)
                    // if it has, changes songChanged to true - this ensures the song changing or being paused gets caught
                    if (trackID != oldTrackID) {
                        // sets the old value to match new
                        oldTrackID = trackID;
                        // sets the boolean to true so the next check goes through
                        songChanged = true;
                    }
                    // checks if the song has been paused since last check
                    // if it has (the pause state is not the previous state (meaning it goes from pause -> unpause or vice versa))
                    if (pauseState != pauseStateOld) {
                        // sets the boolean to true so the next check goes through
                        pauseChanged = true;
                        // updates the previous pause state to match current
                        pauseStateOld.store(pauseState.load());
                    }

                    // these 2 checks are done to see if the album should be left in or dropped to keep the string integrity
                    // checks if the length of the songName (details) field *with* album is eq or less than 103 (cap of 108 for that field)
                    if ((songName + albumName).length() <= 103) {
                        songName = songName + " " + albumName;
                    }
                    // checks if the length of the songName (details) field *with* fallback string is eq or less than 108 (cap of 108 for that field)
                    else if ((songName + albumFallback).length() <= 108) {
                        songName = songName + " " + albumFallback;
                    }
                } // packetValid check close

                // only pushes the update if everything is fine, and the song has changed/paused/update is required
                // I found that if no update is pushed for a longer period of time, Discord may just lose the status completely and drop it
                if (songChanged || pauseChanged || requiredUpdate) {

                    // if the update isn't a timer-based one (meaning something has actually changed)
                    if (!requiredUpdate) {
                        // updates the rpc update boolean to ensure it prints rpc status
                        bool rpcUpdated = false;
                    }

                    // ensures the fields doesn't exceed the character limit (128 is what Discord claims, 108 is pretty safe)
                    songName = utfTrim(songName);
                    songStuff = utfTrim(songStuff);
                    LargeText = utfTrim(LargeText);
                    SmallText = utfTrim(SmallText);

                    // sets up rich presence details
                    discordpp::Activity activity;

                    // sets the rich presence to "Listening to:"
                    activity.SetType(discordpp::ActivityTypes::Listening);
                    // sets the "state" (song playtime, count, etc) - in games, equivalent is "Playing solo/duo..."
                    activity.SetState(songStuff);
                    // sets the "details" (song name) - in games, equivalent is "Competitive"
                    activity.SetDetails(songName);
                    // stateURL only works when a party size is set - which isn't available with this program
                    // activity.SetStateUrl("https://discord.com");

                    // sets up the rich presence assets (pictures)
                    discordpp::ActivityAssets assets;

                    // Large Image is the main picture
                    // if the field is still empty, doesn't push it through (will cause a fail otherwise)
                    if (LargeImage.empty() || LargeImage[0] == ' ') {
                        std::cout << "Large Image field is empty or faulty" << std::endl;
                    }
                    // if the field doesn't seem faulty
                    else {
                        // if the large image has failed once, doesn't try to push a new one
                        if (LargeImageFail) {   
                        }
                        // if the field isn't empty or "faulty" on the first go (or hasn't failed yet), sets the image
                        else {
                            assets.SetLargeImage(LargeImage);
                        }
                    }
        
                    // Large text appears on hovering the large image (and under the song info)
                    assets.SetLargeText(LargeText);
                    // Large URL is the Spotify link to the selected type (Artist, Song, Album, Playlist) of the currently playing track
                    assets.SetLargeUrl(SpotifyURL);

                    // Small URL is the link when you click the smaller picture
                    assets.SetSmallUrl(SmallURL);

                    // Small Image is the circle in the corner of Large Image, text is on hover
                    // if the field is still empty, doesn't push it through (will cause a fail otherwise)
                    if (SmallImage.empty() || SmallImage[0] == ' ') {
                        std::cout << "Small Image field is empty or faulty" << std::endl;
                    }
                    else {
                        // if the small image has failed once, doesn't try to push a new one
                        if (SmallImageFail) {
                        }
                        // if the field isn't empty or "faulty" on the first go (or hasn't failed yet), sets the image
                        else{
                            assets.SetSmallImage(SmallImage);
                        }
                    }
                    // Small text is the text that appears when you hover over the small picture
                    assets.SetSmallText(SmallText);

                    // pushes assets to "activity"
                    activity.SetAssets(assets);

                    // sets up the rich presence timestamps
                    discordpp::ActivityTimestamps timestamps;

                    // sets the song's start time (in UNIX timestamp)
                    timestamps.SetStart(unixStart);
                    // sets the song's end time (in UNIX timestamp)
                    timestamps.SetEnd(unixEnd);
                    // pushes timestamps to "activity"
                    activity.SetTimestamps(timestamps);
                    
                    // updates user rich presence with given info
                    client->UpdateRichPresence(activity, [](discordpp::ClientResult result) {

                        // if it goes through fine
                        if(result.Successful()) {

                            // updates the last update timestamp to match system time
                            lastUpdate = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());

                            // checks if rpc has been updated already, only prints if not
                            if (!rpcUpdated) {
                                // updates user
                                std::cout << "Rich Presence updated" << std::endl;
                                // sets the bool to true, to prevent double-prints
                                bool rpcUpdated = true;
                            }
                            // sets the error states both to false, so they can go through next time
                            ::LargeImageFail = false;
                            ::SmallImageFail = false;
                        }
                        // if it fails to push user RPC update
                        else {
                            // sets the update boolean to false
                            rpcUpdated = false;
                            
                            // if the error message contains "connection error"
                            if ((result.Error().find("Connection failed")!=std::string::npos)) {
                                // sends generic connection error (this is more or less your connection -> Discord)
                                std::cout << "Rich Presence update failed: Issue connecting to Discord API" << std::endl;
                            }
                            // if the error message contains "LargeImage"
                            else if ((result.Error().find("LargeImage")!=std::string::npos) && !LargeImageFail) {
                                // sets the fail state to true
                                ::LargeImageFail = true;
                                std::cout << "Rich Presence update failed: Large Image error" << std::endl;
                            }
                            // if the error message contains "SmallImage"
                            else if ((result.Error().find("SmallImage")!=std::string::npos) && !SmallImageFail) {
                                // sets the fail state to true
                                ::SmallImageFail = true;
                                std::cout << "Rich Presence update failed: Small Image error" << std::endl;
                            }
                            // if the error is an empty external asset error
                            // this is usually an issue with the Discord -> Spotify image grab (nothing you can do)
                            else if ((result.Error().find("external assets")!=std::string::npos)) {
                                std::cout << "Rich Presence update failed: Discord API asset error" << std::endl;
                            }
                            // if the error is something else
                            else {
                                std::cerr << "Rich Presence update failed:" << result.Error() << std::endl;
                            }
                        } // else close
                        
                    }); // UpdateRichPresence close

                } // if there's a change/update requirement close

                // if the song/pause hasn't changed and 15s hasn't passed
                else {
                    // pauses the "thread" for a bit (prevents crazy CPU spikes)
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

        } // closes the "if status connection good" 

        else if (error != discordpp::Client::Error::None) {
            //std::cerr << "Connection Error: " << discordpp::Client::ErrorToString(error) << " - Details: " << errorDetail << std::endl;
            std::cerr << "Failed to connect\n" << std::endl;
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
        std::cerr << "Failed to save token\n" << std::endl;
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
            std::cerr << "Failed to update token\n" << std::endl;
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

    discordpp::AuthorizationArgs args{};
    args.SetClientId(APPLICATION_ID);
    args.SetScopes(discordpp::Client::GetDefaultPresenceScopes());
    args.SetCodeChallenge(codeVerifier.Challenge());

    client->Authorize(args, [&, client, codeVerifier](auto result, auto code, auto redirectUri) {
        if(!result.Successful()) {
            std::cerr << "Authentication error\n" << std::endl;
            return;
        }

        // updates user on status
        std::cout << "Authorized, exchanging token\n" << std::endl;

        client->GetToken(APPLICATION_ID, code, codeVerifier.Verifier(), redirectUri,
            [&, client](discordpp::ClientResult result,
                std::string accessToken,
                std::string refreshToken,
                discordpp::AuthorizationTokenType tokenType,
                int32_t expiresIn,
                std::string scope) {
            
            if(!result.Successful()) {
                std::cerr << "Failed to get access token\n" << std::endl;
                return;
            }

            // updates user on status
            std::cout << "Connecting\n" << std::endl;

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