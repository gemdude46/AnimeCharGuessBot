import datetime
import discord
import time
from urllib.parse import urlparse

async def parse_user(text, guild):
    '''
    Get a member object from a string.
    The string can be either a user id, a ping, or a name.
    '''

    if text.isnumeric() and len(text) == 18:
        # It's a user id.
        user_id = text

    elif text.startswith('<@'):
        # It's a string.
        user_id = ''.join([
            char
            for char in text
            if char.isnumeric()
        ])
    
    else:
        # It might be a name.
        matches = []

        for member in guild.members:
            if text in member.display_name.lower() or text in member.name.lower():
                matches.append(member)

        if len(matches) == 1:
            # Exactly one match, so it's them.
            user_id = matches[0].id

        else:
            return None
    
    try:
        return await guild.fetch_member(user_id)

    except (discord.errors.NotFound, discord.errors.HTTPException):
        return None


def is_int(string):
    '''
    Test if string is a valid base 10 integer.
    '''
    return string and (len(string) == 1 and string.isnumeric()) or (string[1:].isnumeric() and string[0] in '-123456789')


def avatar(user, res = 128):
    '''
    Get the URL of a user's avatar at a resolution.
    '''

    a = user.avatar

    if a is None:
        # No avatar data, return default avatar.
        return 'https://discord.com/assets/3c6ccb83716d1e4fb91d3082f6b21d77.png'

    url = urlparse(a.url)

    return f'{url.scheme}://{url.netloc}{url.path}?size={res}'


def next_daily_reset():
    '''
    Get the Unix timestamp of the next daily bonus reset.
    '''

    prev_daily_reset = datetime.datetime.now().replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    next_daily_reset = prev_daily_reset + datetime.timedelta(days = 1)
    unix = int(time.mktime(next_daily_reset.timetuple()))

    return unix
