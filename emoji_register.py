#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from getpass import getpass
import re
import sys
import json
import argparse
import yaml
from six.moves import input


class SlackAPI(object):
    def __init__(self, imagefile, emojiname, channelname, configfile):
        self.imagefile = imagefile
        self.emojiname = emojiname
        self.channelname = channelname
        self.setlogin(configfile)
        self.baseurl = "https://" + self.teamname + ".slack.com/"
        self.sessioninit()
        self.get_token_and_name()
        self.get_channellist()
        self.setemoji(self.channelname)

    def setlogin(self, configfile):
        config = {}
        if configfile:
            with open(configfile) as f:
                config = yaml.load(f)
        self.teamname = config["teamname"] if "teamname" in config else input("TeamName: ")
        self.email = config["email"] if "email" in config else input("E-mail: ")
        self.password = config["password"] if "password" in config else getpass("Password: ")
        if "channel" in config:
            self.channelname = config["channel"]

    def sessioninit(self):
        self.s = requests.Session()
        r = self.s.get(self.baseurl)
        soup = BeautifulSoup(r.text, "lxml")
        formdata = soup.find("form", attrs={"id": "signin_form"})
        params = {"email": self.email, "password": self.password}
        for i in formdata.find_all("input", attrs={"type": "hidden"}):
            params[i["name"]] = i["value"]
        self.s.post(self.baseurl, data=params)

    def get_token_and_name(self):
        messagehtml = self.s.get("https://api.slack.com/custom-integrations/legacy-tokens")
        messagesoup = BeautifulSoup(messagehtml.text, "lxml")
        self.token = messagesoup.find("input")["value"]
        userinfo = json.loads(
            self.s.post("https://slack.com/api/users.list", data={"token": self.token}).text)
        self.name = [user["name"] for user in userinfo["members"] if
                     "email" in user["profile"] and user["profile"]["email"] == self.email][0]

    def get_channellist(self):
        self.channellist = json.loads(
            self.s.post("https://slack.com/api/channels.list", data={"token": self.token}).text)["channels"]

    def channnel_post(self, channelname):
        channelid = ""
        try:
            channelid = [channel for channel in self.channellist if channel["name"] == channelname][0]["id"]
        except:
            print("Channel not found")
            exit(1)
        sendtext = '@{} 新しい絵文字を登録しました "{}" > :{}:'.format(self.name, self.emojiname, self.emojiname)
        self.s.post("https://slack.com/api/chat.postMessage",
                    data={"channel": channelid, "token": self.token, "link_names": "true", "username": "Dr.EMOJI",
                          "as_user": "false", "text": sendtext})

    def setemoji(self, channelname):
        emojilist = self.get_emoji_list()
        if self.emojiname in emojilist:
            print("emoji already exist")
        else:
            emojitxt = self.s.get(self.baseurl + "admin/emoji")
            soup = BeautifulSoup(emojitxt.text, "lxml")
            form = soup.find("form", attrs={"action": "/customize/emoji"})
            params = {"name": self.emojiname, "mode": "data"}
            for i in form.find_all("input", attrs={"type": "hidden"}):
                if "value" in i.attrs:
                    params[i["name"]] = i["value"]
            img = Image.open(self.imagefile)
            img.thumbnail((128, 128), Image.ANTIALIAS)
            image = BytesIO()
            img.save(image, img.format)
            files = {"img": (args.imagefile, image.getvalue())}
            res = self.s.post(self.baseurl + "/customize/emoji", files=files, data=params)
            if res:
                emojilist = self.get_emoji_list()
                if self.emojiname in emojilist:
                    print("Save Emoji")
                    self.channnel_post(channelname)
                else:
                    print("Failed")

    def get_emoji_list(self):
        emojilist = json.loads(self.s.post("https://slack.com/api/emoji.list", data={"token": self.token}).text)
        return emojilist["emoji"]


parser = argparse.ArgumentParser(description="Slack Emoji Save Script")
parser.add_argument("imagefile", action="store", type=str)
parser.add_argument("--name", "-n", action="store", type=str)
parser.add_argument("--channel", "-ch", default="emoji")
parser.add_argument("--config", "-c", action="store")
args = parser.parse_args()

args.imagefile = args.imagefile.replace("\\", "/")
if not args.name:
    args.name = re.split("[./]", args.imagefile)[-2]
    print("emoji name > ", args.name)

sa = SlackAPI(args.imagefile, args.name, args.channel, args.config)
