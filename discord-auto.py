from imports import *  # Imports custom module from file inside of the folder that imports needed imports

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.presences = True
intents.message_content = True

TOKEN = 'REDACTED'  # < Discord Bot Token 

SERVER_ID = REDACTED  # Replace REDACTED with actual server ID
CHANNEL_ID = REDACTED  # Replace REDACTED with actual channel ID
CLIENT_ID = REDACTED  # Replace REDACTED with actual client ID

bot = commands.Bot(command_prefix='.', intents=intents)

randcolor = discord.Color(random.randint(0x000000, 0xFFFFFF))


@bot.command()
async def ping(ctx):
    """Ping command to check bot latency."""
    embed = discord.Embed(title=f":ping_pong: Pong! {round(bot.latency * 1000)}ms", color=randcolor)
    await ctx.message.delete()  # Delete user's message
    await ctx.send(embed=embed)


@bot.command()
async def whois(ctx, *, user: discord.Member = None):
    """Command to display user information."""
    if user is None:
        user = ctx.author

    date_format = "%a, %d %b %Y %I:%M %p"
    embed = discord.Embed(description=user.mention, title='ID: ' + str(user.id), color=randcolor)
    embed.set_author(name=str(user))
    embed.add_field(name="Joined", value=user.joined_at.strftime(date_format))
    members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
    embed.add_field(name="Join position", value=str(members.index(user) + 1))
    embed.add_field(name="Registered", value=user.created_at.strftime(date_format))
    if len(user.roles) > 1:
        role_string = ' '.join([r.mention for r in user.roles][1:])
        embed.add_field(name="Roles [{}]".format(len(user.roles) - 1), value=role_string, inline=False)
    perm_string = ', '.join([str(p[0]).replace("_", " ").title() for p in user.guild_permissions if p[1]])
    embed.add_field(name="Guild permissions", value=perm_string, inline=False)
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)  # Set a 5 second cooldown for each command per user
async def botinfo(ctx):
    """Displays information about the bot."""
    embed = discord.Embed(
        title="Bot Information",
        description="Detailed information about the bot",
        color=randcolor,
        timestamp=discord.utils.utcnow()  # Replace NOW with discord.utils.utcnow()
    )

    current_process = psutil.Process(os.getpid())
    cpu_usage = current_process.cpu_percent(interval=1) / current_process.num_threads()

    mem = psutil.virtual_memory()
    memory_usage = current_process.memory_info().rss

    # Bytes to megabytes
    memory_usage_mb = memory_usage / (2 ** 20)
    total_memory_mb = mem.total / (2 ** 20)

    discord_py_version = discord.__version__
    python_version = platform.python_version()
    system = platform.system()

    latency_ms = bot.latency * 1000

    uptime_seconds = (discord.utils.utcnow() - bot.user.created_at).total_seconds()
    uptime_str = discord.utils.format_dt(bot.user.created_at, style='R')

    embed.add_field(name='Owner', value='`Replays`', inline=True)  # Replace 'Replays' with actual owner name
    embed.add_field(name='Developer', value='`Replays`', inline=True)  # Replace 'Replays' with actual developer name
    embed.add_field(name='CPU Usage', value='`{0:.2f}%`'.format(cpu_usage), inline=True)
    embed.add_field(name="RAM Usage", value='`{:.2f}/{:.2f} MB`'.format(memory_usage_mb, total_memory_mb), inline=True)
    embed.add_field(name='Platform', value='`{}`'.format(system), inline=True)
    embed.add_field(name='Discord.py Version', value='`{}`'.format(discord_py_version), inline=True)
    embed.add_field(name='Python Version', value='`{}`'.format(python_version), inline=True)
    embed.add_field(name='API Latency', value='`{:.0f} ms`'.format(latency_ms), inline=True)
    embed.add_field(name='Uptime', value='`{}`'.format(uptime_str), inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)


@bot.command()
async def restart(ctx):
    """Command to restart the bot (restricted to authorized user)."""
    if ctx.author.id == CLIENT_ID:  # Check if the user is authorized
        await ctx.send("Restarting Bot...")

        subprocess.Popen([sys.executable, "discord-auto.py"])
        await bot.close()

    else:
        await ctx.send("You are not authorized to use this command.")


def update_upgrade():
    """Function to update and upgrade the Raspberry Pi system."""
    subprocess.run(['sudo', 'apt-get', 'update'])
    subprocess.run(['sudo', 'apt-get', 'upgrade', '-y'])


def get_ip_address():
    """Function to retrieve the Raspberry Pi's IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(('10.255.255.255', 1))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = 'Unable to determine IP Address'
    finally:
        s.close()
    return ip_address


async def send_embed_update():
    """Async function to send system update information to Discord."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        update_upgrade()
        ip_address = get_ip_address()

        embed = discord.Embed(title="Raspberry Pi System Update", color=randcolor)
        embed.add_field(name="Update Status", value="System Updated and Upgraded Successfully.", inline=False)
        embed.add_field(name="Current IP Address", value=ip_address, inline=False)
        embed.add_field(name="Date: ", value=discord.utils.utcnow())

        server = bot.get_guild(SERVER_ID)
        channel = server.get_channel(CHANNEL_ID)

        await channel.send(embed=embed)

        await asyncio.sleep(43200)  # Run every 12 hours


@bot.event
async def on_error(event, *args, **kwargs):
    """Error handling event."""
    import traceback
    traceback.print_exc()


@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    print(f'{bot.user.name} has connected to Discord Successfully!')
    bot.loop.create_task(send_embed_update())

bot.run(TOKEN)
