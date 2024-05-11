# Flipper Zero console remote control
### Version 1.3.0

* [Usage](#Usage)
* [Installation](#Installation)
* [License](#License)

Text-mode [Flipper Zero](https://flipperzero.one/) remote-control.

#### Functions

- Display the Flipper Zero's screen in the console in real time
- Send button presses from the keyboard
- Record and replay a session

https://github.com/Giraut/tFlipper/assets/37288252/9e1c3753-835e-4ead-a4c8-cdbc5b4fc527



## Usage

- Connect the Flipper Zero to a USB port
- Open a terminal
- Run `python tFlipper.py`

The utility connects to the Flipper Zero and displays its screen in the console.

![Flipper Zero display in the console](screenshots/flipper_display_in_the_console.png)

Hit `Ctrl-K` to see the keyboard-to-buttons mapping. To remain compatible with most terminals, the keyboard input uses separate keys to emulate short and long Flipper Zero button presses.

![Flipper Zero display in the console](screenshots/keyboard_mapping_help.png)

If you run `python tFlipper.py -H`, the display will be rendered using high-density semigraphics: the entire display will then fit in a 80 x 24 console, at the cost of a slightly distorted image, because the aspect ratio cannot be respected:

![Flipper Zero display in the console](screenshots/high_density_semigraphics_rendering.png)

If you run `python tFlipper.py -t session.txt`, the session will be recorded as ANSI art text in `session.txt`. The text file can be replayed with the correct timing with `python tFreplay.py session.txt`.

If you run `python tFlipper.py -g session.gif`, the session will be recorded as an animated GIF:

![Flipper Zero session recorded as an animated GIF](screenshots/session_animation.gif)



## Installation

- Install [Python 3](https://www.python.org/)
- Install the following modules:

    ```
    $ python -m pip install flipperzero-protobuf
    $ python -m pip install readchar
    $ python -m pip install Pillow
    ```

- In Windows, you also need to install:

    ```
    $ python -m pip install colorama
    ```

- Clone this repository
- Copy `tFlipper.py` and `tFreplay.py` anywhere you find convenient in the executable path



## License

MIT
