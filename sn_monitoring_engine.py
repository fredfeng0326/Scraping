# coding:utf-8

import json
import requests
from datetime import datetime
from requests.adapters import HTTPAdapter
import urllib
from lxml import html
from .monitoring_engine import MonitoringEngine
# from eledata.serializers.watcher import GeneralWatcherSerializer
from logger import logger


class SNMonitoringEngine(MonitoringEngine):
    # order
    # 0: 综合
    # 8: 销量
    # 6: 评价数
    # 10: 价格
    ORDER_MAPPING = {
        'integrated': '0',
        'price': '10',
        'sales': '8',
        'hot': '6'
    }

    SUPPORTED_LOCATIONS = [
        {'id': '010_0100101_1', 'name': 'bei_jing'},
        {'id': '021_0210101_1', 'name': 'shang_hai'},
        {'id': '022_0220101_1', 'name': 'tian_jin'},
        {'id': '023_0230101_1', 'name': 'chong_qing'},
        {'id': '025_0250101_1', 'name': 'he_bei'},
        {'id': '020_0200101_1', 'name': 'shan_xi'},
        {'id': '531_5310101_1', 'name': 'he_nan'},
        {'id': '571_5710101_1', 'name': 'liao_ning'},
        {'id': '028_0280101_1', 'name': 'ji_lin'},
        {'id': '311_3110101_1', 'name': 'hei_long_jiang'},
        {'id': '027_0270101_1', 'name': 'inner_mongolia'},
        {'id': '591_5910101_1', 'name': 'jiang_su'},
        {'id': '024_0240101_1', 'name': 'shan_dong'},
        {'id': '371_3710101_1', 'name': 'an_hui'},
        {'id': '551_5510101_1', 'name': 'zhe_jiang'},
        {'id': '731_7310101_1', 'name': 'fu_jian'},
        {'id': '029_0290101_1', 'name': 'hu_bei'},
        {'id': '771_7710101_1', 'name': 'hu_nan'},
        {'id': '791_7910101_1', 'name': 'guang_dong'},
        {'id': '351_3510101_1', 'name': 'guang_xi'},
        {'id': '451_4510101_1', 'name': 'jiang_xi'},
        {'id': '431_4310101_1', 'name': 'si_chuan'},
        {'id': '851_8510101_1', 'name': 'hai_nan'},
        {'id': '871_8710101_1', 'name': 'gui_zhou'},
        {'id': '991_9910101_1', 'name': 'yun_nan'},
        {'id': '931_9310101_1', 'name': 'tibet'},
        {'id': '471_4710101_1', 'name': 'shaan_xi'},
        {'id': '898_8980101_1', 'name': 'gan_su'},
        {'id': '951_9510101_1', 'name': 'qing_hai'},
        {'id': '971_9710101_1', 'name': 'ning_xia'},
        {'id': '089_0890101_1', 'name': 'zin_jiang'}
    ]

    # 1.
    sess_re = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_re.mount('http://', adapter)

    sess_t = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_t.mount('http://', adapter)

    sess_c = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_c.mount('http://', adapter)
    keyword = None
    url = None
    img_pth = None
    url_list = []

    def set_searching_url(self, _keyword, _page_limit, _order):
        logger.info("Setting searching urls for SN Monitoring Engine...")
        self.keyword = _keyword

        if not _order:
            order_url_list = []
            for num in range(0, _page_limit, 1):
                if num == 0:
                    list_url = "http://search.suning.com/" + urllib.quote(_keyword.encode('utf8')) + "/"
                    order_url_list.append({"url": list_url, "order": "default"})
                else:
                    list_url = "http://search.suning.com/" + urllib.quote(_keyword.encode('utf8')) + "/&cp=" + str(num)
                    order_url_list.append({"url": list_url, "order": "default"})
            self.url_list.append(order_url_list)
        else:
            for order in _order:
                order_url_list = []
                for num in range(0, _page_limit, 1):
                    if num == 0:
                        list_url = "http://search.suning.com/" + urllib.quote(
                            _keyword.encode('utf8')) + "/" + "&st=" + str(self.ORDER_MAPPING.get(order))
                        order_url_list.append({"url": list_url, "order": order})
                    else:
                        list_url = "http://search.suning.com/" + urllib.quote(_keyword.encode('utf8')) + "/&cp=" + str(
                            num) + "&st=" + str(self.ORDER_MAPPING.get(order))
                        order_url_list.append({"url": list_url, "order": order})
                self.url_list.append(order_url_list)
        logger.info("Updated SN Monitoring Engine with {0} urls".format(len(self.url_list)))

    def get_basic_info(self, url):
        order = url["order"]
        this_url = url["url"]
        async_content = self.sess_t.get(this_url).content
        # print async_content
        tree = html.fromstring(async_content)
        goodslist = tree.xpath('//*[@id="filter-results"]/ul/li')
        rank = 0
        relist = []
        for goods in goodslist:
            rank = rank + 1
            product_name_list = goods.xpath('div/div/div/div[2]/p[2]/a/text()')
            product_name = ''.join(product_name_list)
            # print "SN",product_name
            seller_name_item = goods.xpath('div/div/div/div[2]/p[4]/a/text()')
            if seller_name_item:
                seller_name = seller_name_item[0]
            else:
                seller_name = "None"
            _url_item = goods.xpath('div/div/div/div[2]/p[2]/a/@href')
            if _url_item:
                _url = "http:" + _url_item[0]
                _url_split = _url.split('/')
                vendor_id = _url_split[3]
                _data_pid = _url_split[4].split('.')[0]
            else:
                continue
            img_url_item = goods.xpath('div/div/div/div[1]/div/a/img/@src2')
            if img_url_item:
                img_url = "http:" + img_url_item[0]
            else:
                img_url = "None"
            seller_url_item = goods.xpath('div/div/div/div[2]/p[4]/a/@href')
            if seller_url_item:
                seller_url = "http:" + seller_url_item[0]
            else:
                seller_url = "None"
            # print seller_url
            price_url = 'http://ds.suning.cn/ds/generalForTile/' + _data_pid + '__2_' + vendor_id + '-020-2-' + vendor_id + '-1--.jsonp'
            try:
                price_response = self.sess_re.get(price_url).content
                price_json = price_response[1:-2]
                rs_object = json.loads(price_json)['rs'][0]
                # logger.info("Converting Price: {0}".format(rs_object['price']))
                default_price = float(rs_object['price'])
            except Exception as e:
                logger.warning("Caught Exception: {0} when reading price of {1}".format(e.message, _data_pid))
                default_price = 0
            if default_price == "":
                default_price = 0
            # print "price",default_price,price_url

            # coments_count and score_count:
            try:
                comments_count_url = "https://review.suning.com/ajax/review_satisfy/general-000000000" + _data_pid + \
                                     "-" + vendor_id + "-----.htm?"
                # comments_count_url = "https://product.suning.com/"+vendor_id+"/"+_data_pid+".html"
                comments_count_item = self.sess_c.get(comments_count_url).content[1:-1]
                comments_count_info = json.loads(comments_count_item)
                scoreAve = float(comments_count_info["reviewCounts"][0]["qualityStar"])
                comments_count = float(comments_count_info["reviewCounts"][0]["totalCount"])

            except:
                scoreAve = 0
                comments_count = 0

            # comments
            comment_list = []
            try:
                comments_url = "https://review.suning.com/ajax/review_lists/general-000000000" + _data_pid + \
                               "-" + vendor_id + "-total-1-default-10-----.htm"
                comments_item = self.sess_t.get(comments_url).content[1:-1]
                comments_info = json.loads(comments_item)
                comment_source_list = comments_info["commodityReviews"]
                if comment_source_list:
                    for item in comment_source_list:
                        comment_list.append({
                            "content": item["content"],
                            "content_title": None,
                            "content_score": item["qualityStar"],
                            "content_time": item["publishTime"]
                        })
            except:
                comment_list = []

            # Use Class Parameter to control enable or not. default disabled
            location_list = self.get_location_stocks(_data_pid, vendor_id) if self.is_get_location else []

            the_basic_info = {
                'search_keyword': self.keyword,
                'last_crawling_timestamp': datetime.now(),
                'platform': 'SN',
                'product_name': product_name,
                'seller_name': seller_name,
                'sku_id': _data_pid,
                'default_price': default_price,
                'final_price': 0,
                'item_url': _url,
                'comments_count': comments_count,
                'images': [img_url],
                'current_stock': location_list,
                'support': [],
                'comments_ave_score': scoreAve,
                'advertisements': "",
                'bundle': [],
                'model': {},
                'detail': [],
                'search_rank': rank,
                'search_order': order,
                'seller_url': seller_url,
                'comments_list': comment_list
            }
            relist.append(the_basic_info)
        return relist

    # def out(self, _list):
    #     serializer = GeneralWatcherSerializer(data=_list, many=True)
    #     if serializer.is_valid():
    #         _data = serializer.create(serializer.validated_data)
    #         for data in _data:
    #             data.group = self.group
    #             data.save()
    #     else:
    #         # TODO: report errors
    #         print(serializer.errors)
    #     logger.info('SN Monitoring Engine Task Completed')

    def get_location_stocks(self, sku_id, vendor_id):
        result = []
        for location in self.SUPPORTED_LOCATIONS:
            url = "https://icps.suning.com/icps-web/getAllPriceFourPage/" \
                  "000000000{0}_{1}_{2}_pc_showSaleStatus.vhtm".format(sku_id, vendor_id, location['id'])
            stock_json = self.auto_recovered_fetch_json_callback(url)
            if stock_json:
                location_value = stock_json[u'saleInfo'][0][u'invStatus']
                if location_value == 1:
                    stock_state = 'shippable'
                else:
                    stock_state = 'out_of_stock'
                stock_location = location['name']
                result.append({'stock_state': stock_state, 'stock_location': stock_location})
        return result
