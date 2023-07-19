# Statcast Highlight Tool
Tools for compiling .mp4 highlight reels from BaseballSavant ([example compilation here](https://twitter.com/Sunyveil_Sports/status/1667311883085565954?s=20)). Statcast Highlight Tool can generate leaderboards given statcast data, scrape BaseballSavant for the corresponding video clips, and finally stitch together a highlight reel with annotations, exported in .mp4 format. Specific teams and players may be filtered for, and if so, the broadcast for that player/team will be prioritized when scraping the video clip.

Some of the existing presets in Statcast Highlight Tool include:
* Plays with the biggest change in WPA
* Worst strike/ball calls from umpires
* Highest exit velocity with negative launch angle
* ...and more!

## How to Use

Statcast Highlight Tool's presets.py takes the functionality of the package and streamlines it such that a highlight reel can be generated with only a couple lines of code. To generate a highlight reel, navigate to the appropriate directory, and run the following lines of code:

```
import presets

presets.make_highlight_reel(start_date = '2023-05-01', end_date = '2023-05-31',
                            n_highlights = 10, format = 'clutch', teams = ['SF'],
                            daily = False, ascending = False, max_duration = 20)
```

This query, for example, would generate a highlight reel consisting of the highest WPA events that were positive for the San Francisco Giants. The return value for this function will be the name of the video file created, which defaults to ```compilation.mp4```.

Parameters are described here:
* ```start_date``` and ```end_date```: The start and end dates of the search.
* ```n_highlights```: The top n clips to get.
* ```daily```: If ```True```, will find n clips per day within the specified time range.
* ```format```: Which preset to use. For more info, look at ```presets.preset_dict```.
* ```teams``` and ```players```: Which teams or players to filter for. Team abbreviations are listed in ```presets.teamcodes```, while player codes are their six-digit numeric code on BaseballSavant. To figure out this six-digit code, navigate to a player's BaseballSavant page; the six-digit code after their name in the URL is the one you should put here.
* ```ascending```: Whether the leaderboard should start with high values or low values. Generally, this should be ```False```, but some presets like this set to ```True```.
* ```max_duration```: The max duration of each clip to include, in seconds.

Queries may be customized by manually calling functions in get_vid.py and pyb_tools.py.

## Requirements
Statcast Highlight Tool requires the following to be successfully installed on your device:
* [pybaseball](https://github.com/jldbc/pybaseball)
* [moviepy](https://zulko.github.io/moviepy/)
* [selenium](https://selenium-python.readthedocs.io/)
* [chromedriver](https://zulko.github.io/moviepy/)
* [Google Chrome](https://www.google.com/chrome/)

Only pybaseball is required to make leaderboard dataframes, but creating video compilations require all of the above. Please do keep in mind that moviepy has its own requirements and that chromedriver needs to be updated regularly in order to function.

## Contact
Message [@Sunyveil_Sports](https://twitter.com/sunyveil_sports) on Twitter, or just make a comment here in case of Twitter's looming demise.
