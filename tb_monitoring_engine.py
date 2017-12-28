# coding:utf-8
import time
import requests
import re
import json
from lxml import html
from datetime import datetime
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import cookielib
from .monitoring_engine import MonitoringEngine
# from eledata.serializers.watcher import GeneralWatcherSerializer
from logger import logger


class TBMonitoringEngine(MonitoringEngine):
    ORDER_MAPPING = {
        'integrated': '&sort=default',
        'price': '&sort=price-asc',
        'sales': '&sort=sale-desc',
        'hot': '&sort=renqi-desc',
    }
    url_list = []
    url = None
    keyword = None
    img_pth = "img"
    comments_content_list = []
    cookies = None
    sess_t = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_t.mount('http://', adapter)

    sess_s = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    sess_s.mount('http://', adapter)

    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'cache-control': 'no-cache',
        'cookie': 'miid=5121390821926616657; UM_distinctid=15f33ecb52b5d0-0f99ab24b5d44b-102c1709-1fa400-15f33ecb52c649; thw=cn; ctoken=2zhAoFlsixGwSnB9hJHLp4p-render; _m_h5_tk=9ae1b61a1444b9cded3f8e733e100484_1510889165183; _m_h5_tk_enc=b17c8ead85c82f9ebe614e783283be35; cna=rRtuEpySpFMCAdr/aJ7EvQCo; linezing_session=Ok9134CwShTwenheROhkL2nc_1510909439524Z6A3_6; hng=CN%7Czh-CN%7CCNY%7C156; v=0; uc3=sg2=AiA2JmjMFykdNFUat2vZAyoQSt7JJpdq8GiZx8thupk%3D&nk2=3FjtHEK6d4DckBJQ&id2=VynLTZwA1%2FxU&vt3=F8dBzLOUDYoaXS39eNI%3D&lg2=W5iHLLyFOGW7aA%3D%3D; existShop=MTUxMDkxMDU3Mg%3D%3D; uss=U%2BM95J4tZPJaZF%2FiVNQKkMpm10Sf023QWldhrel4mlMpIQ6O2EVNPxyF; lgc=%5Cu5FEB%5Cu4E50%5Cu7684%5Cu8717%5Cu725B%5Cu725B; tracknick=%5Cu5FEB%5Cu4E50%5Cu7684%5Cu8717%5Cu725B%5Cu725B; cookie2=279d2160779191f0eb991d3259a9a19c; sg=%E7%89%9B6c; cookie1=UR46HvyfWSRS1nyDESFJ%2By%2Bo%2BSEizadoFIX%2Bd%2BB415E%3D; unb=452530156; skt=f654d565c603219d; t=500ebec2d5186d3dd6051374b165032b; publishItemObj=Ng%3D%3D; _cc_=URm48syIZQ%3D%3D; tg=0; _l_g_=Ug%3D%3D; _nk_=%5Cu5FEB%5Cu4E50%5Cu7684%5Cu8717%5Cu725B%5Cu725B; cookie17=VynLTZwA1%2FxU; uc1=cookie16=Vq8l%2BKCLySLZMFWHxqs8fwqnEw%3D%3D&cookie21=WqG3DMC9FxUx&cookie15=UIHiLt3xD8xYTw%3D%3D&existShop=true&pas=0&cookie14=UoTde98k0aB5og%3D%3D&tag=8&lng=zh_CN; mt=ci=0_1; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; whl=-1%260%260%261510913050910; _tb_token_=77a56e6e679e; isg=ApiYPZO8dnW6yFkYr9ThCEQ_ac_qKfyqWyhnQdKJxFOGbTlXepBkmlRLy5Mm',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://item.taobao.com/item.htm?spm=a230r.1.14.39.2daa2bf1K4TRXu&id=527314155848&ns=1&abbucket=12',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
    }

    def to_cookielib_cookie(self, selenium_cookie):
        return cookielib.Cookie(
            version=0,
            name=selenium_cookie['name'],
            value=selenium_cookie['value'],
            port='80',
            port_specified=False,
            domain=selenium_cookie['domain'],
            domain_specified=True,
            domain_initial_dot=False,
            path=selenium_cookie['path'],
            path_specified=True,
            secure=selenium_cookie['secure'],
            expires=selenium_cookie['expiry'],
            discard=False,
            comment=None,
            comment_url=None,
            rest=None,
            rfc2109=False
        )

    def get_cookie(self):
        driver = webdriver.Firefox()
        driver.get("https://login.taobao.com/member/login.jhtml")
        time.sleep(5)
        # 用户名 密码
        elem_user = driver.find_element_by_name("TPL_username")
        elem_user.send_keys("kam_m")
        elem_pwd = driver.find_element_by_name("TPL_password")
        elem_pwd.send_keys("53231323A")
        submit_btn = driver.find_element_by_id("J_SubmitStatic")
        submit_btn.send_keys(Keys.ENTER)
        se_cookies = driver.get_cookies()
        cookie_jar = cookielib.CookieJar()
        for cookie in se_cookies:
            cookie_jar.set_cookie(self.to_cookielib_cookie(cookie))
        self.cookies = cookie_jar

    def set_searching_url(self, _keyword, _page_limit, _order):
        logger.info("Setting searching urls for TB Monitoring Engine...")
        _url = 'https://s.taobao.com/search?q=CHANGEME&bcoffset=0&ntoffset=0&s=0'
        self.url = _url.replace('CHANGEME', _keyword)
        self.keyword = _keyword
        if not _order:
            order_url_list = []
            list_url_1 = "https://s.taobao.com/search?" + "q=" + _keyword + "&s=" + str(0)
            page_content = requests.get(list_url_1)
            tree = html.fromstring(page_content.content)
            l_p = tree.xpath('//*[@id="mainsrp-pager"]/div/div/div/div[1]/text()')
            for num in range(0, _page_limit):
                order_url_list.append({"url": "https://s.taobao.com/search?" + "q=" + _keyword + "&s=" + str(num * 44),
                                       "order": "default"})
            self.url_list.append(order_url_list)
        else:
            for order in _order:
                order_url_list = []
                list_url_1 = "https://s.taobao.com/search?" + "q=" + _keyword + "&s=" + str(0) + self.ORDER_MAPPING.get(
                    order)
                page_content = requests.get(list_url_1)
                tree = html.fromstring(page_content.content)
                l_p = tree.xpath('//*[@id="mainsrp-pager"]/div/div/div/div[1]')
                for num in range(0, _page_limit):
                    order_url_list.append({"url": "https://s.taobao.com/search?" + "q=" + _keyword + "&s=" + str(
                        num * 44) + self.ORDER_MAPPING.get(order), "order": order})
                self.url_list.append(order_url_list)
        logger.info("Updated TB Monitoring Engine with {0} urls".format(len(self.url_list)))

    """
    # items_ad = soup_string.find_all('div', {'class': 'item J_MouserOnverReq item-ad '})
    # items_n = soup_string.find_all('div', {'class': 'item J_MouserOnverReq '})
    """

    def get_comments(self, sku_id, comments_page, comment_count, seller_id, plat):
        comments_content_list = []
        real_page = comment_count / 20
        if comments_page > real_page:
            comments_page = real_page
        comments_url_list = []
        if plat == "TB":
            for num in range(1, comments_page + 1):
                comments_url = "https://rate.taobao.com/feedRateList.htm?auctionNumId=" + sku_id + "&currentPageNum=" + str(
                    num) + "&pageSize=20"
                comments_url_list.append(comments_url)
        if plat == "Tmall":
            for num in range(1, comments_page + 1):
                # https://rate.tmall.com/list_detail_rate.htm?itemId=553776512097&sellerId=379092568&order=3&currentPage=1
                comments_url = "https://rate.tmall.com/list_detail_rate.htm?itemId=" + sku_id + "&sellerId=" + seller_id + "&order=3&currentPage=" + str(
                    num)
                comments_url_list.append(comments_url)

        def get_comments_details(url):
            if plat == 'Tmall':
                try:
                    sess = self.sess_t
                    req = sess.get(url)
                    jsondata = req.text[15:]
                    comments_info = json.loads(jsondata)
                    for item in comments_info["rateList"]:
                        comments_content_list.append({
                            "content_title": None,
                            "content_score": None,
                            "content_time": item['rateDate'],
                            "content": item['rateContent']
                        })
                except Exception as e:
                    pass
            if plat == 'TB':
                try:
                    sess = self.sess_t
                    res = sess.get(url, headers=self.headers)
                    comments_info = json.loads(res.text.strip().strip('()'))
                    for item in comments_info['comments']:
                        comments_content_list.append({
                            "content_title": None,
                            "content_score": None,
                            "content": item['content'],
                            'content_time': item['date']
                        })
                except Exception as e:
                    pass

        if comments_url_list:
            s_pool = self.monitoring_thread_pool
            s_pool.map(get_comments_details, comments_url_list)
            # s_pool.close()
            # s_pool.join()

        return comments_content_list

    def get_items(self, _items, counter=5):
        if counter == 0:
            logger.error("5times error")
            return

        def try_get(_items):
            items_get = _items['mods']['itemlist']['data']['auctions']
            return items_get

        try:
            counter -= 1
            result = try_get(_items)
            logger.info("get tb")
            return result
        except Exception as e:
            logger.error(e)
            time.sleep(1)
            return self.get_items(_items, counter)

    def get_basic_info(self, url):
        sess = self.sess
        page_content = sess.get(url["url"])
        current_order = url["order"]
        contents = page_content.content.decode('utf-8')
        regex = 'g_page_config = (.+)'
        items = re.findall(regex, contents)
        items = items.pop().strip()
        items = items[0:-1]
        items = json.loads(items)
        items_get = self.get_items(items)

        rank = 0
        re_list = []
        if items_get:
            for item in items_get:
                # 1.sku_id
                rank = rank + 1

                if 'itemId' in item:
                    sku_id = item['itemId']
                elif 'nid' in item:
                    sku_id = item['nid']
                else:
                    sku_id = u" "

                # 2.product_name
                if 'title' in item:
                    product_name = item['title']
                elif 'raw_title' in item:
                    product_name = item['raw_title']
                else:
                    product_name = u" "

                if "<span class=H>" in product_name:
                    product_name = re.sub('<span class=H>', '', product_name)
                if "</span>" in product_name:
                    product_name = re.sub('</span>', '', product_name)

                # 3.seller_name
                if 'nick' in item:
                    seller_name = item['nick']
                else:
                    seller_name = u" "

                # 4.seller_location
                if 'item_loc' in item:
                    seller_location = item['item_loc']
                else:
                    seller_location = u" "

                # 5.item_url
                if 'detail_url' in item:
                    item_url = item['detail_url']
                else:
                    item_url = " "


                if "https:" not in item_url:
                    item_url = "https:" + item_url

                # print item_url


                # 5.1 check tmall or taobao
                if "detail.tmall.com" in item_url:
                    e_level = "Tmall"
                elif "item.taobao.com" in item_url:
                    e_level = "TB"
                else:
                    e_level = " "
                # 6.price
                if 'salePrice' in item:
                    default_price = item['salePrice']
                elif 'view_price' in item:
                    default_price = item['view_price']
                else:
                    default_price = 0
                # 7.shop_url
                if 'shopLink' in item:
                    seller_url = "http:" + item['shopLink']
                else:
                    seller_url = u" "
                seller_Id = re.search(r'\d+', seller_url).group()
                # 8.pic_url
                if 'pic_url' in item:
                    img_src = [item['pic_url']]
                else:
                    img_src = []
                # 9.sales_count
                if 'view_sales' in item:
                    sales_count = int(re.search(r'\d+', item['view_sales']).group())
                else:
                    sales_count = 0
                # 10.get comment_count
                '''
                   comment_count
                '''
                try:
                    # _call_ad = "https://rate.taobao.com/detailCount.do?itemId=" + sku_id
                    _call_ad = "https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=" + sku_id
                    sess_g = self.sess
                    rep_g = sess_g.get(_call_ad).content
                    comments_count = int(re.search(r"\"rateTotal\":(\d+)", rep_g).group(1))
                    score_avg = float(re.search(r"\"gradeAvg\":(\d+)", rep_g).group(1))
                except Exception as e:
                    logger.error(e)
                    comments_count = 0
                    score_avg = 0
                # 11.get comment_details
                if comments_count > 1:
                    comments_list = self.get_comments(sku_id=sku_id, comments_page=3, comment_count=comments_count,
                                                      seller_id=seller_Id, plat=e_level)
                else:
                    comments_list = [{
                        "content_title": None,
                        "content_score": None,
                        "content": None,
                        "content_time": None
                    }]
                # 12 get stock value
                headers2 = {'Referer': item_url}
                url3 = "https://mdskip.taobao.com/core/initItemDetail.htm?itemId=" + sku_id
                default_model = self.sess_s.get(url3, headers=headers2)
                default_model_string = default_model.content.decode('unicode_escape').encode('utf-8')
                recall_info = json.loads(default_model_string)
                stock_value = recall_info['defaultModel']['inventoryDO']['totalQuantity']

                the_basic_info = {
                    "platform": "TB",
                    'search_keyword': self.keyword,
                    'last_crawling_timestamp': datetime.now(),
                    'seller_location': seller_location,
                    'product_name': product_name,
                    'seller_name': seller_name,
                    'sku_id': sku_id,
                    'comments_ave_score': float(score_avg),
                    'default_price': float(default_price),
                    'final_price': 0,
                    'item_url': item_url,
                    'images': img_src,
                    'sales_count': float(sales_count),
                    'img_pth': self.img_pth,
                    'search_rank': rank,
                    'search_order': current_order,
                    'seller_url': seller_url,
                    'comments_count': comments_count,
                    'comments_list': comments_list
                }
                re_list.append(the_basic_info)
            return re_list
        else:
            logger.error("not get information this time.TAOBAO")
    #
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
    #     logger.info('TB Monitoring Engine Task Completed')
