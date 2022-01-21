import platform
import os


def getpath():
    config_path = None

    if platform.system() == "Windows":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\config\\config.ini"
    elif platform.system() == "Linux":
        config_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/config/config.ini"
    return config_path
