
<p align="center">
  <img src="https://img.freepik.com/vektoren-premium/tik-tok-logo_578229-290.jpg" height=100>

</p>

<div align="center">
  
## TikTok-AutoUpload

This project empowers users to effortlessly upload TikTok posts without the need for web drivers. With a seamless and straightforward process, users can automate the uploading of their videos, streamlining their TikTok content creation experience. The key feature of this tool is its ability to schedule posts and offer customizable settings, allowing users to tailor their uploads to their preferences.

The sole requirement for utilizing this project is the TikTok ```sessionid``` cookie. Easily obtainable after logging in to your TikTok account, this cookie ensures seamless and secure access to the TikTok API.
</div>


## Installation

1. Install Python3.7+:
Ensure you have Python 3.7+ installed on your system. If not, you can download and install it from https://www.python.org/downloads/.

2. Install NodeJS 19.3+:
Ensure you have NodeJS 19.3+ installed on your system. If not, you can download and install it from https://nodejs.org/en/download/.

4. Clone the Git Repository:
Download the Git repository and move it to a dedicated folder on your machine.

5. Install Required Libraries:
Open a terminal or command prompt and navigate to the folder where you placed the Git repository. Run the following command to install the necessary libraries using pip:
```
python -m pip install -r requirements.txt
```

6. Get TikTok Session ID:
Visit https://www.tiktok.com/ and log in to your account.
Press F12 to open the developer tools, then go to the Application tab.
In the Cookies section, find the value associated with the key ```sessionid``` and copy it.

![](https://github.com/xXChezyXx/TikTok-AutoUpload/blob/main/sessionid%20guide.gif)
    
## Usage

There are two options:

1) Using the Command-Line-Interface: 

```
USAGE: tiktok_autoupload.py -s SESSIONID -v VIDEO -t TITLE [-sc SCHEDULE] [-c COMMENT] [-d DUET] [-st STITCH] [-vi VISIBILITY] [-bo BRANDORGANIC] [-bc BRANDCONTENT] [-ai AILABEL]
```

2) Using the Python file:
```python
from tiktok_autoupload import upload_video

# default settings
sessionid = "SESSIONID"
video = "VIDEO"
title = "TITLE"
schedule = 0 #OPTIONAL
comment = 1 #OPTIONAL
duet = 0 #OPTIONAL
stitch = 0 #OPTIONAL
visibility = 0 #OPTIONAL
brandorganic = 0 #OPTIONAL
brandcontent = 0 #OPTIONAL
ai_label = 0 #OPTIONAL
proxy = None #OPTIONAL

upload_video(sessionid, video, title, schedule, comment, duet, stitch, visibility, brandorganic, brandcontent, ai_label)
```


## Parameters

- ```sessionid``` : Your sessionid from TikTok
- ```video``` : The path of your video
- ```title``` : Your title
- ```schedule``` : The timestamp **(in seconds)** at which you want to schedule your video
- ```comment``` : Allow **(1)**/Disallow **(0)** comments
- ```duet``` : Allow **(1)**/Disallow **(0)** duets
- ```stitch``` : Allow **(1)**/Disallow **(0)** sticthes
- ```visibility``` : Set your video to public **(0)**, private **(1)** or friends **(2)**
- ```brandorganic``` : Enable **(1)**/Disable **(0)** own product placements
- ```brandcontent``` : Enable **(1)**/Disable **(0)** other product placements
- ```ailabel``` : Enable **(1)**/Disable **(0)** created by AI
- ```proxy``` : Send requests with your proxy

**NOTE: The title should not exceed a maximum of 2200 characters**

**NOTE: The maximum duration of your schedule you can set is 86400 seconds (10 days) and the minimum you can set is 900 seconds (15 minutes)**

**NOTE: Private videos cannot be uploaded if you schedule the upload**

## Examples

This command will upload your video publicly with the title "Hello world #TikTok @Bob" allowing comments:

CLI:
```
tiktok_autoupload.py -s f6e4b2a1c9d8e7f6a5b4c3d7a9f3c5d8 -v "/path/to/file.mp4" -t "Hello world #TikTok @Bob"
```

Python:
```python
upload_video("f6e4b2a1c9d8e7f6a5b4c3d7a9f3c5d8", "/path/to/file.mp4", "Hello world #TikTok @Bob")
```

This command will upload your video privately in 900 seconds with the title "Hello #Tiktok @Hello #world @Bob #lol world!" allowing comments and duets with the proxy "http://10.10.10.10:8000":

CLI:
```
tiktok_autoupload.py -s f6e4b2a1c9d8e7f6a5b4c3d7a9f3c5d8 -v "/path/to/file.mp4" -t "Hello #Tiktok @Hello #world @Bob #lol world!" -d 1 -vi 1 -sc 900 -p "http://10.10.10.10:8000"
```

Python:
```python
upload_video("f6e4b2a1c9d8e7f6a5b4c3d7a9f3c5d8", "/path/to/file.mp4", "Hello #Tiktok @Hello #world @Bob #lol world!", duet=1, visibility=1, schedule=900, proxy="http://10.10.10.10:8000")
```
