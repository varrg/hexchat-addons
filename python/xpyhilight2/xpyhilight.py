"""Python 3 plugin for HexChat that prints highlights onto its own window.
"""

__module_name__			= "xPyHilight"
__module_version__		= "2.5"
__module_description__	= "Keeps track of highlights"
__module_author__		= "Dan Boklöv Palovaara <dan@boklov.com>"

import hexchat
import re
from time import strftime

options = {
	"window": ">>Hilights<<",
	"time": "%H:%M",
	"only_away": False,
	"ignore": {"NickServ", "ChanServ", "InfoServ", "Q", "N"},
	"prefix": "%C01,02 %H[%H{channel}%C01,02%H]%H %O$t"
}

def callback(word, word_eol, userdata, attrs):
	if options["only_away"]:
		if hexchat.get_info("away") is None:
			return hexchat.EAT_NONE
	
	if any([hexchat.nickcmp(word[0], ignore) == 0 for ignore in options["ignore"]]):
		return hexchat.EAT_NONE
	
	#context = hexchat.find_context(server=xchat.get_info("server"), channel=options["window"])
	# @todo are the highlights printed to the right window?
	context = hexchat.find_context(channel=options["window"])

	data = {
		"channel": hexchat.get_info("channel"),
		"time": attrs.time or strftime(options["time"]),  # @todo what controls attr[time] format and can I get that format string and pass it to strftime?
		"nick": word[0],
		"text": word[1],
		"mode": word[2] if len(word) > 2 else ""
	}

	tab_newtofront = hexchat.get_prefs("gui_tab_newtofront")
	if tab_newtofront:
		hexchat.command("set -quiet gui_tab_newtofront 0")
	hexchat.command("query -nofocus {0}".format(options["window"]))
	if tab_newtofront:
		hexchat.command("set -quiet gui_tab_newtofront {0}".format(tab_newtofront))
	
	tpl = options["prefix"] + (__message_tpl__ if userdata == "message" else __action_tpl__)
	context.prnt(convert_irc_codes(tpl).format(**data))

	return hexchat.EAT_NONE

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

hexchat.hook_print_attrs("Channel Msg Hilight", callback, userdata="message")
hexchat.hook_print_attrs("Channel Action Hilight", callback, userdata="action")

print(__module_name__, __module_version__, "loaded")
