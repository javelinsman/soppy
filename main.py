# Built-in Modules
import sys
import logging

# Custom Modules
import bot_config

# Bot Components
from interface_telegram_receiver import InterfaceTelegramReceiver
from interface_telegram_sender import InterfaceTelegramSender
from module_echo import ModuleEcho

# Basic Settings for Program
FORMAT = '[%(levelname)s][%(asctime)s][%(module)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)

# Initialize Bot Components
interfaces = {
    "telegram_receiver": InterfaceTelegramReceiver(host=bot_config.host, port=bot_config.port),
    "telegram_sender": InterfaceTelegramSender(),
}
modules = {
    "echo": ModuleEcho(),
}
for interface in interfaces.values():
    interface.start()
for module in modules.values():
    module.start()

# Enter into Command-line Mode
while True:
    try:
        command = input()
        if command.lower() == 'exit':
            raise
    except (KeyboardInterrupt, SystemExit):
        logging.warning('Please enter "exit" to shutdown the program')
    except:
        logging.info('Program will terminate after shutting down all components')
        for interface in interfaces.values():
            interface.shutdown()
        for module in modules.values():
            module.shutdown()
        break
logging.info('Program has terminated successfully')
