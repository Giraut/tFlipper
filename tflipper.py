#!/usr/bin/python3
"""Flipper Zero remote control for the terminal
Version: 1.5.0
"""

## Modules
#

import re
import sys
import argparse
from time import time
from copy import copy
import queue
import threading
import multiprocessing
from readchar import key, readkey
from flipperzero_protobuf.flipper_proto import FlipperProto

try:
  import colorama
except:
  pass

try:
  from PIL import Image
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

# VT100 cursor invisible
set_cursor_invisible = ESC + "[?25l"

# VT100 cursor visible
set_cursor_visible = ESC + "[?25h"

# VT100 invisible text
set_text_invisible = ESC + "[8m"

# ANSI 8-bit color selection
set_bg_color = ESC + "[48;5;{}m"
set_fg_color = ESC + "[38;5;{}m"

# VT100 attributes reset
attributes_reset = ESC + "[0m"

# VT100 x lines up
x_lines_up = ESC + "[{}A"

# Predefined colors
ansi_8bit_black = 0
rgb_black1 = [0, 0, 0]
rgb_black2 = [0, 0, 1]

ansi_8bit_orange = 208
rgb_orange1 = [0xfe, 0x8a, 0x2c]
rgb_orange2 = [0xfe, 0x8a, 0x2d]

# 4-color palette for the GIF file: color 0 & 1 = orange, color 2 & 3 = black
gif_palette = rgb_orange1 + rgb_black1 + rgb_orange2 + rgb_black2

# Minimum and maximum duration of one GIF frame
min_gif_frame_duration_ms = 10 #ms	# because the GIF format encodes the
max_gif_frame_duration_ms = 655350 #ms	# frame duration in 1/100th of a second
					# in an unsigned short

# Format of the invisible timecode and button presses marker
invisible_tc_btn_marker_fmt = "[{:0.3f}s] [{}]"

# Precompiled regex for an invisible timecode and button presses marker with
# a non-empty list of button presses
re_tc_btn_marker = re.compile((set_text_invisible.replace("[", "\\[") + \
				"\[([0-9]+\.[0-9]{3})s\] " \
				"\[([lLdDuUrRoObB]+)\]" + \
				attributes_reset.replace("[", "\\[")))



## Routines
#

class argparse_gif_filename_parser(argparse.Action):
  """Argparse parser for a valid GIF filename
  """

  def __call__(self , parser, namespace, value, option_string = None):
    """__call__ method
    """

    if not value.upper().endswith(".GIF"):
      parser.error("{}: invalid GIF filename".format(value))

    setattr(namespace, self.dest, value)



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



def steg_encode(image, s):
  """ Encode a hidden string in the first line of an image that is 512 pixels
  wide or wider, with a 4-color palette such that:

  - Colors 0 & 2 are very close: color 0 encodes bit 0, color 2 encodes bit 1
  - Colors 1 & 3 are very close: color 1 encodes bit 0, color 3 encodes bit 1

  The string's characters' bits are encoded on the first line from left to
  right, big-endian (512 / 8 = 64 characters in total).

  If the string is shorter than 64 characters, the remaining bits are 0
  If the string is longer than 64 characters, only the first 64 characters
  are encoded into the image.
  """

  color_transforms = map(lambda c: ((0, 1, 0, 1), (2, 3, 2, 3))[int(c)],
				("".join(["{:08b}".format(ord(c)) \
						for c in s]) \
					+ "0" * 512)[:512])
  for x in range(512):
    image.putpixel((x, 0), next(color_transforms)[image.getpixel((x, 0))])



def steg_decode(image, palette):
  """ Decode a hidden string encoded by the steg_encode() function in the first
  line of an image that is 512 wide or wider, with a 4-color palette
  """

  s = ""

  try:

    for x in range(0, 512, 8):
      c = chr(sum([(0 if palette[image.getpixel((x + o, 0))] < 2 else 1) << \
			(7 - o) for o in range(8)]))
      if not c.isprintable() and c != ESC:
        break
      s += c

  except:
    s = ""

  return s



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

  argparser.add_argument(
	  "-t", "--txt",
	  help = "Text file to record the session into (play it back with "
			"tfreplay or replay button presses encoded into it "
			"with -r)",
	  type = str
	)

  argparser.add_argument(
	  "-g", "--gif",
	  help = "Animated GIF to record the session into",
	  action = argparse_gif_filename_parser
	)

  mutexargs = argparser.add_mutually_exclusive_group(required = False)

  mutexargs.add_argument(
	  "-rt", "--replay-buttons-from-txt",
	  help = "Text file session recording to replay button presses from "
			"(generated by -t)",
	  type = str
	)

  mutexargs.add_argument(
	  "-rg", "--replay-buttons-from-gif",
	  help = "GIF file session recording to replay button presses from "
			"(generated by -g)",
	  type = str
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

  keymap_help_line_len = len(keymap_help[0])
  keymap_help_overlay_at_col = int((width - keymap_help_line_len) / 2)
  keymap_help_overlay_at_line = int((height - len(keymap_help)) / 2)

  # If a text file to replay button presses from was specified, load it and
  # extract the button press events from it
  if args.replay_buttons_from_txt:
    with open(args.replay_buttons_from_txt, "r") as f:
      replay_buttons_at = [(float(t), b) \
				for t, b in re_tc_btn_marker.findall(f.read())]

  # If a GIF file to replay button presses from was specified, load it and
  # extract the button press events from it
  elif args.replay_buttons_from_gif:

    with Image.open(args.replay_buttons_from_gif) as gif:
      assert gif.is_animated
      assert gif.size == (512, 256)
      assert len(gif.palette.colors) == 4

      palette = gif.palette.colors

      replay_buttons_at = []
      for frame in range(gif.n_frames):
        gif.seek(frame)
        s = steg_decode(gif if gif.mode == "RGB" else gif.convert("RGB"),
			palette)
        replay_buttons_at.extend([(float(t), b) \
				for t, b in re_tc_btn_marker.findall(s)])

  # No text file or GIF file to replay button pressed from
  else:
    replay_buttons_at = None

  # Connect to the Flipper Zero
  p = FlipperProto(serial_port = args.device)

  # Get the Flipper Zero's name
  flipper_name = "[ " + p.device_info["hardware_name"] + " ]"

  # Left and right spacers for the Flipper Zero's name
  len_flipper_name_spc1 = int((width - len(flipper_name)) / 2)
  flipper_name_spc2 = " " * (width - len_flipper_name_spc1 - len(flipper_name))

  # Bottom help line
  bottom_line = "[ Ctrl-K to show/hide keymap ]     [ Ctrl-C to stop ]"

  # Left and right spacers for the bottom help line
  bottom_line_spc1 = " " * int((width - len(bottom_line)) / 2)
  bottom_line_spc2 = " " * (width - len(bottom_line_spc1) - len(bottom_line))

  # Spawn the thread to get keypresses
  q = multiprocessing.Queue()
  t = threading.Thread(target = input_thread, args = (q,))
  t.start()

  # Open the text file if the session is recorded in a text file
  rt = open(args.txt, "w", encoding = "utf-8") if args.txt else None

  # Create a list of frames and durations if the session is recorded in a GIF
  gif_frames = [] if args.gif else None
  gif_frame_durations_ms = [] if args.gif else None

  gif_frame_no = 0

  nb_lines_back_up = 0
  nb_lines_back_up_text_record = 0

  cursor_visible = True
  show_keymap = False

  start_time = None

  screen_data = b""
  update_display = True

  try:

    # Run until stopped by Ctrl-C
    while True:

      flipper_inputs = ""

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
            update_display = True

          # If the string isn't empty, send the event to the Flipper Zero and
          # store them for recording in the session text file in short form
          elif flipper_input:
            p.rpc_gui_send_input(flipper_input)
            i1, i2 = flipper_input.split()
            flipper_inputs += i2[0].lower() if i1 == "SHORT" else i2[0].upper()

        # The input thread exited normally so do the same thing
        else:
          raise KeyboardInterrupt

      # Get the current time and calculate the current timecode
      now = time()
      if start_time is None:
        start_time = now
      timecode = now - start_time
      if timecode < 0:
        timecode = 0

      # If we're due to replay Flipper Zero button presses, add them to the
      # inputs and replay them
      while replay_buttons_at and timecode >= replay_buttons_at[0][0]:

        _, btns = replay_buttons_at.pop(0)
        flipper_inputs += btns

        # Send the button press events to the Flipper Zero
        for b in btns:
          p.rpc_gui_send_input(("SHORT " if b.islower() else "LONG ") + \
				{"L": "LEFT", "D": "DOWN",
					"U": "UP", "R": "RIGHT",
					"O": "OK", "B": "BACK"}[b.upper()])

      # Get a screenshot from the Flipper Zero
      prev_screen_data = screen_data
      screen_data = p.rpc_gui_snapshot_screen()
      assert len(screen_data) == 1024
      screen_data_changed = screen_data != prev_screen_data

      # If the Flipper's display hasn't changed and no input was sent to the
      # Flipper, there is nothing more to do with this frame
      if not screen_data_changed and not update_display and not flipper_inputs:
        continue

      # Do we record GIF frames and do we have a reason to record this frame?
      if gif_frames is not None and (screen_data_changed or flipper_inputs):

        # Is there at least one stored GIF frame?
        if gif_frames:

          # The difference between this timecode and the previous GIF frame's
          # timecode is the previous GIF frame's duration
          prev_frame_duration_ms = (timecode - last_gif_frame_timecode) * 1000

          # Repeat the previous GIF frame as many times as needed, encode only
          # the frame number invisibly into the image then increment the
          # frame number
          while prev_frame_duration_ms > max_gif_frame_duration_ms + \
						min_gif_frame_duration_ms:
            image = copy(gif_frames[-1])
            steg_encode(image, "{}".format(gif_frame_no))
            gif_frame_no += 1
            gif_frame_durations_ms.append(max_gif_frame_duration_ms)
            gif_frames.append(image)
            prev_frame_duration_ms -= max_gif_frame_duration_ms

          # Add the duration of the last GIF frame
          gif_frame_durations_ms.append(max(prev_frame_duration_ms,
						min_gif_frame_duration_ms))

        # Convert the Flipper's screen data into an image and scale it up x4
        image_data = bytes([(screen_data[i] >> j) & 1 \
				for k in range(0, 1024, 128) \
				for j in range(8) \
				for i in range(k, k + 128)])
        image = Image.frombytes(mode = "P", size = (128, 64),
				data = image_data).\
				resize((512, 256), resample = Image.BOX)
        image.putpalette(gif_palette)

        # Encode the frame number, timecode and flipper inputs invisibly into
        # the image then increment the frame number
        steg_encode(image, "[{}] ".format(gif_frame_no) + \
				set_text_invisible + \
				invisible_tc_btn_marker_fmt.
					format(timecode, flipper_inputs) + \
				attributes_reset)
        gif_frame_no += 1

        # Add the image to the GIF frames
        gif_frames.append(image)
        last_gif_frame_timecode = timecode

      # Hide the cursor if needed
      if cursor_visible:
        sys.stdout.write(set_cursor_invisible)
        cursor_visible = False

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

      # Encode the invisible timecode and button presses marker into the left
      # spacer for the Flipper Zero's name
      tcbtns = invisible_tc_btn_marker_fmt.format(timecode, flipper_inputs)
      flipper_name_spc1 = set_text_invisible + tcbtns + attributes_reset + \
				" " * (len_flipper_name_spc1 - len(tcbtns))

      # Do we record the session in a text file and do we have a reason to
      # record this frame?
      if rt is not None and (screen_data_changed or flipper_inputs):

        # Generate the ANSI text for the record without help overlay or bottom
        # help line
        at = flipper_name_spc1 + flipper_name + flipper_name_spc2 + CR + LF + \
		"".join([set_bg_color.format(ansi_8bit_black) + \
				set_fg_color.format(ansi_8bit_orange) + \
				l + attributes_reset + CR + LF \
				for l in imglines]) + \
		x_lines_up.format(height + 1)

        # Save the ANSI text into the file
        rt.write(at)
        nb_lines_back_up_text_record = height + 1

      # Should we update the display?
      if screen_data_changed or update_display or flipper_inputs:

        # If the keymap help should be displayed, overlay it over the lines
        if show_keymap:
          for i, l in enumerate(keymap_help):
            imglines[keymap_help_overlay_at_line + i] = \
			imglines[keymap_help_overlay_at_line + i]\
				[:keymap_help_overlay_at_col] + \
			attributes_reset + \
			l + \
			set_fg_color.format(ansi_8bit_orange) + \
			imglines[keymap_help_overlay_at_line + i]\
				[keymap_help_overlay_at_col + \
					keymap_help_line_len:]

        # Generate the display ANSI text with help overlay and bottom help line
        at = flipper_name_spc1 + flipper_name + flipper_name_spc2 + CR + LF + \
		"".join([set_bg_color.format(ansi_8bit_black) + \
				set_fg_color.format(ansi_8bit_orange) + \
				l + attributes_reset + CR + LF \
				for l in imglines]) + \
		bottom_line_spc1 + bottom_line + bottom_line_spc2 + \
		x_lines_up.format(1) + CR + LF + x_lines_up.format(height + 1)

        # Print the ANSI text and flush the console so it's updated immediately
        sys.stdout.write(at)
        sys.stdout.flush()
        nb_lines_back_up = height + 1

        update_display = False

  except KeyboardInterrupt:
    pass

  except:
    raise

  finally:

    # Get the current time and calculate this last output's timecode
    now = time()
    if start_time is None:
      start_time = now
    timecode = now - start_time

    # If GIF frames are recorded and we have at least one frame, set this last
    # timecode as the final GIF frame's duration
    if gif_frames:

      # The difference between this timecode and the previous GIF frame's
      # timecode is the previous GIF frame's duration
      prev_frame_duration_ms = (timecode - last_gif_frame_timecode) * 1000

      # Repeat the previous GIF frame as many times as needed, encode only the
      # frame number invisibly into the image then increment the frame number
      while prev_frame_duration_ms > max_gif_frame_duration_ms + \
					min_gif_frame_duration_ms:
        image = copy(gif_frames[-1])
        steg_encode(image, "[{}]".format(gif_frame_no))
        gif_frame_no += 1
        gif_frame_durations_ms.append(max_gif_frame_duration_ms)
        gif_frames.append(image)
        prev_frame_duration_ms -= max_gif_frame_duration_ms

      # Add the duration of the final GIF frame
      gif_frame_durations_ms.append(max(prev_frame_duration_ms,
						min_gif_frame_duration_ms))

    # Output the last invisible timecode and button presses marker then skip
    # past the rendering
    sys.stdout.write(CR + set_text_invisible + \
			invisible_tc_btn_marker_fmt.
				format(timecode, flipper_inputs) + \
			attributes_reset + CR + LF * (nb_lines_back_up + 1))

    # If we record the session into a text file, output the same thing into it
    if rt is not None:
      rt.write(CR + set_text_invisible + \
		invisible_tc_btn_marker_fmt.
			format(timecode, flipper_inputs) + \
		attributes_reset + CR + LF * (nb_lines_back_up_text_record + 1))

    # Show the cursor again if needed
    if not cursor_visible:
      sys.stdout.write(set_cursor_visible)

    # Tell the input thread to stop if it hasn't stopped by itself already
    setattr(t, "do_run", False)

    # Join the thread
    t.join()

  # If GIF frames were recorded and we have at least one frame, save them as an
  # animated GIF
  if gif_frames:

    # Add a copy of the first and last frames with a very small duration
    # to the start and the end of the animation respectively, because
    # some video players don't play edge frames with the correct
    # duration -e.g. mplayer

    # Duplicate of the first frame with frame number -1 invisible encoded in it
    gif_frame_durations_ms[0] = max(gif_frame_durations_ms[0] - \
					min_gif_frame_duration_ms,
					min_gif_frame_duration_ms)
    image = copy(gif_frames[0])
    steg_encode(image, "[-1]")
    gif_frames.insert(0, image)
    gif_frame_durations_ms.insert(0, min_gif_frame_duration_ms)

    # Duplicate of the last frame with the last frame number, last timecode and
    # last flipper inputs invisibly encoded in it
    gif_frame_durations_ms[-1] = max(gif_frame_durations_ms[-1] - \
					min_gif_frame_duration_ms,
					min_gif_frame_duration_ms)
    image = copy(gif_frames[-1])
    steg_encode(image, "[{}] ".format(gif_frame_no) + \
				set_text_invisible + \
				invisible_tc_btn_marker_fmt.
					format(timecode, flipper_inputs)  + \
				attributes_reset)
    gif_frames.append(image)
    gif_frame_durations_ms.append(min_gif_frame_duration_ms)

    # Encode and save the animated GIF file
    gif_frames[0].save(args.gif, save_all = True,
			append_images = gif_frames[1:], optimize = False,
			duration = gif_frame_durations_ms, loop = 0)

  return 0



## Main program
#

if __name__ == "__main__":
  sys.exit(main())
