#!/home/momen/anaconda3/envs/python-zklib/bin/python
from ZK import ZkConnect, ParseConfig, configLogger, getLogFileName
import os
import sys
from pathlib import Path
import logging


def init():
    """
    Initiate the ZK Teco monitoring client.
    """
    try:
        # Load the config
        config_path = Path(os.path.abspath(__file__)).parent / 'config.yaml'
        stream = open(config_path, 'r')

        # Parse config
        config = ParseConfig.parse(stream)

        # Setup logger
        configLogger(config.get('log'))

        # Setup connection
        device = config.get('checkin_device')
        endpoint = config.get('endpoint')
        transmission = config.get(
            'transmission') if 'transmission' in config.keys() else True
        zk = ZkConnect(
            host=device.get('host'),
            port=device.get('port'),
            name=device.get('name'),
            endpoint=endpoint,
            transmission=transmission
        )

        # Start monitoring
        zk.monitor()
    except Exception as error:
        logging.error(error)
        sys.exit(1)


if __name__ == "__main__":
    init()
