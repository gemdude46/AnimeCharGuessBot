import asyncio
import datetime
import discord

import constants

RARITY_STRINGS = (
    '★☆☆☆☆',
    '★★☆☆☆',
    '★★★☆☆',
    '★★★★☆',
    '★★★★★',
    '✪✪✪✪✪'
)

def rarity_string(rarity):
    '''
    Get the star value text for a rarity.
    '''
    return RARITY_STRINGS[rarity]


def create_embed(title, desciption, color = constants.EMBED_COLOR, thumbnail = None, image = None, footer = None):
    '''
    Creates a Discord embed containing text, and optionally other properties.
    '''

    embed = discord.Embed(
        type = "rich",
        title = title,
        description = desciption,
        color = constants.EMBED_COLOR,
        timestamp = datetime.datetime.utcnow()
    )

    if thumbnail is not None:
        embed.set_thumbnail(url = thumbnail)

    if image is not None:
        embed.set_image(url = image)

    if footer is not None:
        embed.set_footer(text = footer)
    
    return embed


async def page(bot, args, waifus, title, page_no = None):
    '''
    Creates a paginated display of a list of waifus.
    Paging is controlled by Discord buttons, and is locked if too much time passes since the last use.
    '''

    if not waifus:
        await args.message.reply(embed = create_embed(
            title,
            "There are no waifus here!"
        ))
        return
    
    pages = 1 + (len(waifus) - 1) // constants.PROFILE_PAGE_SIZE

    page_no = (
        0 if page_no is None
        else page_no % pages if page_no < 1
        else min(page_no, pages) - 1
    )

    # Create the text for each page.
    page_texts = []

    for i in range(pages):
        lines = []

        for waifu in waifus[i * constants.PROFILE_PAGE_SIZE : (i + 1) * constants.PROFILE_PAGE_SIZE]:
            lines.append(str(waifu))

        page_texts.append('\n'.join(lines))

    embed = create_embed(title + f' - Page {page_no + 1}/{pages}', page_texts[page_no])

    if pages > 1:
        # There are multiple pages.

        prev_button = discord.ui.Button(label = '⬅ Prev')
        next_button = discord.ui.Button(label = 'Next ➡')

        button_queue = asyncio.Queue()

        async def prev_cb(interaction):
            if interaction.user.id == args.user.id:
                await button_queue.put(-1)

        async def next_cb(interaction):
            if interaction.user.id == args.user.id:
                await button_queue.put(1)

        prev_button.callback = prev_cb
        next_button.callback = next_cb

        view = discord.ui.View(timeout = constants.PROFILE_TIMEOUT)
        view.add_item(prev_button)
        view.add_item(next_button)

        message = await args.message.reply(embed = embed, view = view)

        try:
            while True:
                # Wait on input from buttons.
                movement = await asyncio.wait_for(button_queue.get(), constants.PROFILE_TIMEOUT)

                page_no += movement
                page_no %= pages

                # Merge multiple quick presses together.
                if button_queue.empty():
                    embed = create_embed(title + f' - Page {page_no + 1}/{pages}', page_texts[page_no])

                    await message.edit(embed = embed, view = view)

        except asyncio.TimeoutError:
            # No activity for a while, so disable the buttons.
            prev_button.callback = next_button.callback = None
            prev_button.disabled = next_button.disabled = True

            view = discord.ui.View()
            view.add_item(prev_button)
            view.add_item(next_button)

            await message.edit(embed = embed, view = view)
    
    else:
        # There is only one page, so just display that.
        await args.message.reply(embed = embed)
