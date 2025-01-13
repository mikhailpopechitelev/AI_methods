from master import Master
from logger import Logger
from config.general import Config, configExample
from pathlib import Path

import time



def main() -> None:
    configPath = Path("config.json")
        
    if configPath.exists():
        config = Config.fromFile(path=configPath)
        config.save(configPath)
        
        logger = Logger(config=config.logging)
        logger.info(f"Load config from file: {configPath.absolute()}")
    
    else:
        logger = Logger(config=config.logging)
        logger.warning(f'Config file "{configPath}" not found, try use default.')
        config.save(configPath)

    
    with Master(config=config, logger=logger) as master:  
        master.join()

if __name__ == "__main__":
    main()
        
        