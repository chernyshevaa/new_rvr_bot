import logging
from datetime import datetime
from bots import Bot

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename="sample.log")
logger = logging.getLogger("TeleBot")
logger.setLevel(level=logging.INFO)

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename="sample.log")
logger = logging.getLogger("TeleBot")
logger.setLevel(level=logging.INFO)

if __name__ == '__main__':
    bot = Bot(logger)
    bot.start()