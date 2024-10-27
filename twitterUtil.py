# import asyncio
import os
from twikit import Client

auth_info_1 = os.getenv('TWITTER_AUTH_INFO_1')
auth_info_2 = os.getenv('TWITTER_AUTH_INFO_2')
password = os.getenv('TWITTER_PASSWORD')

# Initialize client
client = Client('ja')


async def getTweets(keyword):
    if os.path.exists('cookies.json'):
        client.load_cookies('cookies.json')
    else:
        await client.login(
            auth_info_1=auth_info_1,
            auth_info_2=auth_info_2,
            password=password
        )
        client.save_cookies('cookies.json')

    tweets = await client.search_tweet(keyword, 'Latest', count=10)

    for tweet in tweets:
        print(f"Tweet ID: {tweet.id}")
        print(f"User: {tweet.user.screen_name}")
        print(f"Text: {tweet.text}")
        print('-' * 50)

    client.logout()

    return tweets


async def getUser(keyword):
    if os.path.exists('cookies.json'):
        client.load_cookies('cookies.json')
    else:
        await client.login(
            auth_info_1=auth_info_1,
            auth_info_2=auth_info_2,
            password=password
        )
        client.save_cookies('cookies.json')

    users = await client.search_user(keyword, count=1)

    for user in users:
        print(f"name: {user.name}")
        print(f"Screen name: {user.screen_name}")
        print('-' * 50)

    client.logout()

    return users


# keyword = "(from:@smiNoter) -filter:replies"
# keyword = "smiNoter"
# asyncio.run(getUser(keyword))
