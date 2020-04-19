import pykakasi
import logging
import requests
import subprocess
from googletrans import Translator
from telegram.ext import *
import xml.etree.ElementTree as ET

#japlearningbot
token = ""

import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
					level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
	"""Send a message when the command /start is issued."""
	update.message.reply_text('Hey there!')

def help(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_markdown_v2("1\. */new*\n_Gets new daily Japanese word update_\n\n2\. */transjp*\n_Translates text into Japanese_\n`/transjp hello`\n\n3\. */kanji2furi*\n_Converts Kanji into Furigana_\n`/kanji2furi かな漢字交じり文`")

def refresh():
	#repeat once per 24 hours 
	url = "https://wotd.transparent.com/rss/ja-widget.xml"
	filename = "jap.xml"
	r = requests.get(url)
	#https://stackoverflow.com/questions/7243750/download-file-from-web-in-python-3
	file = open(filename, 'wb')
	for chunk in r.iter_content(100000):
		file.write(chunk)
	file.close()
	try:
		tree = ET.parse('jap.xml')
		root = tree.getroot()
		r = requests.get(root[0][4].text)
		pronounciation_url = "pronounciation_url.mp3"
		file = open(pronounciation_url, 'wb')
		for chunk in r.iter_content(100000):
			file.write(chunk)
		file.close()
		r = requests.get(root[0][7].text)
		sample_pronounciation_url = "sample_pronounciation_url.mp3"
		file = open(sample_pronounciation_url, 'wb')
		for chunk in r.iter_content(100000):
			file.write(chunk)
		file.close()
	except:
		update.message.reply_markdown_v2("Error!")

def kanji_to_furigana(update, context):
	text = " ".join(context.args)
	if (text):
		kakasi = pykakasi.kakasi()
		kakasi.setMode("J","aF") # Japanese to furigana
		kakasi.setMode("H","aF") # Japanese to furigana
		conv = kakasi.getConverter()
		result = conv.do(text)
		update.message.reply_text(result)
	else:
		update.message.reply_markdown_v2("_Usage:_ */kanji2furi* かな漢字交じり文")

def translate(update, context):
	translator = Translator()
	user_says = " ".join(context.args)
	if (user_says):
		word = translator.translate(user_says, dest='ja')
		update.message.reply_text(word.text)
	else:
		update.message.reply_markdown_v2("_Usage:_ */transjp* hello")	

def new(update, context):
	update.message.reply_markdown_v2('_Getting latest updates\.\._')
	refresh()
	try:
		tree = ET.parse('jap.xml')
		root = tree.getroot()
		update.message.reply_html("<b>Date:</b> {}\n\n<b>Wordtype:</b> {}\n\n<b>Nihongo word:</b> {}\n\n<b>Romanji:</b> {}\n\n<b>English translation:</b> {}\n\n<b>Example Nihongo sentence:</b>\n {}\n\n<b>Example Nihongo sentence translation in English:</b>\n {}\n\n<b>Example Nihongo sentence translation in Romanji:</b>\n {}\n\n" .format(root[0][0].text, root[0][2].text,root[0][3].text, root[0][9].text, root[0][5].text, root[0][6].text, root[0][8].text, root[0][10].text))
		url = "https://api.telegram.org/bot" + str(token) + "/sendDocument?chat_id=" + str(update.effective_message.chat_id)
		subprocess.call(['curl', '-F', 'document=@pronounciation_url.mp3;filename=' + root[0][9].text + '.mp3', url])
		subprocess.call(['curl', '-F', 'document=@sample_pronounciation_url.mp3;filename="' + root[0][10].text + '.mp3"', url])
	except:
		update.message.reply_markdown_v2("Error!")

def error(update, context):
	"""Log Errors caused by Updates."""
	logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
	updater = Updater(token, use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# on different commands - answer in Telegram
	dp.add_handler(CommandHandler("hi", start))
	dp.add_handler(CommandHandler("help", help))
	dp.add_handler(CommandHandler("info", help))
	dp.add_handler(CommandHandler("new", new))
	dp.add_handler(CommandHandler("transjp", translate))
	dp.add_handler(CommandHandler("kanji2furi", kanji_to_furigana))

	dp.add_error_handler(error)
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()
