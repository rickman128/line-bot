# -*- coding: utf-8 -*-
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import logging
import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
	LineBotApi, WebhookHandler
)
from linebot.exceptions import (
	InvalidSignatureError
)
from linebot.models import (
	MessageEvent, TextMessage, TextSendMessage,
)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from time import sleep


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
	print('Specify LINE_CHANNEL_SECRET as environment variable.')
	sys.exit(1)
if channel_access_token is None:
	print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
	sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# todays corona num in Fukui
def get_today_corona_fukui():
	options = Options()
	options.add_argument('--headless')
	driver = webdriver.Chrome(options=options)
	driver.implicitly_wait(20)
	sleep(2)
	driver.get("https://covid19.mhlw.go.jp/extensions/public/index.html")

	try:
		# test
		el = driver.find_element_by_id("curSituNewCaseKPI")
		num = el.text
		'''
		dropdown = driver.find_element_by_id("prefectures")
		select = Select(dropdown)
		#select.select_by_visible_text('福井')
		select.select_by_value('18')

		# 本日の新規感染者数（１日前くらい・・・？）
		div_days = driver.find_element_by_class_name("col4-pattern1_num")
		num = div_days.text
		logging.debug("num: ")
		logging.debug(num)
		'''
	except:
		logging.exception("error around selenium")

	driver.quit()
	# add
	return num

@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)

	return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
	num = get_today_corona_fukui()
	line_bot_api.reply_message(
		event.reply_token,
		TextSendMessage(text=str(num))
	)
'''
	if event.message.text == 'corona':
		num = get_today_corona_fukui()
		# reply
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(text=str(num))
		)
	else:
		# reply
		line_bot_api.reply_message(
			event.reply_token,
			TextSendMessage(text=event.message.text)
		)
'''

if __name__ == "__main__":
	port = int(os.getenv("PORT", 5000))
	app.run(host="0.0.0.0", port=port)