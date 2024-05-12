#!/usr/bin/python3
"""Flipper Zero remote control for the terminal
Version: 1.4.0

Record player

Replay sessions recorded with tflipper -r
"""

## Modules
#

import re
import sys
import argparse
from time import time, sleep

try:
  import colorama
except:
  pass



## Defines
#

# Special characters
ESC = "\x1b"
CR = "\n"
LF = "\n"

# VT100 cursor invisible
set_cursor_invisible = ESC + "[?25l"

# VT100 cursor visible
set_cursor_visible = ESC + "[?25h"

# VT100 invisible text
set_text_invisible = ESC + "[8m"

# VT100 attributes reset
attributes_reset = ESC + "[0m"

# VT100 x lines up
x_lines_up = ESC + "[{}A"



## Main routine
#

def main():

  # If we run on Windows, initialize colorama, so the Windows console
  # understands ANSI escape codes
  if sys.platform[0:3] == "win":
    colorama.init()

  # Parse the command line arguments
  argparser = argparse.ArgumentParser()

  argparser.add_argument(
	  "record",
	  help = "tflipper session record file to play",
	  type = str
	)

  args = argparser.parse_args()

  # Precompiled regex for an invisible timecode and button presses marker
  re_tc_btn_marker = re.compile((set_text_invisible.replace("[", "\\[") + \
					"\[([0-9]+\.[0-9]{3})s\] " \
					"\[[lLdDuUrRoObB]*\]" + \
					attributes_reset.replace("[", "\\[")).\
					encode("ascii"))

  # Precompiled regex for a x-lines-up sequence
  re_x_lines_up = re.compile(x_lines_up.replace("[", "\\[").\
				format("([0-9]+)").encode("ascii"))

  # Precompiled regex for line feeds
  re_lf = re.compile(LF.encode("ascii"))

  nb_lines_back_up = 0

  cursor_visible = True
  start_time = time()

  f = None

  try:

    # Open the record
    with open(args.record, "rb") as f:

      # Read the file line by line
      for l in f.readlines():

        # Does the line contain an invisible timecode?
        m = re_tc_btn_marker.search(l)
        if m:

          # Wait long enough to reproduce the same delay as originally recorded
          wait = float(m[1]) - time() + start_time
          if wait > 0:
            sleep(wait)

        # Does the line contain x-lines-up sequences?
        m = re_x_lines_up.findall(l)
        if m:
          nb_lines_back_up += sum(map(int, m))

        # Does the line contain line feeds?
        m = re_lf.findall(l)
        if m:
          nb_lines_back_up -= len(m)

        # Hide the cursor if needed
        if cursor_visible:
          sys.stdout.buffer.write(set_cursor_invisible.encode("ascii"))
          cursor_visible = False

        # Print the line
        sys.stdout.buffer.write(l)
        sys.stdout.buffer.flush()

    f = None

    # Raise a keyboard interrupt even if we stop normally so the display gets
    # cleaned up before quitting
    raise KeyboardInterrupt

  except KeyboardInterrupt:

    # Add an extra LF in case the playback was interrupted
    if f is not None:
      sys.stdout.buffer.write(LF.encode("ascii"))

  except:
    raise

  finally:

    # Skip past lines we printed that are below the cursor
    if nb_lines_back_up > 0:
      sys.stdout.buffer.write((CR + LF * nb_lines_back_up).encode("ascii"))

    # Show the cursor again if needed
    if not cursor_visible:
      sys.stdout.buffer.write(set_cursor_visible.encode("ascii"))

    sys.stdout.buffer.flush()

  return 0



## Main program
#

if __name__ == "__main__":
  sys.exit(main())
