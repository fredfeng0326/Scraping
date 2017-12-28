# coding:utf-8
from base_engine import BaseEngine
import os
import requests
from abc import abstractmethod
import json
# from eledata.util import EngineExecutingError
import time
import uuid
from multiprocessing.dummy import Pool as ThreadPool
from requests.adapters import HTTPAdapter
from .logger import logger


class MonitoringEngine(BaseEngine):
    """
    Environment Setting Functions
    """

    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess.mount('http://', adapter)

    def __init__(self, event_id, group, params, keyword=None, location=None, _u_key='CHANGE_ME', _p_key='CHANGE_ME',
                 _page_limit=None, order=None, is_get_location=False):
        # TODO: get keywords, locations from params
        # TODO: get page, order from params??
        # if not keyword:
        #     keyword = get_keyword_from_group_param
        logger.info("init with {0}".format(str(event_id)))
        super(MonitoringEngine, self).__init__(event_id, group, params)
        self.driver = None
        self.page_limit = 0
        self.img_pth = 'temp/img'
        self.locations = []
        self.url_list = []
        self.order_list = []
        self.id_list = []
        self.limit_current = -1
        self.limit_total = 0
        self.keyword = keyword
        self.page_limit = _page_limit
        self.set_location(location)
        self.order = order
        self.set_cookie(_u_key, _p_key)
        self.set_searching_url(self.keyword, self.page_limit, self.order)
        self.is_get_location = is_get_location

        # Setting instance based Thread Pool...
        # TODO: Use global queue
        self.monitoring_thread_pool = ThreadPool(4)

        # Setting instance based HTTP Manager...
        self.sess = requests.Session()
        self.adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.sess.mount('http://', self.adapter)

    def set_keyword(self):
        keyword_param = filter(lambda _x: _x.label == "keywords", self.params)[0]
        if not keyword_param.choice_input:
            pass
        self.keyword = keyword_param.choice_input.split(",")
        return

    def set_page_limit(self):
        leaving_param = filter(lambda _x: _x.label == "page_limit", self.params)[0]
        user_input = leaving_param.choice_input \
            if leaving_param.choice_index is 1 else 3  # by default 3 pages
        self.page_limit = user_input
        return

    def set_location(self):
        location_param = filter(lambda _x: _x.label == "location_limit", self.params)[0]
        user_input = location_param.choice_input \
            if location_param.choice_index is 1 else 20  # by default 3 pages
        self.locations = self.supported_locations[:user_input]
        pass

    def set_order(self):
        # TODO: update to sync order param
        location_param = filter(lambda _x: _x.label == "location_limit", self.params)[0]
        user_input = location_param.choice_input \
            if location_param.choice_index is 1 else 20  # by default 3 pages
        self.locations = self.supported_locations[:user_input]
        pass

    @abstractmethod
    def set_location(self, _location):
        """
        update self.location from _location (and self.supported_locations,for engines with location dependency)
        """

    @abstractmethod
    def set_cookie(self, _key_1, _key_2):
        """
        update self.cookie based on _key_1, _key_2 on selenium (for engines with login dependency most likely)
        """

    @abstractmethod
    def set_searching_url(self, _keyword, _page, _order):
        """
        Update self.url from _keyword, for all sub-engines.
        :param _keyword: string, Searching keywords from params.
        :param _page: int, Number of page to be monitored.
        :param _order: string, Type of product ordering to be monitored.
        :return: list of string, Contains the url(s) to be monitored.
        """

    """
    Monitoring Core Functions
    """

    def execute(self):
        """
        Core Function.
        :return:
        """
        # try:
        # s_pool = self.monitoring_thread_pool
        for _index, url_dict in enumerate(self.url_list):
            logger.info("Sending {0}/{1} url dict to basic info extraction".format(
                (_index + 1), len(self.url_list)))
            results = list(map(lambda x: self.get_basic_info(x), url_dict))
            # results = s_pool.map(self.get_basic_info, url_dict)
            for response in results:
                self.out(response)
        # s_pool.close()
        # s_pool.join()
        # except Exception, e:
        #     logger.error("Execution Error: {0}".format(e.message))
        #     raise EngineExecutingError(e.message)

    def event_init(self):
        """
        There is no event to be reported by low level monitoring engines.
        :return: None
        """
        return

    @abstractmethod
    def get_basic_info(self, url_dict):
        """
        Extract product information from soup_string
        :param url_dict: Dict, {url, order, page}.
        :return: [{...item_information},]
        """
        return

    @abstractmethod
    def out(self, data):
        """
        Save product information
        :param data: list, List of product information object.
        :return:
        """
        return

    """
    Monitoring Utils Functions
    """

    def auto_recovered_fetch_json(self, _url, _http_header=None):
        """
        :param _url: string,
        :param _http_header:　
        :return:
        """
        _info = None
        count = 5
        while count >= 0:
            try:
                sess = self.sess
                resp = sess.get(_url, headers=_http_header)
                resp.encoding = 'gbk'
                _info = json.loads(resp.text)
                break
            except ValueError:
                time.sleep(5)
                count -= 1
                continue
        return _info

    def auto_recovered_fetch_json_callback(self, _url, _http_header=None):
        """
        Separated as another auto fetcher, avoiding multiple condition checking
        :param _url: string,
        :param _http_header:
        :return:
        """
        _info = None
        count = 5
        while count >= 0:
            try:
                sess = self.sess
                resp = sess.get(_url, headers=_http_header)
                # Encoding with bk below destroyed the json string structure.
                # resp.encoding = 'gbk'
                _info = json.loads(resp.text.split("(")[1].strip(");"))
                break
            except ValueError as e:
                time.sleep(5)
                count -= 1
                continue
        return _info

    @staticmethod
    def save_image(_url, _save_path):
        _filename = str(uuid.uuid4())
        if not os.path.exists(_save_path):
            os.makedirs(_save_path)
        img_data = requests.get(_url).content
        path = _save_path + "/" + _filename + '.jpg'
        with open(path, 'wb') as handler:
            handler.write(img_data)
        return path
