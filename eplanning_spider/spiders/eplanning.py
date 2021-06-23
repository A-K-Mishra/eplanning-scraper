from scrapy import Spider
from scrapy.http.request import Request
from scrapy.http import FormRequest


class EplanningSpider(Spider):
    name = 'eplanning'
    allowed_domains = ['eplanning.ie']
    start_urls = ['http://eplanning.ie/']

    def parse(self, response):
        urls = response.xpath('//a/@href').extract()
        for url in urls :
            if '#' == url:
                pass
            else:
                yield Request(url, callback = self.parse_application)

    def parse_application(self, response):
        app_url = response.xpath('//*[@class="glyphicon glyphicon-inbox btn-lg"]/following-sibling::a/@href').extract_first()

        yield Request(response.urljoin(app_url),callback=self.parse_form)

    def parse_form(self,response):
        yield FormRequest.from_response(
            response,
            formdata={
                'RdoTimeLimit': '7'
            },
            dont_filter=True,
            formxpath='(//form)[2]',
            callback=self.parse_pages
        )

    def parse_pages(self, response):
        application_url = response.xpath('//td/a/@href').extract()
        for url in application_url:
            url = response.urljoin(url)
            yield Request(url , callback = self.parse_items)
        next_page_url = response.xpath('//a[@rel="next"]/@href').extract_first()
        if next_page_url :
            absolute_url = response.urljoin(next_page_url)
            yield Request(absolute_url,callback=self.parse_pages)

    def parse_items(self,response):
        agent_btn = response.xpath('//*[@value ="Agents"]/@style').extract_first()
        if agent_btn and 'visibility: visible' in agent_btn:
            name = response.xpath('//tr[th = "Name :"]/td/text()').extract_first()
            address_first = response.xpath('//tr[th = "Address :"]/td/text()').extract()
            address_second = response.xpath('//tr[th = "Address :"]/following::tr/td/text()').extract()[0:2] 
            address = address_first = address_second 
            phone =  response.xpath('//tr[th = "Phone :"]/td/text()').extract_first()
            fax =  response.xpath('//tr[th = "Fax :"]/td/text()').extract_first()
            email =response.xpath('//tr[th = "e-mail :"]/td/a/text()').extract_first() 
            yield{
                'name':name,
                'address':address,
                'phone':phone,
                'fax':fax,
                'email':email
            }
        else:
            self.logger.info('Agent button not found on page, passing invalid url')

