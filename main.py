import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import schedule
import time

from db import getDB, addSubscribe, getSubscribeById, listSubscribe, getSubscribeByChannel, Subscribe, deleteSubscribe
from twitterUtil import getTweets, getUser


session = getDB()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()


@app.command("/twitter")
def twitterCmd(ack, say, command):
    ack()
    command["text"] = command["text"].strip()
    options = command["text"].strip()
    match(options[0]):
        case "list":
            blockTemp = [
                {
                    "type": "section",
                    "text": {
                            "type": "mrkdwn",
                        "text": "**Subscribed users**"
                    }
                },
                {
                    "type": "divider"
                }
            ]
            for subscribe in getSubscribeByChannel(command["channel_id"], session):
                section = {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"**{getUser(subscribe.target_user)[0].name}({getUser(subscribe.target_user)[0].screen_name}**\nRT: {subscribe.retweet}\nReply: {subscribe.reply}"
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": getUser(subscribe.target_user)[0].profile_image_url,
                        "alt_text": "Icon"
                    }
                }
                blockTemp.append(section)
            say(blockTemp)
        case "subscribe":
            data = Subscribe(
                id=id,
                channel=command["channel"],
                target_user=options[1],
                by_user=command["user"],
                retweet=((options[2] == "+RT") or (options[3] == "+RT")),
                reply=((options[2] == "+Reply") or (options[3] == "+Reply"))
            )
            addSubscribe(data, session)
            say("OK...Subscribed now")
        case "unsubscribe":
            data = getSubscribeById(options[1], session)
            deleteSubscribe(data, session)
            say("Deleted")
        case _:
            say("invalid command")


def cronTwitterJob():
    for subscribe in listSubscribe(session):
        tweets = []
        if subscribe.reply:
            keyword = f"(from:{subscribe.target_user}) -filter:replies"
            tweets = getTweets(keyword)
        else:
            keyword = f"(from:{subscribe.target_user})"
            tweets = getTweets(keyword)

        for tweet in tweets:
            app.client.chat_postMessage(
                channel=subscribe.channel,
                text=f"**@{tweet.user.screen_name}**\n{tweet.text}"
            )
        
        


schedule.every(10).minutes.do(cronTwitterJob)

while True:
    schedule.run_pending()
    time.sleep(1)
