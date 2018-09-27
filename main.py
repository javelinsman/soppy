"""
Main module for Nalinyang-Twix.
This module turns on several other components(which is thread),
            enters into command-line mode,
            and gently stop components when it terminates
"""

# Built-in Modules
import sys
import logging

# Custom Modules
import bot_config

# Bot Components
from interfaces.telegram.receiver import InterfaceTelegramReceiver
from interfaces.telegram.sender import InterfaceTelegramSender
from interfaces.timer.timer import Timer

from modules.soppy.module import ModuleSoppy


# Basic Settings for Program
FORMAT = '[%(levelname)s][%(asctime)s][%(pathname)s][%(funcName)s]\n\t%(message)s\n'
if '--debug' in sys.argv:
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
else:
    logging.basicConfig(format=FORMAT, level=logging.INFO)

# Initialize Bot Components
INTERFACES = {
    "telegram_receiver_brand": InterfaceTelegramReceiver(host=bot_config.HOST, port=bot_config.PORT_BRAND, interface_name='brand'),
    "telegram_receiver_brand_friend": InterfaceTelegramReceiver(host=bot_config.HOST, port=bot_config.PORT_BRAND_FRIEND, interface_name='brand_friend'),
    "telegram_receiver_humanlike": InterfaceTelegramReceiver(host=bot_config.HOST, port=bot_config.PORT_HUMANLIKE, interface_name='humanlike'),
    "telegram_receiver_humanlike_friend": InterfaceTelegramReceiver(host=bot_config.HOST, port=bot_config.PORT_HUMANLIKE_FRIEND, interface_name='humanlike_friend'),
    "telegram_receiver_human": InterfaceTelegramReceiver(host=bot_config.HOST, port=bot_config.PORT_HUMAN, interface_name='human'),
    "telegram_receiver_human_friend": InterfaceTelegramReceiver(host=bot_config.HOST, port=bot_config.PORT_HUMAN_FRIEND, interface_name='human_friend'),
    "telegram_sender_brand": InterfaceTelegramSender(bot_config.API_BASE_BRAND, interface_name='brand'),
    "telegram_sender_brand_friend": InterfaceTelegramSender(bot_config.API_BASE_BRAND_FRIEND, interface_name='brand_friend'),
    "telegram_sender_humanlike": InterfaceTelegramSender(bot_config.API_BASE_HUMANLIKE, interface_name='humanlike'),
    "telegram_sender_humanlike_friend": InterfaceTelegramSender(bot_config.API_BASE_HUMANLIKE_FRIEND, interface_name='humanlike_friend'),
    "telegram_sender_human": InterfaceTelegramSender(bot_config.API_BASE_HUMAN, interface_name='human'),
    "telegram_sender_human_friend": InterfaceTelegramSender(bot_config.API_BASE_HUMAN_FRIEND, interface_name='human_friend'),
    "timer": Timer(),
}
MODULES = {
    "soppy": ModuleSoppy(),
}

def start_components():
    "Turn on all interfaces and modules"
    for interface in INTERFACES.values():
        interface.start()
    for module in MODULES.values():
        module.start()

def stop_components():
    "Turn off all interfaces and modules"
    for interface in INTERFACES.values():
        interface.shutdown()
    for module in MODULES.values():
        module.shutdown()

def command_line_mode():
    "command-line mode to operate the bot"
    while True:
        try:
            command = input()
            if command.lower() == 'exit':
                break
        except (KeyboardInterrupt, SystemExit):
            logging.warning('Please enter "exit" to shutdown the program')
    logging.info('Exiting command line mode')

if __name__ == "__main__":
    start_components()
    command_line_mode()
    stop_components()
    logging.info('Program has terminated successfully')
