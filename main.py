import asyncio
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import nest_asyncio
nest_asyncio.apply()

import schedule
import time

from db import (
    getDB,
    addSubscribe,
    listSubscribe,
    getSubscribeByChannel,
    Subscribe, deleteSubscribe,
    getSendedTweetByTweetId,
    deleteSendedTweet,
    addSendedTweet,
    getSendedTweetByChannel,
    createDB)
from twitterUtil import getTweets, getUser

session = getDB()

app = App(token=os.getenv("SLACK_BOT_TOKEN"))


@app.command("/twitter")
def twitterCmd(ack, say, command):
    ack()
    command["text"] = command["text"].strip()
    options = command["text"].strip().split(" ")
    match(options[0]):
        case "list":
            print("[->] list")
            asyncio.run(listSubscribeCmd(command, say))
        case "subscribe":
            print("[->] subscribe")
            asyncio.run(subscribedAccountRegistToSended(options, command))
            say("OK...Subscribed now")
        case "unsubscribe":
            print("[->] unsubscribe")
            asyncio.run(unsubscribeCmd(command, say, options))
        case _:
            say("invalid command")


async def cronTwitterJob():
    """
    Asynchronous function to perform a scheduled job that fetches tweets and posts them to a specified channel.

    The function iterates over a list of subscriptions, fetches tweets based on the subscription's criteria, 
    and posts the tweets to the corresponding channel. It also manages the state of sent tweets to avoid 
    duplicate postings and cleans up tweets that are no longer relevant.

    Steps:
    1. Print a log message indicating the start of the job.
    2. Get the current session.
    3. Iterate over each subscription.
    4. Fetch tweets based on the subscription's criteria (with or without replies).
    5. Post each tweet to the specified channel if it hasn't been posted before.
    6. Add the tweet to the list of sent tweets.
    7. Clean up sent tweets that are no longer relevant.

    Note:
    - The function uses asynchronous calls to fetch tweets.
    - The function assumes the existence of several helper functions:
      - `listSubscribe(session)`: Returns a list of subscriptions.
      - `getTweets(keyword)`: Fetches tweets based on the given keyword.
      - `getSendedTweetByTweetId(tweet_id, session)`: Checks if a tweet has already been sent.
      - `addSendedTweet(tweet_id, channel, session)`: Adds a tweet to the list of sent tweets.
      - `getSendedTweetByChannel(channel, session)`: Gets the list of sent tweets for a channel.
      - `deleteSendedTweet(sended_tweet_id, session)`: Deletes a sent tweet from the list.

    """
    print("[-] cronTwitterJob")
    currentSession = next(getDB())
    for subscribe in listSubscribe(currentSession):
        tweets = []
        print(subscribe.id)
        if subscribe.reply:
            keyword = f"(from:{subscribe.target_user})"
            tweets = await getTweets(keyword)
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
    print("[-] cronTwitterJob end")


def cron():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_schedule())
    loop.close()


schedule.every(1).minutes.do(cron)


def run_schedule():
    while True:
        time.sleep(60)
        asyncio.run(cronTwitterJob())


async def subscribedAccountRegistToSended(options, command):
    """
    Registers a subscribed account and processes its tweets.

    This function takes in options and a command, creates a subscription
    record, and retrieves tweets from the subscribed account. Depending on
    the options provided, it will either include replies or filter them out.
    The retrieved tweets are then added to the sent tweets record.

    Args:
        options (list): A list of options where the first element is ignored,
                        the second element is the target user, and the rest are
                        additional options such as "+RT" for retweets and "+Reply"
                        for replies.
        command (dict): A dictionary containing command details such as "channel_id"
                        and "user_id".

    Returns:
        None
    """
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

    return


async def listSubscribeCmd(command, say):
    """
    Handles the 'list subscribe' command by retrieving and displaying a list of subscribed users for a given channel.

    Args:
        command (dict): A dictionary containing information about the command, including the channel ID.
        say (function): A function to send messages back to the channel.

    Returns:
        None

    The function performs the following steps:
    1. Retrieves the current session.
    2. Initializes a block template for the message.
    3. Iterates over the list of subscribed users for the given channel.
    4. For each subscribed user, retrieves user details and constructs a section block with user information.
    5. Appends the section block to the block template.
    6. Sends the constructed message back to the channel using the `say` function.
    """
    currentSession = next(getDB())
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


async def unsubscribeCmd(command, say, options):
    """
    Handles the unsubscribe command.

    This asynchronous function processes an unsubscribe command by looking up a subscription
    based on the provided command text. If the subscription is found, it deletes the subscription
    and sends a confirmation message. If the subscription is not found, it sends a "Not found" message.

    Args:
        command (dict): A dictionary containing the command details. The subscription ID is expected
                        to be in the "text" field of this dictionary.
        say (function): A function to send messages back to the user.

    Returns:
        None
    """
    currentSession = next(session)
    subscribe = getSubscribeByChannel(command["channel_id"], currentSession)
    subscribe = next(
        (sub for sub in subscribe if sub.target_user == options[1]), None)
    if subscribe:
        deleteSubscribe(subscribe.id, currentSession)
        say("Deleted")
    else:
        say("Not found")

if __name__ == "__main__":
    createDB()
    thread = Thread(target=run_schedule)
    thread.start()
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()
