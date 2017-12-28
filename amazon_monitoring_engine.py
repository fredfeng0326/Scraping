# coding:utf-8
import requests
from lxml import html
from .monitoring_engine import MonitoringEngine
from datetime import datetime
# from eledata.serializers.watcher import GeneralWatcherSerializer
from requests.adapters import HTTPAdapter
import re
import time
from logger import logger


class AmazonmonitoringEngine(MonitoringEngine):
    # sort by
    # relevanceblender: 相关度
    # price-asc-rank: 价格由低到高
    # price-desc-rank: 价格由高到低
    # review-rank: 用户评分
    # date-desc-rank: 上架时间
    ORDER_MAPPING = {
        'integrated': 'relevanceblender',
        'price': 'price-asc-rank',
        # 'sales_desc': 'price-desc-rank',
        'sales': 'review-rank',
        'hot': 'rank'
    }
    headers = {
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,fr;q=0.4,zh-TW;q=0.2',
    }
    keyword = None
    url = None
    img_pth = None
    url_list = []
    sess_am = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_am.mount('http://', adapter)
    sess_in = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_in.mount('http://', adapter)
    sess_com = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_com.mount('http://', adapter)

    def set_searching_url(self, _keyword, _page_limit, _order):
        logger.info("Setting searching urls for AZ Monitoring Engine...")
        if not _order:
            order_url_list = []
            for num in range(1, _page_limit + 1, 1):
                # list_url = 'https://www.amazon.cn/s/ref=sr_pg_' + str(num) + '?' + urllib.urlencode(query_params)
                list_url = 'https://www.amazon.cn/s/ref=sr_pg_' + str(num) + '?' + '&page=' + str(
                    num) + 'keywords=' + _keyword
                order_url_list.append({"url": list_url, "order": "default"})
            self.url_list.append(order_url_list)
        else:
            for order in _order:
                order_url_list = []
                for num in range(1, _page_limit + 1, 1):
                    # list_url = 'https://www.amazon.cn/s/ref=sr_pg_' + str(num) + '?' + urllib.urlencode(query_params)
                    list_url = 'https://www.amazon.cn/s/ref=sr_pg_' + str(num) + '?' + '&page=' + str(
                        num) + '&sort=' + self.ORDER_MAPPING.get(order) + '&keywords=' + _keyword
                    order_url_list.append({"url": list_url, "order": order})
                self.url_list.append(order_url_list)
        logger.info("Updated AZ Monitoring Engine with {0} urls".format(len(self.url_list)))

    def get_basic_info(self, url):
        this_url = url["url"]
        order = url["order"]
        relist = []

        def retry(count=5):
            _product_list = None
            for i in range(count):
                page_content = self.sess_am.get(this_url, headers=self.headers)
                root = html.fromstring(page_content.content)
                _product_list = root.xpath('//li[contains(@class, "s-result-item")]')
                if _product_list:
                    break
                else:
                    logger.warning("cannot get amazon item, retrying:({0}/5)".format(i + 1))
                    time.sleep(5)
                    continue
            return _product_list

        product_list = retry(count=5)
        if product_list:
            logger.info("Extracted Amazon Item, count: {0}".format(len(product_list)))
        else:
            # TODO: serious error, have to report continuous monitoring engine
            logger.warning("Cannot extract amazon item, response website: {0}".format(this_url.encode('utf-8')))

        rank = 0
        for product in product_list:
            # exclude advertisements
            rank = rank + 1
            if bool(product.xpath('.//*[contains(@class, "s-sponsored-header")]')):
                continue

            # image path
            img_image = product.xpath('.//img[contains(@class, "s-access-image")]')[0]
            image_path = img_image.xpath('@src')[0]

            # product name
            product_name = product.xpath('.//a[contains(@class, "s-access-detail-page")]/@title')[0]
            # print product_name

            # price
            try:
                price = product.xpath('.//span[contains(@class, "s-price")]/text()')[0]
                price = int(re.search(r'\d+', price).group())
            except Exception:
                price = "0"

            # whether 海外购
            is_buying_abroad = bool(product.xpath('.//i[contains(@class, "s-icon-ags-large-badge")]'))
            comments_count = product.xpath('.//a[contains(@href, "customerReviews")]/text()')
            if comments_count:
                comments_count = comments_count[0]
            else:
                comments_count = 0

            # product inner page link
            inner_page_url = str(product.xpath('.//a[contains(@class, "s-access-detail-page")]/@href')[0])

            # whether has comments
            has_comments = bool(product.xpath('.//span[contains(@class, "a-declarative")]'))
            if has_comments:
                # comments count

                if is_buying_abroad:
                    inner_page_content = self.sess_in.get(inner_page_url, headers=self.headers)
                    inner_page_root = html.fromstring(inner_page_content.content)

                    comment_source_list = inner_page_root.xpath('.//div[@data-hook="cmps-review"]')
                    comment_list = []
                    for comment in comment_source_list:
                        content = comment.xpath('.//div[contains(@class, "a-expander-content")]/text()')[0]
                        comment_list.append({
                            "content": content
                        })
                    score_avg = 0

                else:
                    # comment page url
                    page = '1'
                    comment_page_url = inner_page_url[0:inner_page_url.rindex('/ref=')].replace(
                        '/dp/', '/product-reviews/'
                    ) + '/ref=cm_cr_getr_d_paging_btm_' + page + '?showViewpoints=1&pageNumber=' + page

                    comment_page_content = self.sess_com.get(comment_page_url, headers=self.headers)
                    comment_page_root = html.fromstring(comment_page_content.content)

                    comment_source_list = comment_page_root.xpath('.//div[@data-hook="review"]')
                    score_avg_item = comment_page_root.xpath(
                        '//*[@id="cm_cr-product_info"]/div/div[1]/div[3]/span/a/span/text()')

                    comment_list = []
                    total_score = 0
                    index = 0
                    for comment in comment_source_list:
                        content_score = comment.xpath('.//i[@data-hook="review-star-rating"]/span/text()')[0][0]
                        content_title = comment.xpath('.//a[contains(@class, "review-title")]/text()')[0]
                        content = comment.xpath('.//span[contains(@class, "review-text")]/text()')[0]
                        total_score = total_score + int(content_score)
                        index = index + 1
                        comment_list.append({
                            "content_time": None,
                            "content_score": content_score,
                            "content_title": content_title,
                            "content": content
                        })
                    if index != 0:
                        score_avg_by_mannu = total_score / float(index)
                    else:
                        score_avg_by_mannu = 0

                    if score_avg_item:
                        score_avg_list = score_avg_item[0]
                        score_avg = score_avg_list.split()[0]
                    else:
                        score_avg = score_avg_by_mannu
            else:
                score_avg = 0
                # Using Empty List instead of list with empty object
                # List with empty object make confusion on data handling
                comment_list = []

            the_basic_info = {
                'search_keyword': self.keyword,
                'last_crawling_timestamp': datetime.now(),
                'platform': 'AMAZON',
                'product_name': product_name,
                'seller_name': "Amazon.cn",
                'sku_id': inner_page_url.split('/')[4],
                'default_price': float(price),
                'final_price': 0,
                'item_url': inner_page_url,
                'comments_count': comments_count,
                'images': [image_path],
                'current_stock': [],
                'support': [],
                'advertisements': "",
                'comments_ave_score': float(score_avg),
                'bundle': [],
                'model': {},
                'detail': [],
                'search_rank': rank,
                'search_order': order,
                'seller_url': "https://www.amazon.cn/",
                'comment_source_list': comment_list
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
    #     logger.info('AMAZON Monitoring Engine Task Completed')
