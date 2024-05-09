#!/usr/bin/python3
"""Flipper Zero remote control for the terminal
Version: 1.0.0
"""

## Modules
#

import sys
import argparse
import queue
import threading
import multiprocessing
from readchar import key, readkey
from flipperzero_protobuf.flipper_proto import FlipperProto

try:
  import colorama
except:
  pass



## Keyboard-to-Flipper input mapping
#

keyboard_to_flipper_input = {

  "a":           "SHORT LEFT",
  "h":           "SHORT LEFT",
  key.LEFT:      "SHORT LEFT",

  "s":           "SHORT DOWN",
  "j":           "SHORT DOWN",
  key.DOWN:      "SHORT DOWN",

  "w":           "SHORT UP",
  "k":           "SHORT UP",
  key.UP:        "SHORT UP",

  "d":           "SHORT RIGHT",
  "l":           "SHORT RIGHT",
  key.RIGHT:     "SHORT RIGHT",

  "o":           "SHORT OK",
  key.SPACE:     "SHORT OK",
  key.ENTER:     "SHORT OK",

  "b":           "SHORT BACK",
  key.BACKSPACE: "SHORT BACK",
  key.DELETE:    "SHORT BACK",

  "A":           "LONG LEFT",
  "H":           "LONG LEFT",

  "S":           "LONG DOWN",
  "J":           "LONG DOWN",

  "W":           "LONG UP",
  "K":           "LONG UP",

  "D":           "LONG RIGHT",
  "L":           "LONG RIGHT",

  "O":           "LONG OK",

  "B":           "LONG BACK"
}

keyboard_to_flipper_help1 = [
"_______________________________________________________________",
"|                  SHORT PRESS                                 ",
"|              ___________________                             ",
"|              |       UP:       |                             ",
"|              |     w, ^, k     |                             ",
"|              +-----------------+                             ",
"| ___________  ___________________  ___________                ",
"| |  LEFT:  |  |       OK:       |  |  RIGHT: |                ",
"| | <, a, h |  | SPACE, ENTER, o |  | d, l, > |                ",
"| +---------+  +-----------------+  +---------+                ",
"|              ___________________       _____________________ ",
"|              |      DOWN:      |       |       BACK:       | ",
"|              |     s, v, j     |       | BACKSPACE, DEL, b | ",
"|              +-----------------+       +-------------------+ ",
"+--------------------------------------------------------------"]

keyboard_to_flipper_help2 = [
"________________________________________",
"            LONG PRESS                 |",
"            __________                 |",
"            |   UP:  |                 |",
"            |  W, K  |                 |",
"            +--------+                 |",
"__________  __________  __________     |",
"|  LEFT: |  |   OK:  |  | RIGHT: |     |",
"|  A, H  |  |    O   |  |  D, L  |     |",
"+--------+  +--------+  +--------+     |",
"            __________       _________ |",
"            |  DOWN: |       | BACK: | |",
"            |  S, J  |       |   B   | |",
"            +--------+       +-------+ |",
"---------------------------------------+"]



## defines
#

unicode_block_elements = [
  "\u2588",	# Full block
  "\u2584",	# Lower half block
  "\u2580",	# Upper half block
  " ",		# Space
]

# Special characters
ESC = "\x1b"
CR = "\r"
LF = "\n"

# ANSI 8-bit color selection
set_bg_color = ESC + "[48;5;{}m"
set_fg_color = ESC + "[38;5;{}m"

# Predefined colors
ansi_8bit_black = 0
ansi_8bit_orange = 208

# ANSI attributes reset
attribute_reset = ESC + "[0m"

# ANSI x lines up
x_lines_up = ESC + "[{}A"



## Routines
#

def input_thread(msg_queue):
  """ Get keyboard keypresses, turn them into Flipper Zero input events and send
  them to the main thread
  """

  t = threading.current_thread()

  try:

    # Run until we're told to stop
    while getattr(t, "do_run", True):

      # Get one key
      k = readkey()

      # It the user wants to show / hide the keymap, send "k" to the main thread
      if k == key.CTRL_K:
        msg_queue.put(("k", None))

      # Send the main thread the input event to send the Flipper if there is one
      else:
        msg_queue.put((keyboard_to_flipper_input.get(k, ""), None))

  except KeyboardInterrupt:
    msg_queue.put((None, None))

  except Exception as e:
    msg_queue.put((None, e))
    return



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
	  "-d", "--device",
	  help = "Flipper Zero serial device to use. Default: autodetect",
	  type = str
	)

  args = argparser.parse_args()

  # Combine and semigraphic-ize the keymap help strings
  keymap_help = []
  for l1, l2 in zip(keyboard_to_flipper_help1, keyboard_to_flipper_help2):
    l = (" " + l1 + l2 + " ").\
		replace(" _", " \u250c").replace("_ ", "\u2510 ").\
		replace("_", "\u2500").replace("|", "\u2502").\
		replace(" +", " \u2514").replace("+ ", "\u2518 ").\
		replace("-", "\u2500").replace("<", "\u2190").\
		replace("^", "\u2191").replace(">", "\u2192").\
		replace("v", "\u2193")[1:-1]
    keymap_help.append(l)

  keymap_help_line_len = len(keymap_help[0])
  keymap_help_overlay_at_col = int((128 - keymap_help_line_len) / 2)
  keymap_help_overlay_at_line = int((32 - len(keymap_help)) / 2)

  # Connect to the Flipper Zero
  p = FlipperProto(serial_port = args.device)

  # Get the Flipper Zero's name
  flipper_name = "[ " + p.device_info["hardware_name"] + " ]"
  flipper_name_spacing = " " * int((128 - len(flipper_name)) / 2)

  # Bottom help line
  bottom_line = "[ Ctrl-K to show/hide keymap ]     [ Ctrl-C to stop ]"
  bottom_line_spacing = " " * int((128 - len(bottom_line)) / 2)

  nb_display_lines = 34

  # ANSI sequences to home the cursor and send it to the end of the display
  home_cursor = x_lines_up.format(nb_display_lines)
  goto_end_display = CR + LF * (nb_display_lines - 1)

  # Spawn the thread to get keypresses
  q = multiprocessing.Queue()
  t = threading.Thread(target = input_thread, args = (q,))
  t.start()

  show_keymap = False

  try:

    # Run until stopped by Ctrl-C
    while True:

      # Get a screenshot from the Flipper Zero
      screen_data = p.rpc_gui_snapshot_screen()
      assert len(screen_data) == 1024

      # Turn the screen data into lines of unicode block elements
      imglines = ["".join([unicode_block_elements[(screen_data[i] >> j) & 0b11]
			for i in range(k, k + 128)])
		for k in range(0, 1024, 128) for j in range(0, 8, 2)]

      # If the keymap help should be displayed, overlay it over the lines
      if show_keymap:
        for i, l in enumerate(keymap_help):
          imglines[keymap_help_overlay_at_line + i] = \
			imglines[keymap_help_overlay_at_line + i]\
				[:keymap_help_overlay_at_col] + \
			attribute_reset + \
			l + \
			set_fg_color.format(ansi_8bit_orange) + \
			imglines[keymap_help_overlay_at_line + i]\
				[keymap_help_overlay_at_col + \
					keymap_help_line_len:]

      # Create the final ASCII art
      aa =  flipper_name_spacing + flipper_name + CR + LF + \
		"".join([set_bg_color.format(ansi_8bit_black) + \
				set_fg_color.format(ansi_8bit_orange) + \
				l + attribute_reset + CR + LF \
				for l in imglines]) + \
		bottom_line_spacing + bottom_line + CR + \
		home_cursor

      # Print the ASCII art on the console
      print(aa)

      # Process messages from the input thread
      while True:

        # Try to get one message out of the queue
        try:
          flipper_input, e = q.get_nowait()

        except queue.Empty:
          break

        # If we got an exception from the input thread, re-raise it
        if e is not None:
          raise e

        # Do we have a Flipper Zero input event string?
        elif flipper_input is not None:

          # Should we show or hide the keymap?
          if flipper_input == "k":
            show_keymap = not show_keymap

          # If the string isn't empty, send the event to the Flipper Zero
          elif flipper_input:
            p.rpc_gui_send_input(flipper_input)

        # The input thread exited normally so do the same thing
        else:
          raise KeyboardInterrupt

  except KeyboardInterrupt:

    # Skip past the display
    print(goto_end_display)

  except:

    # Skip past the display
    print(goto_end_display)

    # Re-raise the exception
    raise

  finally:

    # Tell the input thread to stop if it hasn't stopped by itself already
    setattr(t, "do_run", False)

    # Join the thread
    t.join()

  return 0



## Main program
#

if __name__ == "__main__":
  sys.exit(main())
