import discord
import time

from discord.ext import commands, tasks
from dotenv import dotenv_values

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup


env = dotenv_values('.env')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

options = webdriver.ChromeOptions()
options.add_argument('--headless')

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

async def jitosol_multiply():
    url = 'https://app.kamino.finance/lending/multiply/H6rHXmXoCQvq8Ue81MqNh7ow5ysPa1dSozwW3PU1dDH6/F9HdecRG8GPs9LEn4S5VfeJVEZVqrDJFR6bvmQTi22na/6gTJfuPHEg6uRAijRkMqNc9kan4sVZejKMxmvx2grT1p'

    try:
        driver.get(url)
        time.sleep(3)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        spans = soup.find_all('span')
        
        result = None
        for span in spans:
            if '$' in span.text:
                result = (float(span.text[1:]), span.text)
                break
                
        return result
        
    finally:
        if driver:
            driver.quit()

@tasks.loop(seconds=600)
async def check_liquidity():
    liquidity, dollars = await jitosol_multiply()

    if liquidity > 0.0:
        await bot.get_channel(int(env['CHANNEL'])).send('JITOSOL Multiply Liquidity Available: ' + str(dollars))


@bot.command()
async def kamino(ctx):
    liquidity, dollars = await jitosol_multiply()
    await bot.get_channel(int(env['CHANNEL'])).send('JITOSOL Multiply Liquidity Available: ' + str(dollars))

@bot.event
async def on_ready():
    print('Bot is ready')
    check_liquidity.start()

bot.run(env['BOT_TOKEN'])