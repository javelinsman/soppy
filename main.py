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
from interface_telegram_receiver import InterfaceTelegramReceiver
from interface_telegram_sender import InterfaceTelegramSender
#from module_echo import ModuleEcho
from module_nalida_classic_second import ModuleNalidaClassicSecond


# Basic Settings for Program
FORMAT = '[%(levelname)s][%(asctime)s][%(module)s] %(message)s'
if '--debug' in sys.argv:
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
else:
    logging.basicConfig(format=FORMAT, level=logging.INFO)

# Initialize Bot Components
INTERFACES = {
    "telegram_receiver": InterfaceTelegramReceiver(host=bot_config.host, port=bot_config.port),
    "telegram_sender": InterfaceTelegramSender(),
}
MODULES = {
    #"echo": ModuleEcho(),
    "nalida_classic_second": ModuleNalidaClassicSecond(),
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
