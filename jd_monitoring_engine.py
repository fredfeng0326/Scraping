# coding:utf-8
import requests
import re
from lxml import html
from datetime import datetime
import time
# from eledata.serializers.watcher import GeneralWatcherSerializer
from logger import logger
from requests.adapters import HTTPAdapter
import json
from multiprocessing.dummy import Pool as ThreadPool



class JDMonitoringEngine():
    ORDER_MAPPING = {
        'integrated': '&psort=0',
        'price': '&psort=2',
        'sales': '&psort=3',
        'hot': '&psort=4',
    }

    driver = None
    page_limit = 0
    img_pth = 'temp/img'
    locations = []
    url_list = []
    order_list = []
    id_list = []
    limit_current = -1
    limit_total = 0
    keyword = None
    sorder = None
    monitoring_thread_pool = ThreadPool(4)
    sess = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess.mount('http://', adapter)
    is_get_location = False

    SUPPORTED_LOCATIONS = [
        {'id': '1_72_2799_0', 'name': 'bei_jing'},
        {'id': '2_2813_51976_0', 'name': 'shang_hai'},
        {'id': '3_51035_39620_0', 'name': 'tian_jin'},
        {'id': '4_113_9775_0', 'name': 'chong_qing'},
        {'id': '5_142_42540_42668', 'name': 'he_bei'},
        {'id': '6_303_36780_51307', 'name': 'shan_xi'},
        {'id': '7_412_3547_51753', 'name': 'he_nan'},
        {'id': '8_560_567_52113', 'name': 'liao_ning'},
        {'id': '9_639_3172_52217', 'name': 'ji_lin'},
        {'id': '10_727_3334_52324', 'name': 'hei_long_jiang'},
        {'id': '11_799_3240_51319', 'name': 'inner_mongolia'},
        {'id': '12_904_3373_0', 'name': 'jiang_su'},
        {'id': '13_2900_2908_39385', 'name': 'shan_dong'},
        {'id': '14_1151_19227_51648', 'name': 'an_hui'},
        {'id': '15_1158_3412_53564', 'name': 'zhe_jiang'},
        {'id': '16_1303_3483_0', 'name': 'fu_jian'},
        {'id': '17_1432_1435_52285', 'name': 'hu_bei'},
        {'id': '18_1482_3606_0', 'name': 'hu_nan'},
        {'id': '19_1601_3633_0', 'name': 'guang_dong'},
        {'id': '20_1715_43114_51446', 'name': 'guang_xi'},
        {'id': '21_1827_3505_51732', 'name': 'jiang_xi'},
        {'id': '22_1930_50947_52198', 'name': 'si_chuan'},
        {'id': '23_3690_4182_0', 'name': 'hai_nan'},
        {'id': '24_2144_3906_51694', 'name': 'gui_zhou'},
        {'id': '25_2235_2246_52440', 'name': 'yun_nan'},
        {'id': '26_3970_3972_42525', 'name': 'tibet'},
        {'id': '27_2428_31523_51869', 'name': 'shaan_xi'},
        {'id': '28_2525_4001_17664', 'name': 'gan_su'},
        {'id': '29_2580_2581_37708', 'name': 'qing_hai'},
        {'id': '30_2628_2629_52516', 'name': 'ning_xia'},
        {'id': '31_4110_4122_52526', 'name': 'zin_jiang'}
    ]

    sess_l = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_l.mount('http://', adapter)

    def set_cookie(self, _key_1, _key_2):
        pass

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

    def set_searching_url(self, _keyword, _page_limit, _order):
        logger.info("Setting searching urls for JD Monitoring Engine...")
        self.keyword = _keyword

        if not _order:
            order_url_list = []
            list_url_1 = 'https://search.jd.com/Search?keyword=' + _keyword + '&enc=utf-8&page=' + str(
                1) + "&psort=0" + "&scrolling=y"
            page_content = requests.get(list_url_1)
            tree = html.fromstring(page_content.content)
            try:
                l_p = int(tree.xpath('//*[@id="J_topPage"]/span/i/text()')[0])
            except:
                l_p = 1
            if _page_limit * 2 > l_p:
                _page_limit = l_p
            for num in range(1, _page_limit * 2 + 1, 1):
                list_url = 'https://search.jd.com/Search?keyword=' + _keyword + '&enc=utf-8&page=' + str(
                    num) + '&psort=1' + "&scrolling=y"
                order_url_list.append({"url": list_url, "order": "default"})
            self.url_list.append(order_url_list)
        else:
            for order in _order:
                order_url_list = []
                list_url_1 = 'https://search.jd.com/Search?keyword=' + _keyword + '&enc=utf-8&page=' + str(
                    1) + self.ORDER_MAPPING.get(order) + "&scrolling=y"

                page_content = requests.get(list_url_1)
                tree = html.fromstring(page_content.content)
                try:
                    l_p = int(tree.xpath('//*[@id="J_topPage"]/span/i/text()')[0])
                except:
                    l_p = 1
                if _page_limit * 2 > l_p:
                    _page_limit = l_p
                for num in range(1, _page_limit * 2 + 1, 1):
                    list_url = 'https://search.jd.com/Search?keyword=' + _keyword + '&enc=utf-8&page=' + str(
                        num) + self.ORDER_MAPPING.get(order) + "&scrolling=y"
                    order_url_list.append({"url": list_url, "order": order})
                self.url_list.append(order_url_list)
        logger.info("Updated JD Monitoring Engine with {0} urls".format(len(self.url_list)))
        print (self.url_list)

    def check_page(self, url):
        s = re.findall('page=(\d+)', url)
        t = int(s[0])
        return t % 2 == 0

    def get_comments(self, sku_id, comments_page, comment_count):
        # check if the request page bigger than real page,if yes, the request page = real page
        real_page = comment_count / 10
        if comments_page > real_page:
            comments_page = real_page
        # 2.get page details.\
        comments_url_list = []
        for num in range(0, comments_page):
            comments_url = "https://sclub.jd.com/comment/productPageComments.action?productId=" + sku_id + "&score=0&sortType=5&page=" + str(
                num) + "&pageSize=10"
            comments_url_list.append(comments_url)
        url_1 = "https://sclub.jd.com/comment/productPageComments.action?productId=" + sku_id + "&score=0&sortType=5&page=" + str(
            1) + "&pageSize=10"
        comments_info_1 = self.auto_recovered_fetch_json(url_1)
        score_avg = comments_info_1['productCommentSummary']['averageScore']
        comments_content_list = []

        def get_comments_details(url):
            comments_info = self.auto_recovered_fetch_json(url)
            for comment_item in comments_info['comments']:
                content = comment_item.get('content')
                content_time = comment_item.get('creationTime')
                content_score = comment_item.get('score')
                comments_content_list.append({
                    "content_title": None,
                    "content": content,
                    "content_time": content_time,
                    "content_score": content_score
                })

        s_pool = self.monitoring_thread_pool
        s_pool.map(get_comments_details, comments_url_list)
        # s_pool.close()
        # s_pool.join()
        return score_avg, comments_content_list

    def get_basic_info(self, url_dict):
        logger.info("Execution: JD Monitoring")
        order = url_dict["order"]
        page_content = requests.get(url_dict["url"])
        tree = html.fromstring(page_content.content)
        goods_list = tree.xpath('//*[@id="J_goodsList"]/ul/li')
        re_list = []
        rank = 0

        if self.check_page(url_dict["url"]):
            rank = 30
        logger.info("Detected {0} products".format(len(goods_list)))
        for goods in goods_list:
            # 0. rank
            rank = rank + 1
            # 1._http
            _http = goods.xpath('div/div[contains(@class,"p-img")]/a/@href')
            # logger.debug("_http: {0}".format(_http))
            if _http:
                _http = "http:" + _http[0]
            else:
                continue
            # 2.data_pid = sku_id
            _data_pid = re.findall('jd.com/(.*?).html', _http)[0] if _http != "not get" else None
            # logger.debug("_data_pid: {0}".format(_data_pid))
            try:
                # 3.img_path
                img_item = goods.xpath('div/div[contains(@class,"p-img")]/a/img/@src')
                if not img_item:
                    img_item = goods.xpath('div/div[contains(@class,"p-img")]/a/img/@data-lazy-img')
                img = ["http:" + img_item[0]]

                # 4.price that list show

                final_price_item1 = goods.xpath('div/div[contains(@class,"p-price")]/strong/i/text()')
                final_price_item2 = goods.xpath('div/div[contains(@class,"p-price")]/strong/@data-price')
                price_list = final_price_item1 + final_price_item2
                final_price = next(item for item in price_list if item is not None)

                # final_price = goods.xpath('div/div[2]/strong/@data-price')[0]
                # logger.debug("final_price: {0}".format(final_price))

                # 5.product_name
                product_name_list = goods.xpath('div/div[contains(@class,"p-name")]/a/em/text()')
                product_name = ''.join(product_name_list)

                # logger.debug("product_name: {0}".format(product_name))

                # 6.comment_count
                comment_count = goods.xpath('div/div[contains(@class,"p-commit")]/strong/a/text()')[0]
                comment_count = self.comment_quantity_change(comment_count)

                # logger.debug("comment_count: {0}".format(comment_count))

                # 7.8.seller name and seller url
                try:
                    seller_name = goods.xpath('div/div[contains(@class, "p-shop")]/span/a/@title')[0]
                    seller_url = "http:" + goods.xpath('div/div[contains(@class, "p-shop")]/span/a/@href')[0]
                except:
                    seller_name = u"JD"
                    seller_url = "http://www.jd.com"
                # print "jd", seller_name

                # logger.debug("seller_name: {0}".format(seller_name))
                # logger.debug("seller_url: {0}".format(seller_url))
                self.id_list.append(_data_pid)
                # 9.comments details
                if comment_count > 0:
                    score_avg, comment_list = self.get_comments(sku_id=_data_pid, comments_page=5,
                                                                comment_count=comment_count)
                else:
                    score_avg = 0
                    comment_list = []

                # 10.locations and stock value
                # Use Class Parameter to control enable or not. default disabled
                location_list = self.get_location_stocks(sku_id=_data_pid) if self.is_get_location else []

                the_basic_info = {
                    'search_keyword': self.keyword,
                    'last_crawling_timestamp': datetime.now(),
                    'platform': 'JD',
                    'product_name': product_name,
                    'seller_name': seller_name,
                    'sku_id': _data_pid,
                    'default_price': float(final_price),
                    'final_price': 0,
                    'item_url': _http,
                    'comments_ave_score': float(score_avg),
                    'comments_count': comment_count,
                    'images': img,
                    'current_stock': location_list,
                    'search_rank': rank,
                    'search_order': order,
                    'seller_url': seller_url,
                    'comments_list': comment_list
                }
                re_list.append(the_basic_info)
            except:
                logger.warning("item: pid({0}) is missed".format(_data_pid))
        logger.info("Returned {0} products".format(len(re_list)))
        self.print(re_list)
        return re_list

    # def out(self, _list):
    #     serializer = GeneralWatcherSerializer(data=_list, many=True)
    #     if serializer.is_valid():
    #         _data = serializer.create(serializer.validated_data)
    #         for data in _data:
    #             data.group = self.group
    #             data.save()
    #     else:
    #         # TODO: report errors
    #         logger.error(serializer.errors)
    #     logger.info('JD Monitoring Engine Task Completed')

    def print(self,_list):
        #             'search_keyword': self.keyword,
        #             'last_crawling_timestamp': datetime.now(),
        #             'platform': 'JD',
        #             'product_name': product_name,
        #             'seller_name': seller_name,
        #             'sku_id': _data_pid,
        #             'default_price': float(final_price),
        #             'final_price': 0,
        #             'item_url': _http,
        #             'comments_ave_score': float(score_avg),
        #             'comments_count': comment_count,
        #             'images': img,
        #             'current_stock': location_list,
        #             'search_rank': rank,
        #             'search_order': order,
        #             'seller_url': seller_url,
        #             'comments_list': comment_list
        for item in _list:
            print("Product_name", item["product_name"])
            print("last_crawling_timestamp", item["last_crawling_timestamp"])
            print("seller_name", item["seller_name"])
            print("sku_id", item["sku_id"])
            print("default_price", item["default_price"])
            print("item_url", item["item_url"])
            print("comments_count", item["comments_count"])
            print("comments_ave_score", item["comments_ave_score"])
            print("images", item["images"])
            print("search_rank", item["search_rank"])
            print("seller_url", item["seller_url"])
            print("comments_list", item["comments_list"])

    """
    JD Utils Functions
    """

    @staticmethod
    def comment_quantity_change(before_quantity):
        """
        Converting 1万 or 1.0万 to 10000.
        :param before_quantity:
        :return:
        """
        before_quantity = before_quantity.replace("+", "")
        if u'万' in before_quantity:
            if '.' in before_quantity:
                before_quantity = before_quantity.replace(".", "")
                before_quantity = before_quantity.replace(u'万', "000")
            else:
                before_quantity = before_quantity.replace(u'万', "0000")
        return int(before_quantity)

    def get_location_stocks(self, sku_id):
        result = []
        for location in self.SUPPORTED_LOCATIONS:
            url = "https://c0.3.cn/stocks?type=getstocks&skuIds=" + sku_id + "&area=" + location['id']
            stock_json = self.auto_recovered_fetch_json(url)
            location_stock_json_value = stock_json.values()
            if location_stock_json_value:
                location_value = location_stock_json_value[0]
                # Stock State Code. 40: 可發貨; 33: 有貨, 34: 無貨
                stock_state_code = location_value["StockState"]
                if stock_state_code == 40:
                    stock_state = 'shippable'
                elif stock_state_code == 33:
                    stock_state = 'in_stock'
                else:
                    # elif stock_state_code == 34:
                    stock_state = 'out_of_stock'

                stock_location = location["name"]
                location_j = {
                    "stock_state": stock_state,
                    "stock_location": stock_location
                }
                result.append(location_j)
        return result


if __name__ == "__main__":
    j = JDMonitoringEngine()
    j.set_searching_url(_keyword="dell", _page_limit=1, _order=["sales"])
    url_list = j.url_list
    for _index, url_dict in enumerate(url_list):
        logger.info("Sending {0}/{1} url dict to basic info extraction".format(
            (_index + 1), len(url_list)))
        results = list(map(lambda x: j.get_basic_info(x), url_dict))
        # results = s_pool.map(self.get_basic_info, url_dict)
        # for response in results:
        #     # print(response)
