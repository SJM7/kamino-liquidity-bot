import discord
import time
import logging
from discord.ext import commands, tasks
from dotenv import dotenv_values
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kamino_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

env = dotenv_values('.env')
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

async def jitosol_multiply():
    url = 'https://app.kamino.finance/lending/multiply/H6rHXmXoCQvq8Ue81MqNh7ow5ysPa1dSozwW3PU1dDH6/F9HdecRG8GPs9LEn4S5VfeJVEZVqrDJFR6bvmQTi22na/6gTJfuPHEg6uRAijRkMqNc9kan4sVZejKMxmvx2grT1p'
    driver = None
    try:
        logger.info("Initializing Chrome WebDriver...")
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 20)
        
        logger.info(f"Attempting to connect to {url}")
        driver.get(url)
        logger.info("Successfully connected to webpage")
        
        time.sleep(3)
        logger.debug("Parsing page content...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        spans = soup.find_all('span')
        result = None
        
        for span in spans:
            if '$' in span.text:
                result = (float(span.text[1:]), span.text)
                logger.info(f"Found liquidity value: {span.text}")
                break
        
        return result
    except Exception as e:
        logger.error(f"Error in jitosol_multiply: {str(e)}")
        return None
    finally:
        if driver:
            logger.debug("Closing WebDriver")
            driver.quit()

@tasks.loop(seconds=600)
async def check_liquidity():
    try:
        result = await jitosol_multiply()
        if result:
            liquidity, dollars = result
            if liquidity >= 1000:
                await bot.get_channel(int(env['CHANNEL'])).send('JITOSOL Multiply Liquidity Available: ' + str(dollars))
            else:
                logger.debug(f"Current liquidity: {dollars}")
        else:
            logger.warning("No liquidity data retrieved")
    except Exception as e:
        logger.error(f"Error in check_liquidity: {str(e)}")

@bot.command()
async def kamino(ctx):
    try:
        logger.info(f"Kamino command received from {ctx.author}")
        result = await jitosol_multiply()
        if result:
            liquidity, dollars = result
            await bot.get_channel(int(env['CHANNEL'])).send('JITOSOL Multiply Liquidity Available: ' + str(dollars))
            logger.info(f"Sent liquidity information: {dollars}")
        else:
            logger.warning("Unable to retrieve liquidity information")
    except Exception as e:
        logger.error(f"Error in kamino command: {str(e)}")

@bot.event
async def on_ready():
    logger.info('Bot is ready')
    check_liquidity.start()
    logger.info('Started check_liqudity')

bot.run(env['BOT_TOKEN'])