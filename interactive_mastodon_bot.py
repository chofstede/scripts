from mastodon import Mastodon
import re
import os
import openai

# Replace these with your Mastodon and OpenAI credentials
instance_url = '!!FILLME!!'
access_token = '!!FILLME!!'
openai.api_key = "!!FILLME!!"

# Create an instance of Mastodon
mastodon = Mastodon(
    access_token=access_token,
    api_base_url=instance_url
)

# File to store the replied message IDs
data_file = 'replied_messages.txt'

def load_replied_messages():
    replied_messages = set()
    if os.path.exists(data_file):
        with open(data_file, 'r') as file:
            replied_messages = set(line.strip() for line in file)
    return replied_messages

def save_replied_messages(replied_messages):
    with open(data_file, 'w') as file:
        file.write('\n'.join(str(message_id) for message_id in replied_messages))

# Set to keep track of replied messages
replied_messages = load_replied_messages()

def get_unreplied_mentions():
    # Fetching mentions
    mentions = mastodon.notifications()
    unreplied_mentions = []

    for mention in mentions:
        if mention["type"] == "mention":
            status_id = mention["status"]["id"]
            if str(status_id) not in replied_messages:  # Ensure message ID is a string
                unreplied_mentions.append(mention)
                replied_messages.add(str(status_id))  # Ensure message ID is a string

    return unreplied_mentions

def reply_to_mentions():
    unreplied_mentions = get_unreplied_mentions()

    for mention in unreplied_mentions:
        account_id = mention["account"]["id"]
        content = mention["status"]["content"]

        # Extract the message content without any HTML tags
        message = re.sub(r'<.*?>', '', content)

        # Send user message to OpenAI API to get a response
        prompt = {"role": "user", "content": message}
        completion = openai.ChatCompletion.create(
          model="gpt-4",
          messages=[
            prompt
          ]
        )

        # Post the reply
        mastodon.status_post(f"@{mention['account']['acct']} {completion.choices[0].message.content}", in_reply_to_id=mention["status"]["id"], visibility="direct")

    # Save the replied message IDs
    save_replied_messages(replied_messages)

if __name__ == '__main__':
    reply_to_mentions()
