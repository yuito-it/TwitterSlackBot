import asyncio
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import schedule
import time

from db import getDB, addSubscribe, getSubscribeById, listSubscribe, getSubscribeByChannel, Subscribe, deleteSubscribe, getSendedTweetByTweetId, deleteSendedTweet, addSendedTweet, getSendedTweetByChannel, createDB
from twitterUtil import getTweets, getUser

# TODO: 4 development only
from dotenv import load_dotenv
from threading import Thread
load_dotenv()

session = getDB()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))


@app.command("/twitter")
def twitterCmd(ack, say, command):
    ack()
    command["text"] = command["text"].strip()
    options = command["text"].strip().split(" ")
    print(options[0])
    match(options[0]):
        case "list":
            asyncio.run(listSubscribeCmd(command, say))
        case "subscribe":
            asyncio.run(subscribedAccountRegistToSended(options, command))

            say("OK...Subscribed now")
        case "unsubscribe":
            currentSession = next(session)
            data = getSubscribeById(options[1], currentSession)
            deleteSubscribe(data, currentSession)
            say("Deleted")
        case _:
            say("invalid command")


async def cronTwitterJob():
    print("RunningTwitterJob")
    currentSession = next(session)
    for subscribe in listSubscribe(currentSession):
        tweets = []
        print(subscribe.id)
        if subscribe.reply:
            keyword = f"(from:{subscribe.target_user})"
            tweets = getTweets(keyword)
        else:
            keyword = f"(from:{subscribe.target_user}) -filter:replies"
            tweets = await getTweets(keyword)

        for tweet in tweets:
            if getSendedTweetByTweetId(tweet.id, currentSession):
                break
            app.client.chat_postMessage(
                channel=subscribe.channel,
                text=f"*@{tweet.user.screen_name}*\n{tweet.text}"
            )
            addSendedTweet(tweet.id, subscribe.channel, currentSession)

        for sendedTweet in getSendedTweetByChannel(subscribe.channel, currentSession):
            if sendedTweet.tweet_id not in [tweet.id for tweet in tweets]:
                deleteSendedTweet(sendedTweet.id, currentSession)


def run_schedule():
    while True:
        schedule.run_pending()
        print("pendingTwitterJob")
        time.sleep(1)


schedule.every(10).minutes.do(cronTwitterJob)


async def subscribedAccountRegistToSended(options, command):
    currentSession = next(session)
    subOptions = options[2:]

    data = Subscribe(
        channel=command["channel_id"],
        target_user=options[1],
        by_user=command["user_id"],
        retweet=("+RT" in subOptions),
        reply=("+Reply" in subOptions)
    )

    addSubscribe(data, currentSession)
    if data.reply:
        keyword = f"(from:{data.target_user})"
        tweets = getTweets(keyword)
    else:
        keyword = f"(from:{data.target_user}) -filter:replies"
        tweets = await getTweets(keyword)
    for tweet in tweets:
        addSendedTweet(tweet.id, data.channel, currentSession)


async def listSubscribeCmd(command, say):
    currentSession = next(session)
    blockTemp = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Subscribed users*"
            }
        },
        {
            "type": "divider"
        }
    ]
    for subscribe in getSubscribeByChannel(command["channel_id"], currentSession):
        user = await getUser(subscribe.target_user)
        section = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{user[0].name}(@{user[0].screen_name})*\nRT: {subscribe.retweet}\nReply: {subscribe.reply}"
            },
            "accessory": {
                "type": "image",
                "image_url": user[0].profile_image_url,
                "alt_text": "Icon"
            }
        }
        blockTemp.append(section)
        say(blocks=blockTemp, text="List of subscribe user")


if __name__ == "__main__":
    # asyncio.run(cronTwitterJob())
    createDB()
    thread = Thread(target=run_schedule)
    thread.start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
