#define DISCORDPP_IMPLEMENTATION
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
#include <Windows.h>
#include <codecvt>

// version number (y.m.dd.hhmm)
std::string DSIDver = "v0.3.1.0910";

// initialises the Discord Application ID
std::uint64_t APPLICATION_ID = 0;

// initialises a default small icon of nothing
std::string SmallImage = "";

// initialises a default refresh time of 15 seconds
std::uint64_t RefreshTime = 0;

// initialises bools for image failing
// this is not common, but prevents more than 1 failure
std::atomic<bool> LargeImageFail = false;
std::atomic<bool> SmallImageFail = false;

// initialises a temp string for checks (0 ensures it's always a new song on program start)
std::uint64_t unixOldStart = 0;

// initialises a temp string for checks (empty ensures it's always a new song on program start)
std::string oldSong = "";

// flag to control application run state (starts as true to start running)
std::atomic<bool> running = true;



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
std::string utfTrim(const std::string& input, size_t maxUnits = 118) {
    // if there's nothing, falls back to default
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

    // goes through every character in the string
    for (size_t i = 0; i < utf16.size(); ++i) {
        wchar_t wc = utf16[i];

        // goes through "surrogate pairs" (non-standard characters, emojis, etc)
        // "high" surrogates = 0xD800-0xDBFF, "lows" = 0xDC00-0xDFFF
        if (wc >= 0xD800 && wc <= 0xDBFF) {
            // if the pairs fit in maxUnits
            if (i + 1 < utf16.size()) {
                wchar_t low = utf16[i + 1];
                if (low >= 0xDC00 && low <= 0xDFFF) {
                    // they get added to trimmed string and add +2
                    if (units + 2 > maxUnits) break;
                    trimmed += wc;
                    trimmed += low;
                    units += 2;
                    ++i;
                    continue;
                }
            }
            // if they're invalid, they get skipped
            continue;
        }

        // anything else just gets counted normally
        // they'll only get added until that character + 1 is > than the safe max
        if (units + 1 > maxUnits) break;
        // adds the character to the trimmed string
        trimmed += wc;
        ++units;
    }

    // a function that trims trailing space/invisible characters
    auto trailTrim = [](wchar_t c) {
        return c == L' ' || c == L'\t' || c == L'\r' || c == 0x200B || c == 0xFEFF;
    };
    while (!trimmed.empty() && trailTrim(trimmed.back())) {
        trimmed.pop_back();
    }

    // makes sure the string is at least 2 (discord needs 2 =< x =< 128 characters)
    if (trimmed.size() < 2) {
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
    // ids.txt contains the Discord Application ID, the refreshTime and small picture name/link (written once by DSI at start)
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
        std::cerr << "Failed to open/read ids.txt, Discord RPC closed.\n" << std::endl;
        return 1;
    }

    // creates "line" (placeholder string) and lineNum (a counter)
    std::string line;
    int lineNum = 0;

    // creates empty strings to hold info later
    std::string AppID, SIMG, rfT;

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
            // third (last) line is the Refresh Time, aka how often the program should send data
            else if (lineNum == 2) rfT = value;
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
    catch (...) {
        std::cerr << "Invalid App ID, check config.ini\n" << std::endl;
        return 1;

    }
    // tries to replace RefreshTime with rfT (number from ids.txt)
    try {
        RefreshTime = std::stoull(rfT);
    } 
    catch (...) {
        std::cerr << "Invalid Refresh Time, try deleting token.txt in Discord folder if this doesn't resolve automatically\n" << std::endl;
        return 1;
    }

    // something something Discord's handler
    std::signal(SIGINT, signalHandler);

    // informs when DSI has successfully launched
    std::cout << "Discord RPC started via DSIdiscord " << DSIDver << "\n" << std::endl;

    // creates a Discord Client
    auto client = std::make_shared<discordpp::Client>();

    // sets up logging callback
    client->AddLogCallback([](auto message, auto severity) {
      // std::cout << "[" << EnumToString(severity) << "] " << message << std::endl;
    }, discordpp::LoggingSeverity::Info);

    std::atomic<bool> RPCrunning = false;

    // sets up status callback to check client connection
    client->SetStatusChangedCallback([client, &RPCrunning](discordpp::Client::Status status, discordpp::Client::Error error, int32_t errorDetail) {

      // if discord succeeds at finding client, gets ready to change activity info
      if (status == discordpp::Client::Status::Ready) {

        // checks if the RPC has already been started and is already running
        if (!RPCrunning.exchange(true)) {

        // updates user
        std::cout << "Loading Discord Status\n" << std::endl;

        // starts a new thread just for updating some fields
        std::thread([client]() {
          // creates variables for the whole thread

          // sets up a temp song name
          std::string songName = "Loading";

          // initializes the song info
          std::string songStuff = "Discord Spotify Integration";

          // sets an empty large image name
          std::string LargeImage = "";
          // small image is set above, since it doesn't have a changing method, like large image does

          // the descriptions for the assets (hover elements)
          std::string LargeText = "Large Text";
          std::string SmallText = "Small Text";

          // placeholder URLs to pass
          std::string SpotifyURL = "https://youtube.com";
          std::string SmallURL = "https://twitter.com";

          // placeholder UNIX timestamps
          uint64_t unixStart = 0;
          uint64_t unixEnd = 0; // both set to 0, if the timestamps are missing in songData, falls back to displaying program uptime

          // defaults the "success" to not true
          bool success = false;

          // starts a loop to refresh info
          while (running) {

            // sets up the prerequisite UNIX temp variables as empty strings
            std::string unixStartStr, unixEndStr;

            // opens the file containing the song information (provided by the main python script) 
            // the file is stored 2 directories above where the EXE resides, 
            std::ifstream SongInfo("songData.txt", std::ios::binary);

            // once it's open, goes line-by-line and picks up the information
            if (SongInfo.is_open()) {

                // if the file was opened correctly, changes success to true
                success = true;

                // updates user (this keeps printing constantly)
                // std::cout << "Song File opened\n" << std::endl;

                // creates an empty helper string
                std::string line;

                // initializes lineNum as 0 (starts at line 0)
                int lineNum = 0;

                // goes through the file 1 by 1
                while(std::getline(SongInfo, line)) {
                    // checks for "=" mark to indicate splits
                    size_t pos = line.find('=');
                    // checks each line for the "=" mark, then processes the line
                    if(pos != std::string::npos) {
                        std::string value = line.substr(pos + 1);
                        // checks for empty space
                        if (!value.empty() && value[0] == ' ')
                            // removes any empty space
                            value.erase(0, 1);
                        if (!value.empty() && value.back() == '\r')
                            // removes an invisible character
                            value.pop_back();
                        // line 0 is the name/artist and album of the song
                        if (lineNum == 0) songName = value;
                        // line 1 is the info on songStuff (minutes, plays, etc)
                        else if (lineNum == 1) songStuff = value;
                        // line 2 is largeImage
                        else if (lineNum == 2) LargeImage = value;
                        // line 3 is "large text" (total hours)
                        else if (lineNum == 3) LargeText = value;
                        // line 4 is the text on hover
                        else if (lineNum == 4) SmallText = value;
                        // line 5 is the URL of the song
                        else if (lineNum == 5) SpotifyURL = value;
                        // line 6 is the "small url"
                        else if (lineNum == 6) SmallURL = value;
                        // line 7 is the start time of the song, in UNIX (string now)
                        else if (lineNum == 7) unixStartStr = value;
                        // line 8 is the end time of the song, in UNIX (string now)
                        else if (lineNum == 8) unixEndStr = value;

                        // adds 1 to lineNum so it chooses the next line
                        lineNum++;
                    }
                } // closes the reader bracket

                // tries to turn the UNIX timestamps from strings to integers (Discord only accepts int in this field)
                try {
                    unixStart = std::stoull(unixStartStr);
                    unixEnd = std::stoull(unixEndStr);
                  } 
                  // if the str -> int fails, sends an exception (e) in text
                  catch(const std::exception& e) {
                    std::cerr << "Timestamp in file is invalid" << "\n" << e.what() << "\n" << std::endl;
                  }

            } // if(song.is_open) close bracket
            else {
              std::cout << "Error reading the song file\n" << std::endl;
            }
            
            // closes the text file
            SongInfo.close();

            // sets up a boolean to check song status
            bool songChanged = false;

            // checks if the song has changed since the last update
            // if it has (timestamps OR song names don't match) - this ensures the song changing or being paused gets caught
            if (unixStart != unixOldStart || oldSong != songName ) {

                // sets the temporary variable to match the new song's name
                oldSong = songName;
                // sets the temporary variable to match the new song's timestamp
                unixOldStart = unixStart;
                // sets the boolean to true so the next
                songChanged = true;
            }
            // if the song hasn't changed
            else {
                // pauses the "thread" for a bit (prevents crazy CPU/disk usage for nothing)
                std::this_thread::sleep_for(std::chrono::seconds(2));
            }

                // only pushes the update if the file was read correctly and the song has changed
                if (success && songChanged) {

                    // ensures the fields doesn't exceed the character limit
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
                        std::cout << "Large Image field is empty or faulty, not pushing\n" << std::endl;
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
                        std::cout << "Small Image field is empty or faulty, not pushing\n" << std::endl;
                    }
                    else {
                        // if the small image has failed once, doesn't try to push a new one
                        if (SmallImageFail) {
                        }

                        else{
                        // if the field isn't empty or "faulty" on the first go (or hasn't failed yet), sets the image
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
                            // updates user
                            std::cout << "Rich Presence updated\n" << std::endl;
                            // sets the error states both to false, so they can go through next time
                            ::LargeImageFail = false;
                            ::SmallImageFail = false;
                        }
                        // if it fails to push user RPC update
                        else { 
                            // prints out the error for debug (likely wrong format or missing filenames, etc)
                            std::cerr << "Rich Presence update failed. Reason:\n" << result.Error() << "\n" << std::endl; 

                            // if the error message contains "LargeImage"
                            if ((result.Error().find("LargeImage")!=std::string::npos) && !LargeImageFail) {
                                // sets the fail state to true
                               ::LargeImageFail = true;
                               std::cout << "Attempting to fix large image error, please wait for the next data push\n" << std::endl;
                            }
                            // if the error message contains "SmallImage"
                            if (result.Error().find("SmallImage")!=std::string::npos && !SmallImageFail) {
                                // sets the fail state to true
                               ::SmallImageFail = true;
                               std::cout << "Attempting to fix small image error, please wait for the next data push\n" << std::endl;
                            }
                        } // else close
                        
                  }); // UpdateRichPresence close

                } // if(success) close
                
                // pauses the update loop for 3 seconds (songData won't update that fast, so just lets program breathe)
                std::this_thread::sleep_for(std::chrono::seconds(3));
                
                } // while(running) close bracket

                // detaches itself from the main thread so as to not stop the discord communications updates
                }).detach(); // thread close bracket
            }

    } // closes the "if status connection good" 

      else if (error != discordpp::Client::Error::None) {
        //std::cerr << "Connection Error: " << discordpp::Client::ErrorToString(error) << " - Details: " << errorDetail << std::endl;
        std::cerr << "Failed to connect\n" << std::endl;
      }
    }); // client callback close bracket

// initializes variables for tokens and time
std::string savedAccessToken, savedRefreshToken;
int64_t savedExpiryTime = 0;

// reads the token.txt file (inside the build directory)
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
        std::cerr << "Failed to save tokens\n" << std::endl;
    }
};

// starts Discord connection
auto connectWithToken = [&](const std::string& access) {
    client->UpdateToken(discordpp::AuthorizationTokenType::Bearer, access, [client](discordpp::ClientResult result) {
        if(result.Successful()) {
            // updates user
            std::cout << "Token loaded, connecting to Discord\n" << std::endl;
            client->Connect();
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