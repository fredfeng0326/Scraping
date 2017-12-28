import logging

logging.basicConfig(filename='eledata.log', level=logging.INFO,
                    format='%(asctime)s %(filename)s %(funcName)s()[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S', )
logger = logging.getLogger('')
