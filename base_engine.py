"""
This is the mother class for engine executing executing questions in EleData.

@params:
- group:
    Model Object of user group, corresponding for retrieving the entity data and the destination for the output(event).

And all executing engine should experience the same life-cycle:

Initializing Engine
- engine.init()
"""

from multiprocessing import Process
from abc import abstractmethod


class BaseEngine(object):
    group = None
    response = None
    params = None

    def __init__(self, event_id, group, params):
        self.event_id = event_id
        self.group = group
        self.params = params

    @abstractmethod
    def execute(self):
        """
        void function to update intermediate/ ultimate response
        """


    @abstractmethod
    def event_init(self):
        """
        (When engine is for Event Response)
        void function to update
        """

    def get_processed(self):
        """
        (When engine is not for Event Response)
        Return engine response in series way
        :return: engine ultimate response
        """
        return self.response
