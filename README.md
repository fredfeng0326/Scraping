# Scraping
电子商务爬虫分析（test阶段）
==== 
1.简单说明
-------

 京东，淘宝，苏宁，亚马逊中国 抓取数据，存储到database 并进行分析
 
2.抓取的DIC
-------

```Python
 the_basic_info = {
                    'search_keyword': self.keyword,  "使用的keyword"
                    'last_crawling_timestamp': datetime.now(),    "当前抓取时间"
                    'platform': 'JD',   "抓取平台"
                    'product_name': product_name,    "产品名称"
                    'seller_name': seller_name,   "商家名称"
                    'sku_id': _data_pid,    "产品Id"
                    'default_price': float(final_price),   "最终价格"
                    'final_price': 0,
                    'item_url': _http,  "商品网页地址"
                    'comments_ave_score': float(score_avg),    "商品评分"
                    'comments_count': comment_count,    "商品评论数量"
                    'images': img,    "商品图片地址"
                    'current_stock': location_list,   "商品存储地址"
                    'search_rank': rank,    "在当前搜索索引下的排名"
                    'search_order': order,   "当前索引（按销量，价格，热度等）"
                    'seller_url': seller_url,   "商家网页地址"
                    'comments_list': comment_list    "具体评论，支持抓取100条评论"
                }
```

一个例子：  
-------
Product_name  戴尔灵越游匣15PR-6748B 15.6英寸游戏笔记本电脑(i7-7700HQ 8G 128GSSD+1T GTX1050 4G独显 IPS)黑 <br/>
last_crawling_timestamp 2017-12-28 20:20:09.684290 <br/>
seller_name 戴尔京东自营旗舰店 <br/>
sku_id 4824733 <br/>
default_price 6599.0 <br/>
item_url http://item.jd.com/4824733.html <br/>
comments_count 72000 <br/>
comments_ave_score 5.0 <br/>
images ['http://img13.360buyimg.com/n7/jfs/t12472/179/736139380/319777/f266f597/5a128bf6N079a87ba.jpg'] <br/>
search_rank 1 <br/>
seller_url http://mall.jd.com/index-1000000140.html  <br/>
comments_list [{'content_score': 5, 'content_time': '2017-12-05 18:54:31', 'content_title': None, 'content': '用了将近一个月了，说说体验如何。11月9号凌晨买的，当天下午就到了。包装精简，京东袋子里就是戴尔的盒子。电脑颜值高，A面类肤质，后面散热口非常帅。电脑不轻薄，因为做工的好的原因有点厚重，不过这样才有点游戏本的意思。宿舍里还有台暗影精灵2pro和R720，相比2pro键盘敲打起来挺有弹性，但是背光没有其他两台亮。个人感觉键盘触感最好的还是R720，而且按键大一些。说说R720和2PRO跟游匣无法比拟的，那就是低音炮，音质非常好，三个室友都夸赞羡慕游匣的音质。所以我的电脑也成了我们宿舍的音响。。。屏幕呢是ips45色域的。对于以前一直用的是TN屏的我感觉这电脑屏幕相当好了。再说说性能，其实性能是最不用说的，配置都摆在那里，鲁大师跑分将近一万八，1050ti能够应付大多数大型单机游戏了，吃鸡中画质可以流畅运行。运行大型游戏时风扇会全力运作，声音稍微有点响（散热好和噪音小不可兼得），我更注重散热所以风扇声大点无所谓，听着还挺带劲的。固态(不是nvme协议)和机械硬盘都比较差，开机十秒左右。总结下吧。优点:1.颜值高2.散热好3.做工精良4.配置低音炮缺点:1.低端ips屏2.略厚重3.硬盘差'}]  <br/>

3.测试？
-------
```Python
if __name__ == "__main__":
    j = JDMonitoringEngine()
    j.set_searching_url(_keyword="dell", _page_limit=1, _order=["sales"])
    url_list = j.url_list
    for _index, url_dict in enumerate(url_list):
        logger.info("Sending {0}/{1} url dict to basic info extraction".format(
            (_index + 1), len(url_list)))
        results = list(map(lambda x: j.get_basic_info(x), url_dict))
```

将jd_monitoring_engine main 方法里面的_keyword,_page_limit,_order <br/>
改成你想测试的例子。三个参数分别是关键字,搜索页数和搜索索引


                
