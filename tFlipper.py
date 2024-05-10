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

keyboard_to_flipper_help = [
"________________________________________________________________",
"|                     _________________                        |",
"|                     |      UP:      |                        |",
"|                     |               |                        |",
"|              Long > |    [W] [K]    |                        |",
"|             Short > |     w ^ k     |                        |",
"|                     +---------------+                        |",
"|        ___________  _________________  ___________           |",
"|        |  LEFT:  |  |      OK:      |  |  RIGHT: |           |",
"|        |         |  |               |  |         |           |",
"| Long > | [A] [H] |  |      [O]      |  | [D] [L] |           |",
"|Short > |  < a h  |  | SPACE ENTER o |  |  d l >  |           |",
"|        +---------+  +---------------+  +---------+           |",
"|                     _________________         ______________ |",
"|                     |     DOWN:     |         |    BACK:   | |",
"|                     |               |         |            | |",
"|              Long > |    [S] [V]    |  Long > |     [B]    | |",
"|             Short > |     s v j     | Short > | BACK DEL b | |",
"|                     +---------------+         +------------+ |",
"+--------------------------------------------------------------+"]



## defines
#

unicode_blocks_1x2 = [
  "\u2588",	# Full block:		#
		#			#

  "\u2584",	# Lower half block:	.
		#			#

  "\u2580",	# Upper half block:	#
		#			.

  " ",		# Space:		.
		#			.
]

unicode_blocks_2x3 = [
  "\u2588",	# Full block:		##
		#			##
		#			##

  "\U0001fb3b",	#			.#
		#			##
		#			##

  "\U0001fb38",	#			##
		#			.#
		#			##

  "\U0001fb37",	#			.#
		#			.#
		#			##

  "\U0001fb2c",	#			##
		#			##
		#			.#

  "\U0001fb2b",	#			.#
		#			##
		#			.#

  "\U0001fb28",	#			##
		#			.#
		#			.#

  "\u2590",	# Right half block:	.#
		#			.#
		#			.#

  "\U0001fb3a",	#			#.
		#			##
		#			##

  "\U0001fb39",	#			..
		#			##
		#			##

  "\U0001fb36",	#			#.
		#			.#
		#			##

  "\U0001fb35",	#			..
		#			.#
		#			##

  "\U0001fb2a",	#			#.
		#			##
		#			.#

  "\U0001fb29",	#			..
		#			##
		#			.#

  "\U0001fb27",	#			#.
		#			.#
		#			.#

  "\U0001fb26",	#			..
		#			.#
		#			.#

  "\U0001fb34",	#			##
		#			#.
		#			##

  "\U0001fb33",	#			.#
		#			#.
		#			##

  "\U0001fb30",	#			##
		#			..
		#			##

  "\U0001fb2f",	#			.#
		#			..
		#			##

  "\U0001fb25",	#			##
		#			#.
		#			.#

  "\U0001fb24",	#			.#
		#			#.
		#			.#

  "\U0001fb21",	#			##
		#			..
		#			.#

  "\U0001fb20",	#			.#
		#			..
		#			.#

  "\U0001fb32",	#			#.
		#			#.
		#			##

  "\U0001fb31",	#			..
		#			#.
		#			##

  "\U0001fb2e",	#			#.
		#			..
		#			##

  "\U0001fb2d",	#			..
		#			..
		#			##

  "\U0001fb23",	#			#.
		#			#.
		#			.#

  "\U0001fb22",	#			..
		#			#.
		#			.#

  "\U0001fb1f",	#			#.
		#			..
		#			.#

  "\U0001fb1e",	#			..
		#			..
		#			.#

  "\U0001fb1d",	#			##
		#			##
		#			#.

  "\U0001fb1c",	#			.#
		#			##
		#			#.

  "\U0001fb19",	#			##
		#			.#
		#			#.

  "\U0001fb18",	#			.#
		#			.#
		#			#.

  "\U0001fb0e",	#			##
		#			##
		#			..

  "\U0001fb0d",	#			.#
		#			##
		#			..

  "\U0001fb0a",	#			##
		#			.#
		#			..

  "\U0001fb09",	#			.#
		#			.#
		#			..

  "\U0001fb1b",	#			#.
		#			##
		#			#.

  "\U0001fb1a",	#			..
		#			##
		#			#.

  "\U0001fb17",	#			#.
		#			.#
		#			#.

  "\U0001fb16",	#			..
		#			.#
		#			#.

  "\U0001fb0c",	#			#.
		#			##
		#			..

  "\U0001fb0b",	#			..
		#			##
		#			..

  "\U0001fb08",	#			#.
		#			.#
		#			..

  "\U0001fb07",	#			..
		#			.#
		#			..

  "\U0001fb15",	#			##
		#			#.
		#			#.

  "\U0001fb14",	#			.#
		#			#.
		#			#.

  "\U0001fb12",	#			##
		#			..
		#			#.

  "\U0001fb11",	#			.#
		#			..
		#			#.

  "\U0001fb06",	#			##
		#			#.
		#			..

  "\U0001fb05",	#			.#
		#			#.
		#			..

  "\U0001fb02",	#			##
		#			..
		#			..

  "\U0001fb01",	#			.#
		#			..
		#			..

  "\u258c",	# Left half block:	#.
		#			#.
		#			#.

  "\U0001fb13",	#			..
		#			#.
		#			#.

  "\U0001fb10",	#			#.
		#			..
		#			#.

  "\U0001fb0f",	#			..
		#			..
		#			#.

  "\U0001fb04",	#			#.
		#			#.
		#			..

  "\U0001fb03",	#			..
		#			#.
		#			..

  "\U0001fb00",	#			#.
		#			..
		#			..

  " ",		# Space:		..
		#			..
		#			..
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

  argparser.add_argument(
	  "-H", "--high-density-semigraphics",
	  help = "Use 2x3 unicode block characters for rendering (smaller "
			"console needed but incorrect aspect ratio). Default: "
			"1x2 blocks",
	  action = "store_true"
	)

  args = argparser.parse_args()

  # Semigraphic-ize the keymap help strings
  keymap_help = [(" " + l + " ").\
			replace(" _", " \u250c").replace("_ ", "\u2510 ").\
			replace("_", "\u2500").replace("|", "\u2502").\
			replace(" +", " \u2514").replace("+ ", "\u2518 ").\
			replace("-", "\u2500").replace("<", "\u2190").\
			replace("^", "\u2191").replace(">", "\u2192").\
			replace("v", "\u2193")[1:-1]
			for l in keyboard_to_flipper_help]

  width = 64 if args.high_density_semigraphics else 128
  height = 22 if args.high_density_semigraphics else 32

  nb_display_lines = height + 2

  keymap_help_line_len = len(keymap_help[0])
  keymap_help_overlay_at_col = int((width - keymap_help_line_len) / 2)
  keymap_help_overlay_at_line = int((height - len(keymap_help)) / 2)

  # Connect to the Flipper Zero
  p = FlipperProto(serial_port = args.device)

  # Get the Flipper Zero's name
  flipper_name = "[ " + p.device_info["hardware_name"] + " ]"
  flipper_name_spc1 = " " * int((width - len(flipper_name)) / 2)
  flipper_name_spc2 = " " * (width - len(flipper_name_spc1) - len(flipper_name))

  # Bottom help line
  bottom_line = "[ Ctrl-K to show/hide keymap ]     [ Ctrl-C to stop ]"
  bottom_line_spc1 = " " * int((width - len(bottom_line)) / 2)
  bottom_line_spc2 = " " * (width - len(bottom_line_spc1) - len(bottom_line))

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
      if args.high_density_semigraphics:

        imglines = []
        for k in range(0, 1024, 384):

          c = [screen_data[i] + (screen_data[i + 128] << 8) + \
		((screen_data[i + 256] << 16) if i < 768 else 0xff0000) \
		for i in range(k, k + 128)]

          for j in (0, 3, 6, 9, 12, 15) + ((18, 21) if k < 768 else ()):
            imglines.append("".join([unicode_blocks_2x3[
						((c[i] >> j) & 7) | \
						(((c[i + 1] >> j) & 7) << 3)] \
					for i in range(0, 128, 2)]))

      else:
        imglines = ["".join([unicode_blocks_1x2[(screen_data[i] >> j) & 0b11]
				for i in range(k, k + 128)])
			for k in range(0, 1024, 128) for j in (0, 2, 4, 6)]

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

      # Print the final ASCII art
      print(flipper_name_spc1 + flipper_name + flipper_name_spc2 + CR + LF + \
		"".join([set_bg_color.format(ansi_8bit_black) + \
				set_fg_color.format(ansi_8bit_orange) + \
				l + attribute_reset + CR + LF \
				for l in imglines]) + \
		bottom_line_spc1 + bottom_line + bottom_line_spc2 + CR + \
		home_cursor)

      # Flush stdout to make sure the console is updated immediately
      sys.stdout.flush()

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
