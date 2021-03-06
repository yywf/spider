# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request, FormRequest
from scrapy.selector import Selector

from zhihu.items import ZhihuItem
from zhihu.items import ZhihuUserItem


class Zhihu1Spider(CrawlSpider):
    name = 'zhihu1'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/people/yywf/followees']

    rules = (
        Rule(SgmlLinkExtractor(allow=('/people/.*/followers',)), callback='parse_followers', follow=True),
        Rule(SgmlLinkExtractor(allow=('/people/.*',), deny=('/people/.*/followers',)), callback='parse_people', follow=True),
    )

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        #"Referer": "https://www.zhihu.com/people/yywf",
        "Connection": "keep-alive",
        #"Cache-Control": "max-age=0",
        #"Upgrade-Insecure-Requests": "1",
        "Content-Type": " application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
        "Referer": "http://www.zhihu.com/"
    }

    def start_requests(self):
        return [Request("http://www.zhihu.com/login/email", meta={'cookiejar': 1}, callback=self.post_login)]

    def post_login(self, response):
        print
        'Preparing login'
        # 下面这句话用于抓取请求网页后返回网页中的_xsrf字段的文字, 用于成功提交表单
        xsrf = Selector(response).xpath('//input[@name="_xsrf"]/@value').extract()[0]
        from_data = {'_xsrf': xsrf, 'email': '740242567@qq.com', 'password': 'hanaidong(9'}
        # FormRequeset.from_response是Scrapy提供的一个函数, 用于post表单
        # 登陆成功后, 会调用after_login回调函数
        return [FormRequest.from_response(response, meta={'cookiejar': response.meta['cookiejar']},
                                          headers=self.headers, formdata=from_data,
                                          callback=self.after_login, dont_filter=True)]

    def after_login(self, response):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse_followers(self, response):
        sel = Selector(response)
        item = ZhihuUserItem()

        username = sel.xpath('//div[@class="top"]/div[@class="title-section"]/a[@class="name"]/@href').extract()[0].encode('utf-8')
        name = sel.xpath('//div[@class="top"]/div[@class="title-section"]/a[@class="name"]/text()').extract()[0].encode('utf-8')
        brief = sel.xpath('//div[@class="top"]/div[@class="title-section"]/div/text()').extract()[0].encode('utf-8')
        url = response.url
        thanks = sel.xpath('//div[@class="zm-profile-header-info-list"]/div[@class="zm-profile-header-user-thanks"]//text()').extract()[0].encode('utf-8')
        agree = sel.xpath('//div[@class="zm-profile-header-info-list"]/div[@class="zm-profile-header-user-agree"]//text()').extract()[0].encode('utf-8')
        sex = sel.xpath('//div[@class="zm-profile-header-user-describe"]//span[@class="item gender"]//i/@class').extract()[0].encode('utf-8')
        image_urls = sel.xpath('//div[@class="zm-profile-header-main"]/img/@src').extract()

        return item

    def parse_followers(self, response):
        return