# PyClip

_Always able to record already said things_

## What is PyClip

PyClip is a python script that give you nuclear power in voice chat. This has been created in order to be able to "Clip" things like on twitch on my friend's discord.
To do this after configuration, PyClip will listen and continuously record last 2 minutes of theses channels. If you want to save the last two minutes, you only have to write something in the console app or use the F2 key.

Please use this whisely and do not create too much trouble.

## How to install

If you want to listen to some app such as discord, ... Please read _How to listen to apps_ section.

-   Be sure that [ffmpeg](https://ffmpeg.org/) is installed and added to your PATH
-   Download and install latest version of Python (working on 3.10)
-   Run Setup.cmd and configure your entries with your wanted label
-   To autorun paste the created StartupPyClip.cmd file into the startup directory (Windows+R => shell:startup)
-   Run the script with Start.cmd

## How to listen to apps

As Pyclip can only record "Microphone", you have to use a virtual cable as the output of the app you want to listen.
To do this follow this procedure:

-   Install a virtual cable app (for exemple [this one](https://vb-audio.com/Cable/index.htm))
-   Select it at the output of your app
-   In the sound configuration pannel choose in the cable output's properties "Listen on this peripheral". Choose your headset.

You should be able to hear your app sound in your headset and select the cable in PyClip configuration
