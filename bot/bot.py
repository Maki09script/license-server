import discord
from discord import app_commands
from discord.ext import commands
import requests
import os

# CONFIGURATION
TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
SERVER_URL = "http://127.0.0.1:5001"    # Local server for now
ADMIN_SECRET = "super_secret_admin_key_123"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def get_headers():
    return {"Authorization": f"Bearer {ADMIN_SECRET}", "Content-Type": "application/json"}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} commands')
    except Exception as e:
        print(e)

@bot.tree.command(name="getkey", description="Generate a new license key")
@app_commands.describe(duration="Duration (e.g., 1d, 30d, lifetime)")
async def getkey(interaction: discord.Interaction, duration: str):
    # Determine if user is allowed? For now, allow all or check ID
    # if interaction.user.id != ...: return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        payload = {"duration": duration}
        resp = requests.post(f"{SERVER_URL}/create_key", json=payload, headers=get_headers())
        
        if resp.status_code == 200:
            data = resp.json()
            key = data['key']
            ktype = data['type']
            dur = data['duration']
            
            embed = discord.Embed(title="License Generated", color=discord.Color.green())
            embed.add_field(name="Key", value=f"`{key}`", inline=False)
            embed.add_field(name="Type", value=ktype.capitalize(), inline=True)
            embed.add_field(name="Duration", value=dur, inline=True)
            embed.set_footer(text="One Device Only. Do not share.")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.followup.send(f"Error: {resp.text}", ephemeral=True)
            
    except Exception as e:
        await interaction.followup.send(f"Connection Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="resethwid", description="Reset HWID for a key to allow new device")
@app_commands.describe(key="The license key to reset")
async def resethwid(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    
    try:
        payload = {"key": key}
        resp = requests.post(f"{SERVER_URL}/reset_hwid", json=payload, headers=get_headers())
        
        if resp.status_code == 200:
            await interaction.followup.send(f"✅ HWID successfully reset for key `{key}`.", ephemeral=True)
        elif resp.status_code == 404:
            await interaction.followup.send("❌ Key not found.", ephemeral=True)
        else:
            await interaction.followup.send(f"Error: {resp.text}", ephemeral=True)
            
    except Exception as e:
        await interaction.followup.send(f"Connection Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="delete", description="Permanently delete a license key")
@app_commands.describe(key="The license key to delete")
async def delete(interaction: discord.Interaction, key: str):
    await interaction.response.defer(ephemeral=True)
    
    try:
        payload = {"key": key}
        resp = requests.post(f"{SERVER_URL}/delete_key", json=payload, headers=get_headers())
        
        if resp.status_code == 200:
            await interaction.followup.send(f"🗑️ Key `{key}` has been permanently deleted.", ephemeral=True)
        elif resp.status_code == 404:
            await interaction.followup.send("❌ Key not found.", ephemeral=True)
        else:
            await interaction.followup.send(f"Error: {resp.text}", ephemeral=True)
            
    except Exception as e:
        await interaction.followup.send(f"Connection Error: {str(e)}", ephemeral=True)

if __name__ == '__main__':
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable not set.")
    else:
        bot.run(TOKEN)
