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

    @commands.command(
        name="example",  # This is the name of the command
        brief="This command returns an example message",  # This is a short description of the command
        aliases=['exam', 'ex']  # These are alternate ways to summon the command
    )
    # This is the minimum for setting up a command, it takes in no arguments and
    # returns whatever you choose with no additional user input
    async def example(self, ctx):
        await ctx.send('Hello There, this is an example command')

    # noinspection PyTypeChecker
    @commands.command(

    )
    async def order(self, ctx):

        message = await ctx.send(ctx.author.mention, embed=discord.Embed(
            title='Please Check Your DMs to supply address and name info'
        ))

        def check(m):
            return ctx.author.id == m.author.id and m.channel == ctx.author.dm_channel
        while True:
            await ctx.author.send(
                embed=discord.Embed(
                    title="What is your first name?"))
            reply = (await self.bot.wait_for('message', check=check))
            f_name = reply.content

            await ctx.author.send(
                embed=discord.Embed(
                    title="What is your last name?"))
            reply = (await self.bot.wait_for('message', check=check))
            l_name = reply.content

            await ctx.author.send(
                embed=discord.Embed(
                    title="What is your email?"))
            reply = (await self.bot.wait_for('message', check=check))
            email = reply.content

            await ctx.author.send(
                embed=discord.Embed(
                    title="What is your phone number?"))
            reply = (await self.bot.wait_for('message', check=check))
            phone = reply.content

            await ctx.author.send(
                embed=discord.Embed(
                    title="What is your street address?"))
            reply = (await self.bot.wait_for('message', check=check))
            street = reply.content

            await ctx.author.send(
                embed=discord.Embed(
                    title="What is your city?"))
            reply = (await self.bot.wait_for('message', check=check))
            city = reply.content

            await ctx.author.send(
                embed=discord.Embed(
                    title="What is your state?"))
            reply = (await self.bot.wait_for('message', check=check))
            state = reply.content

            await ctx.author.send(
                embed=discord.Embed(
                    title="What is your zip code?"))
            reply = (await self.bot.wait_for('message', check=check))
            zip_code = reply.content

            embed = discord.Embed(title='Please resupply your info.')
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

            await confirmation.add_reaction("✅")
            await confirmation.add_reaction("❌")

            reaction, user = await self.bot.wait_for(
                'reaction_add', timeout=45, check=c_check)

            if reaction.emoji == "✅":
                await ctx.author.send(embed=discord.Embed(
                    title='Your all set return to the channel you started this command in to continue your order!'
                ))
                break
            else:
                embed = discord.Embed(title='Please resupply your info.')
                await ctx.author.send(embed=embed)

        await message.edit(embed=discord.Embed(title='LOADING'))

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
            title='LOADING....PLEASE WAIT'
        ))
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        await message.add_reaction("🍕")
        await message.add_reaction("🍗")
        await message.add_reaction("🧁")
        await message.add_reaction("🥤")
        await message.add_reaction("✅")
        await message.add_reaction("🗒️")

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

                done, pending = await asyncio.wait([
                    self.bot.wait_for('message'),
                    self.bot.wait_for('reaction_add')
                ], return_when=asyncio.FIRST_COMPLETED, timeout=1200)
                if not done:
                    break
                else:
                    stuff = done.pop().result()

                    if type(stuff) == type(message):
                        if stuff.channel.id == ctx.channel.id and stuff.author.id == ctx.author.id:
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
                                        description=f"**Price:** ${item['Price']}"
                                    ))
                                    await product.add_reaction("✅")
                                    await product.add_reaction("❌")

                                    def r_check(react, author):
                                        return product.id == react.message.id and author.id == ctx.author.id

                                    reaction, user = await self.bot.wait_for(
                                        'reaction_add', timeout=45, check=r_check)
                                    await product.delete()
                                    if reaction.emoji == "✅":
                                        order.add_item(item['Code'])
                                        await ctx.send(embed=discord.Embed(
                                            title=f"Added {item['Name']} to your order."),
                                            delete_after=5)
                                    else:
                                        await ctx.send('No Item Added', delete_after=5)
                                else:
                                    item = order.data['Products'][int(stuff.content)-1]
                                    product = await ctx.send(embed=discord.Embed(
                                        title=f" Do you want to remove {item['Name']} from your order?",
                                        description=f"**Price:** ${item['Price']}"
                                    ))
                                    await product.add_reaction("✅")
                                    await product.add_reaction("❌")

                                    def r_check(react, author):
                                        return product.id == react.message.id and author.id == ctx.author.id

                                    reaction, user = await self.bot.wait_for(
                                        'reaction_add', timeout=45, check=r_check)
                                    await product.delete()
                                    if reaction.emoji == "✅":
                                        order.remove_item(item['Code'])
                                        await ctx.send(embed=discord.Embed(
                                            title=f"Removed {item['Name']} from your order."),
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
                        if stuff[0].message.id == message.id and stuff[1].id == ctx.author.id:
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
                                await message.edit(embed=discord.Embed(title='ORDER CREATION CANCELLED'))
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
                        """
        embed.description = f"Total Cost ${total_cost}+tax{instructions}"
        await message.delete()
        message = await ctx.send(ctx.author.mention, embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def r_check(react, author):
            return message.id == react.message.id and author.id == ctx.author.id

        reaction, user = await self.bot.wait_for(
            'reaction_add', timeout=45, check=r_check)

        if reaction.emoji == "✅":
            await message.edit(embed=discord.Embed(title='Placing order please wait....'))
            try:
                data = order.place()
                print(data)
                await message.edit(embed=discord.Embed(title='Your Order Has Been Placed'))
            except:
                await message.edit(embed=discord.Embed(
                    title='There May Have Been An Error With Placing Your Oder',
                    description="""Please enter your phone number on the tracking site
                                or call the Domino's you ordered from to confirm your order"""
                ))
        else:
            await message.edit(embed=discord.Embed(title='Order Cancelled!'))

def setup(bot):
    """Imports the cog, this should also be set to the name of the class"""
    bot.add_cog(BotCommands(bot))
