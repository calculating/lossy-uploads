base = 'https://discord.com/api/v10/'

import os
token = os.environ['DISC_TOK']
headers = {
    "Authorization": f"{token}"
}

if not os.path.exists('jsons'):
    os.makedirs('jsons')

import sqlite3
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    message_id TEXT PRIMARY KEY,
    channel_id TEXT,
    guild_id TEXT,
    content TEXT,
    author_username TEXT,
    timestamp DATETIME
)
''')

conn.commit()

import json
meta_file = "meta.json"
try:
    with open(meta_file, 'r') as f:
        meta_data = json.load(f)
except FileNotFoundError:
    meta_data = {}

import requests


valid_ids = ['1147040380672544808', '1151446856031805460', '1105155817788944434', '1111418775284228157']


def get_guilds():
    r = requests.get(base + 'users/@me/guilds?after=0', headers=headers)
    guilds = r.json()
    if len(guilds) == 100:
        while True:
            r = requests.get(base + f'users/@me/guilds?after={guilds[0]["id"]}', headers=headers)
            guilds += r.json()
            if len(r.json()) < 100:
                break
    return guilds

def get_channels(guild_id):
    r = requests.get(base + f'guilds/{guild_id}/channels?after=0', headers=headers)
    channels = r.json()
    if len(channels) == 100:
        while True:
            r = requests.get(base + f'guilds/{guild_id}/channels?after={channels[0]["id"]}', headers=headers)
            channels += r.json()
            if len(r.json()) < 100:
                break
    return channels

def get_messages(channel_id):
    if meta_data.get(channel_id):
        r = requests.get(base + f'channels/{channel_id}/messages?after={meta_data[channel_id]}&limit=100', headers=headers)
    else:
        print('no meta')
        r = requests.get(base + f'channels/{channel_id}/messages?after=0&limit=100', headers=headers)
    messages = r.json()
    if len(messages) == 100:
        while True:
            r = requests.get(base + f'channels/{channel_id}/messages?after={messages[0]["id"]}&limit=100', headers=headers)
            messages += r.json()
            print(r.json())
            if len(r.json()) < 100:
                break

    try:
        if messages[0]['id']:
            print('adding new meta')
            meta_data[channel_id] = messages[0]['id']
    except Exception as e:
        print(e)
    
    return messages


def get_dm_channels():
    r = requests.get(base + 'users/@me/channels?after=0', headers=headers)
    channels = r.json()
    if len(channels) == 100:
        while True:
            r = requests.get(base + f'users/@me/channels?after={channels[0]["id"]}', headers=headers)
            channels += r.json()
            if len(r.json()) < 100:
                break
    return channels


guilds = get_guilds()

for guild in guilds:
    guild_id = guild['id']
    print(guild['name'])
    if guild_id not in valid_ids:
        continue

    channels = get_channels(guild_id)
    messages = []
    for channel in channels:
        channel_id = channel['id']
        new_messages = get_messages(channel_id)
        if 'code' in new_messages:
            continue
        messages += new_messages
    
    print(len(messages))
    for message in messages:
        message_data = (
            message['id'], channel_id, guild_id, message['content'],
            message['author']['username'], message['timestamp']
        )
        cursor.execute("INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?, ?, ?)", message_data)

        # Save as individual JSON
        filename = f"./jsons/{guild_id}-{channel_id}-{message['id']}.json"
        with open(filename, 'w') as f:
            json.dump(message, f)

    with open(meta_file, 'w') as f:
        json.dump(meta_data, f)
        

conn.commit()
conn.close()
messages_url = base + f"channels/1021567104652152932/messages?limit=100&after=0"
response = requests.get(messages_url, headers=headers)
messages = response.json()
print(messages[-1]["content"])
