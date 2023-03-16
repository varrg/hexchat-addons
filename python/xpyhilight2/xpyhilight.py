"""Python 3 plugin for HexChat that prints highlights onto its own window.
"""

__module_name__		= "xPyHilight"
__module_version__	= "2.5"
__module_description__  = "Keeps track of highlights"
__module_author__	= "Dan Boklöv Palovaara <dan@boklov.com>"

import hexchat
import re
from time import strftime

options = {
	"window_name": ">>Hilights<<",
	"only_when_away": False,
	"prefix": "%C01,02 %H[%H{channel}%C01,02%H]%H %O$t"
}

def hilight(word, word_eol, userdata, attrs):
	if options["only_when_away"] and not hexchat.get_info("away"):
		return None
	
	if hexchat.get_prefs("gui_focus_omitalerts") and hexchat.get_info("win_status") == "active" and hexchat.find_context() == hexchat.get_context():
		return None
	
	data = {
		"channel": hexchat.get_info("channel"),
		"time": attrs.time or strftime(hexchat.get_prefs("stamp_text_format")), 
		"nick": word[0],
		"text": word[1],
		"mode": word[2] if len(word) > 2 else ""
	}

	tpl = options["prefix"] + (__message_tpl__ if userdata == "message" else __action_tpl__)

	# @todo are the highlights printed to the right window? otherwise also send server=hexchat.get_info("server")
	context = hexchat.find_context(channel=options["window_name"]) or open_window(channel=options["window_name"])
	context.prnt(convert_irc_codes(tpl).format(**data))

	return None

def open_window(server=None, channel=None):
	tab_newtofront = hexchat.get_prefs("gui_tab_newtofront")
	if tab_newtofront:
		hexchat.command("set -quiet gui_tab_newtofront 0")
	
	hexchat.command(f"query -nofocus {channel}")

	if tab_newtofront:
		hexchat.command(f"set -quiet gui_tab_newtofront {tab_newtofront}")
	
	context = hexchat.find_context(server=server, channel=channel)
	context.command("chanopt -quiet text_scrollback 0")
	context.command("chanopt -quiet text_logging 0")

	return context

def convert_irc_codes(str):
	cmap = {
		"%B": "\002",
		"%U": "\037",
		"%I": "\035",
		"%H": "\010",
		"%R": "\026",
		"%O": "\017",
		"%C": "\003",
		"%%": "%",
		"$t": "\t",
		"$1": "{nick}",
		"$2": "{text}",
		"$3": "{mode}",
		"$4": ""
	}

	return re.sub(r"(%[%CHBORUI]|\$(\d|t|a\d{3}))", lambda m: cmap.get(m[0], chr(int(m[0][2:])) if m[0][:2] == "$a" else m[0]), str)

__message_tpl__ = hexchat.get_info("event_text Channel Message")
__action_tpl__ = hexchat.get_info("event_text Channel Action")

hexchat.hook_print_attrs("Channel Msg Hilight", hilight, userdata="message")
hexchat.hook_print_attrs("Channel Action Hilight", hilight, userdata="action")

print(__module_name__, __module_version__, "loaded")
