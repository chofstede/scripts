'''
Script to let a blink(1) pulsate red on a Mastodon notification

Usage instructions:

- Install asyncio, certifi, aiomast and blink1 Python libraries:
  $ pip install asyncio certifi aiomast blink1

- Create Mastodon API Token at https://$instance/settings/applications

- Set Environment variable MASTODON_TOKEN and run script
  $ MASTODON_TOKEN=$some_token python mastoblink.py
'''

import asyncio
import os
import ssl
import time
import certifi
from aiomast import MastodonAPI
from blink1.blink1 import Blink1

MASTODON_INSTANCE = 'some.mastodon.instance.demo'
ACCESS_TOKEN = os.environ['MASTODON_TOKEN']

async def main():
    blinky = Blink1()
    blinky.off() 

    api = MastodonAPI(MASTODON_INSTANCE)
    api.set_access_token(ACCESS_TOKEN)
    api.ssl = ssl.create_default_context(cafile=certifi.where())

    instance = await api.instance.info()
    config = instance['configuration']
    streaming_url = config['urls']['streaming']

    async with api.session:
        while True:
            print('connecting to mastodon stream')
            stream = await api.websockets.connect(streaming_url)
            await stream.subscribe('user:notification')
            print('streaming')
            print('')
            async for event in stream:
                if event['event'] == 'notification':
                    blinky.fade_to_rgb(1000, 255, 0, 0) 
                    time.sleep(1.5)
                    blinky.fade_to_rgb(1000, 0, 0, 0, 0)
                    print(event['data'])
            print('disconnected')

asyncio.run(main())
