"""Here are your needed imports you may need to add to these depending on what your doing"""

import discord
import asyncio
from discord.ext import commands
from asyncio import TimeoutError
from pizzapy import Customer, StoreLocator, Order

"""
This creates the class your cog runs in, 'ExampleCog' should be replaced with whatever you want your cog name to be.
"""


class BotCommands(commands.Cog):
    """This creates and defines the needed info for you"""

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title='Help Command',
            description="This bot is still in beta but WILL ACTUALLY ORDER FROM DOMINO'S IF YOU ACCEPT AN ORDER"
            )
        embed.add_field(name='User Info',
                        value='User info is NOT saved and only cash orders can be made for security reasons.',
                        inline=False)
        embed.add_field(
            name='The d.order command',
            value="""
                The order command will first DM you for your address and other info needed for an order, after that return to the page to add items to your order.
                Use ⬅️ and  ➡️ to navivgate a page at a time.  The other emojis will jump to the page of the category matching the image. Use the green check to finish 
                your order and use the red X to cancel.
                """
        )

        embed.add_field(name="Number of guilds", value=str(len(self.bot.guilds)), inline=False)
        await ctx.send(embed=embed)

    # noinspection PyTypeChecker
    @commands.command(

    )
    async def order(self, ctx):

        message = await ctx.send(ctx.author.mention, embed=discord.Embed(
            title='Please Check Your DMs to supply address and name info',
            color=0xde2939
        ))

        if ctx.author.id != 000000:
            while True:
                try:
                    f_name = await self.answer(ctx, "What is your first name?", 500)
                    l_name = await self.answer(ctx, "What is your last name?", 500)
                    email = await self.answer(ctx, "What is your email?", 500)
                    phone = await self.answer(ctx, "What is your phone number?", 500)
                    street = await self.answer(ctx, "What is your street address?", 500)
                    city = await self.answer(ctx, "What is your city?", 500)
                    state = await self.answer(ctx, "What is your state?", 500)
                    zip_code = await self.answer(ctx, "What is your zip code?", 500)
                except TimeoutError:
                    await ctx.author.send(embed=discord.Embed(title='Order Creation has timed out! Please start over'))

                embed = discord.Embed(title='Please verify your info.')
                embed.add_field(name='Name', value=f"{f_name} {l_name}", inline=False)
                embed.add_field(name='Email', value=email, inline=True)
                embed.add_field(name='Phone', value=phone, inline=True)
                embed.add_field(name='Street Address', value=street, inline=False)
                embed.add_field(name='City', value=city)
                embed.add_field(name='State', value=state)
                embed.add_field(name='Zip Code', value=zip_code)

                confirmation = await ctx.author.send(embed=embed)

                def c_check(r, a):
                    return confirmation.id == r.message.id and a.id == ctx.author.id

                emoji = await self.reaction(ctx.author, confirmation, ("✅", "❌"), 45)

                if emoji == "✅":
                    await ctx.author.send(embed=discord.Embed(
                        title='Your all set return to the channel you started this command in to continue your order!',
                        color=0xde2939
                    ))
                    break
                else:
                    embed = discord.Embed(title='Please resupply your info.')
                    await ctx.author.send(embed=embed)
        else:
            f_name = 'jim'
            l_name = 'bo'
            email = 'email'
            phone = '123'
            street = '24 S. Prospect'
            city = 'Clarendon Hills'
            state = 'il'
            zip_code = '60514'
        await message.edit(embed=discord.Embed(title='LOADING', color=0xde2939))

        customer = Customer(f_name, l_name, email, phone,
                            f"{street},{city},{state},{zip_code}")
        store = StoreLocator.find_closest_store_to_customer(customer)
        menu = store.get_menu()

        data = {}
        names = []
        for product in menu.products:
            try:
                for value in menu.variants:
                    if menu.variants[value]['ProductCode'] == product.code:
                        if product.menu_data['ProductType'] == 'Pizza':
                            pizza = menu.variants[value]
                            defaults = (
                                'Handmade Pan',
                                'Hand Tossed',
                                'Thin',
                                'Gluten Free Crust',
                                'Brooklyn',
                                'Crust')
                            name = pizza['Name'].split(')')[1].strip()

                            for f in defaults:
                                name = name.replace(f, "")
                            if name not in names:
                                names.append(name)
                                data[product.menu_data['ProductType']].append({
                                    'Name': name,
                                    'Price': '\n_Small:_ $12.99 _Medium:_ $15.99 _Large:_ $17.99 _x-Large_ $19.99',
                                    'Code': 'WIP',
                                    'Description': product.menu_data['Description'],
                                    'Sizes': [menu.variants[value]]
                                })
                            else:
                                for pizza in data[product.menu_data['ProductType']]:
                                    if pizza['Name'] == name:
                                        pizza['Sizes'].append(menu.variants[value])
                        else:
                            menu.variants[value]['Description'] = product.menu_data['Description']
                            data[product.menu_data['ProductType']].append(menu.variants[value])
            except KeyError:
                for value in menu.variants:
                    if menu.variants[value]['ProductCode'] == product.code:
                        if product.menu_data['ProductType'] == 'Pizza':
                            pizza = menu.variants[value]
                            defaults = ('Handmade Pan', 'Hand Tossed', 'Thin', 'Gluten Free Crust', 'Brooklyn')
                            name = pizza['Name'].split(')')[1]
                            for f in defaults:
                                name = name.replace(f, "")
                            if name not in names:
                                names.append(name)
                                data[product.menu_data['ProductType']] = [{
                                    'Name': name,
                                    'Price': '\n_Small:_ $12.99 _Medium:_ $15.99 _Large:_ $17.99 _x-Large_ $19.99',
                                    'Code': 'WIP',
                                    'Description': product.menu_data['Description'],
                                    'Sizes': [menu.variants[value]]
                                }]
                        else:
                            menu.variants[value]['Description'] = product.menu_data['Description']
                            data[product.menu_data['ProductType']] = [menu.variants[value]]
        categories = []
        for category in data:
            categories.append(category)
        page = 0

        await message.edit(text=ctx.author.mention, embed=discord.Embed(
            title='LOADING....PLEASE WAIT',
            color=0xde2939
        ))
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        await message.add_reaction("🍕")
        await message.add_reaction("🍗")
        await message.add_reaction("🧁")
        await message.add_reaction("🥤")
        await message.add_reaction("✅")
        await message.add_reaction("🗒️")
        await message.add_reaction("❌")

        order = Order(store, customer)
        while True:
            try:
                if page <= 0:
                    page = 0
                    info = store.data
                    embed = discord.Embed(title='Store Info', description=f"_Address:_ {info['AddressDescription']}")
                    embed.add_field(name='Phone Number', value=info['Phone'], inline=False)
                    embed.add_field(name='Hours', value=info['HoursDescription'])
                    wait = info['ServiceMethodEstimatedWaitMinutes']['Delivery']
                    wait_time = f"MIN: {wait['Min']}, MAX: {wait['Max']}"
                    embed.add_field(name='Estimated Wait Time', value=wait_time, inline=False)

                elif page <= len(categories):
                    embed = discord.Embed(
                        title=categories[page - 1],
                        description="""
                            Reply with the item code (the title of each field) to add it to your order
                            or react with ✅ to finish your order
                        """
                    )
                    lists = ""
                    count = 1
                    for info in data[categories[page - 1]]:
                        field = f"**{count}:** {info['Name']}, ${info['Price']}\n{info['Description']}\n\n"
                        count += 1
                        if len(lists) + len(field) > 1024:
                            embed.add_field(name='_ _', value=lists, inline=False)
                            lists = ""
                        else:
                            lists += field
                    if lists:
                        embed.add_field(name='_ _', value=lists)
                else:
                    page = 10
                    embed = discord.Embed(title='CURRENT ORDER')
                    total_cost = 0.00
                    count = 0
                    for item in order.data['Products']:
                        count += 1
                        total_cost += float(item['Price'])
                        embed.add_field(name=f"**{count}:** {item['Name']}", value=item['Price'], inline=False)
                    instructions = """
                                    Reply with the number of the item you'd like to remove.
                                    Or continue browsing the menu to add more items.
                                   """
                    embed.description = f"Total Cost ${total_cost}+{instructions}"
                embed.set_footer(text=f"Page {page + 1} of {len(categories) + 2}")
                await message.edit(embed=embed)

                stuff = await self.message_check(message, ctx.author, 600)

                if not stuff:
                    break
                else:

                    if type(stuff) == type(message):
                        try:
                            await stuff.delete()
                            if page != 10:
                                if page == 6:
                                    pizzas = data[categories[page - 1]][int(stuff.content) - 1]['Sizes']
                                    count = 1
                                    embed = discord.Embed(
                                        title='Size Options',
                                        escription='Reply with the number of the side of your choice')
                                    sizes = ""
                                    for pie in pizzas:
                                        sizes += f"**{count}:** {pie['Name']}, ${pie['Price']}\n"
                                        count += 1
                                    embed.add_field(name='_ _', value=sizes)
                                    options = await ctx.send(embed=embed)

                                    def check(m):
                                        return m.author == ctx.author and m.channel == ctx.channel

                                    reply = (await self.bot.wait_for('message', check=check))
                                    choice = reply.content
                                    await reply.delete()
                                    await options.delete()
                                    stuff.content = reply.content
                                    item = pizzas[int(choice) - 1]

                                else:
                                    item = data[categories[page - 1]][int(stuff.content) - 1]

                                product = await ctx.send(embed=discord.Embed(
                                    title=f" Do you want to add {item['Name']} to your order?",
                                    description=f"**Price:** ${item['Price']}",
                                    color=0xde2939
                                ))

                                def r_check(react, author):
                                    return product.id == react.message.id and author.id == ctx.author.id

                                emoji = await self.reaction(ctx.author, product, ("✅","❌"), 500)
                                await product.delete()
                                if emoji == "✅":
                                    order.add_item(item['Code'])
                                    await ctx.send(embed=discord.Embed(
                                        title=f"Added {item['Name']} to your order.", color=0xde2939),
                                        delete_after=5)
                                else:
                                    await ctx.send('No Item Added', delete_after=5)
                            else:
                                item = order.data['Products'][int(stuff.content)-1]
                                product = await ctx.send(embed=discord.Embed(
                                    title=f" Do you want to remove {item['Name']} from your order?",
                                    description=f"**Price:** ${item['Price']}",
                                    color=0xde2939
                                ))

                                emoji = await self.reaction(ctx.author, product, ("✅","❌"), 500)
                                await product.delete()
                                if emoji == "✅":
                                    order.remove_item(item['Code'])
                                    await ctx.send(embed=discord.Embed(
                                        title=f"Removed {item['Name']} from your order.",color=0xde2939),
                                        delete_after=5)
                                else:
                                    await ctx.send('No Item Removed')
                        except KeyError:
                            await ctx.send('Invalid Item', delete_after=5)
                        except IndexError:
                            await ctx.send('Invalid Item', delete_after=5)
                        except ValueError:
                            await ctx.send('Invalid Item', delete_after=5)

                    else:
                        if stuff[0].emoji == "⬅️":
                            page -= 1
                        elif stuff[0].emoji == "➡️":
                            page += 1
                        elif stuff[0].emoji == "🍕":
                            page = 6
                        elif stuff[0].emoji == "🍗":
                            page = 9
                        elif stuff[0].emoji == "🧁":
                            page = 2
                        elif stuff[0].emoji == "🥤":
                            page = 3
                        elif stuff[0].emoji == '🗒️':
                            page = 10
                        elif stuff[0].emoji == "✅":
                            break
                        elif stuff[0].emoji == "❌":
                            await message.edit(embed=discord.Embed(title='ORDER CREATION CANCELLED',color=0xde2939))
                            return
                        else:
                            print(stuff[0])
                        await stuff[0].remove(stuff[1])

            except TimeoutError:
                await ctx.send("ORDER CREATION TIMED OUT DO d.menu TO RESTART")
                return

        embed = discord.Embed(title='CURRENT ORDER')
        total_cost = 0.00
        count = 0
        for item in order.data['Products']:
            count += 1
            total_cost += float(item['Price'])
            embed.add_field(name=f"**{count}:** {item['Name']}", value=item['Price'], inline=False)
        instructions = """
                 Please Verify Your Order Info. This will be sent to the address supplied in the first step.
                 THIS WILL ORDER A REAL PIZZA TO YOUR ADRESS IF YOU ACCEPT!!!!!
                        """
        embed.description = f"Total Cost ${total_cost}+tax{instructions}"
        await message.delete()
        message = await ctx.send(ctx.author.mention, embed=embed)

        emoji = await self.reaction(ctx.author, message, ("✅", "❌"), 500)

        if emoji == "✅":
            await message.edit(embed=discord.Embed(title='Placing order please wait....',color=0xde2939))
            try:
                data = order.place()
                print(data)
                await message.edit(embed=discord.Embed(title='Your Order Has Been Placed',color=0xde2939))
            except:
                await message.edit(embed=discord.Embed(
                    title='There May Have Been An Error With Placing Your Oder',
                    description="""Please enter your phone number on the tracking site
                                or call the Domino's you ordered from to confirm your order""",
                    color=0xde2939
                ))
        else:
            await message.edit(embed=discord.Embed(title='Order Cancelled!',color=0xde2939))


    async def answer(self, ctx, question, timeout = 0):
        return await asyncio.wait_for(self._answer(ctx, question), timeout = timeout)

    async def _answer(self, ctx, question):
        user = ctx.author
        await user.send(
            embed=discord.Embed(
                title=question))
        while True:
            reply = (await self.bot.wait_for('message'))
            if reply.channel.id == user.dm_channel.id and reply.author.id == user.id:
                return reply.content

    async def reaction(self, author, message, emojis, timeout):
        return await asyncio.wait_for(self._reaction(author, message, emojis), timeout=timeout)

    async def _reaction(self, author, message, emojis):
        for emoji in emojis:
            await message.add_reaction(emoji)
        while True:
            reaction, user = await self.bot.wait_for('reaction_add')
            if reaction.message.id == message.id and user.id == author.id:
                return reaction.emoji

    async def message_check(self, message, user, timeout):
        return await asyncio.wait_for(self._message_check(message, user), timeout=timeout)

    async def _message_check(self, message, user):
        while True:
            done, pending = await asyncio.wait([
                self.bot.wait_for('message'),
                self.bot.wait_for('reaction_add')
            ], return_when=asyncio.FIRST_COMPLETED)
            if not done:
                break
            else:
                stuff = done.pop().result()

                if type(stuff) == type(message):
                    if stuff.channel.id == message.channel.id and stuff.author.id == user.id:
                        return stuff
                else:
                    if stuff[0].message.id == message.id and stuff[1].id == user.id:
                        return stuff


def setup(bot):
    """Imports the cog, this should also be set to the name of the class"""
    bot.add_cog(BotCommands(bot))
