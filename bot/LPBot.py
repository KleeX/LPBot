# -*- coding: utf-8 -*-

from flask import Flask, request
from OpenSSL import SSL
import telepot
import json
from collections import namedtuple
import os

tokenLP = open('/home/pi/Documents/certs_telegram/token_lp.txt', 'r').read()
linkToJsonFile = '/home/pi/Documents/HomeProject/KeyWordsLP.json'
host = open('/home/pi/Documents/certs_telegram/host_lp.txt', 'r').read()
cert = '/home/pi/Documents/certs_telegram/cert.pem'
key = '/home/pi/Documents/certs_telegram/private.key'
port = 443

bot = telepot.Bot(tokenLP)
bot.setWebhook('https://%s:%s/%s' % (host, port, tokenLP), open(cert))
# print(bot.getMe())

app = Flask(__name__)
context = (cert, key)


class DataKeys(object):
    def __init__(self):
        self.key = ""
        self.value = ""


@app.route('/')
def hello():
    return 'Hello!'


def send_text_message(receiver, message):
    bot.sendMessage(receiver, message)


@app.route('/' + tokenLP, methods=["POST"])
def telegram_webhook():
    print('\n-----telegram works-----\n')
    try:
        update = request.get_json()
        print(update)
        if "message" in update:
            text = update["message"]["text"]
            if text is None:
                return "OK"
            chat_id = update["message"]["chat"]["id"]
            if text.startswith("@lp_text_bot ") and text.find("|") != -1:
                str_json = text[13:]
                send_text_message(chat_id, add_data_to_json_file(str_json.split("|")))
                return "OK"
            result = parse_data(text)
            if result is not None:
                send_text_message(chat_id, result)
    except:
        return "OK"
    return "OK"


def parse_data(message):
    file_json = open(linkToJsonFile, "r+b")
    json_data = json.load(file_json)
    str_result = None
    for item in json_data:
        try:
            if message == item["key"]:
                str_result = item["value"]
                if str_result is not None:
                    break
        except:
            continue
    return str_result


def add_data_to_json_file(values):
    print(values)
    json_file = open(linkToJsonFile, "r+b")
    data = json.load(json_file)
    for item in data:
        try:
            if values[0] == item["key"]:
                str_result = item["value"]
                if str_result is not None:
                    item["value"] = values[1]
                    json_file.seek(0)
                    json_file.write(str(json.dumps(data)))
                    json_file.truncate()
                    json_file.close()
                    return "Edited!"
        except:
            continue
    data.append({"key": values[0], "value": values[1]})
    json_file.seek(0)
    json_file.write(str(json.dumps(data)))
    json_file.truncate()
    json_file.close()
    return "Added!"


app.run('0.0.0.0', port, ssl_context=context, debug=True)
