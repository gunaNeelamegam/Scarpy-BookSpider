import scrapy


class MySpider(scrapy.Spider):
    name = "bookspider"
    start_urls = ["http://books.toscrape.com/"]

    def parse(self, response, **kwrags):
        # page_link = response.css(" article.product_pod div.image_container a::attr(href)").get()
        # page_link = response.css(".image_container a::attr(href)").get()
        if next_url := response.css("ul.pager li.next a::attr('href')").get(default=""):
            if next_url:
                self.log(f'{"#"*20} {next_url=} {"#"*20}')
                yield from response.follow_all(css=".image_container a", callback=self.parse_books)
                yield response.follow(next_url, self.parse)

    def parse_books(self, response):
        table_content = response.css("table tr")
        table_data = dict()
        for table_row in table_content:
            table_data[f"{table_row.css('th::text').get().strip()}"] = table_row.css(
                'td::text').get().strip()

        def parse_stock():
            digit = ""
            for word in response.css("div.product_main p.instock").get().strip().split(" "):
                for _ in word:
                    if _.isdigit():
                        digit = digit+_
            return int(digit)
        yield {
            "url": response.url,
            "image_url": response.css("div.item img::attr('src')").get(default="").strip(),
            "book_name": response.css(".product_main h1::text").get(default="").strip(),
            "price": response.css(".product_main .price_color::text").get(default="").strip(),
            "book_description": response.xpath('//*[@id="content_inner"]/article/p/text()').get(),
            "instock": parse_stock(),
            "ratings": response.css(".product_main p.star-rating::attr(class)").get(),
            ** table_data
        }
