import httpx
from bs4 import BeautifulSoup

URL = "https://kalimatimarket.gov.np/"

def scrap_price():
    html = httpx.get(URL).content
    soup = BeautifulSoup(html, 'html.parser')

    main_div = soup.find('div', id='commodityPricesDailyTable')

    title = main_div.find('h5').text
    headings = main_div.select('table > thead > tr > th')
    headings_list = []

    for heading in headings:
        headings_list.append(heading.text)

    listings_detail_trs = main_div.select("table#commodityDailyPrice > tbody > tr")
    rows_listing = []

    for row in listings_detail_trs:
        columns = [ item.text for item in row.select('td')]
        rows_listing.append(columns)

    print(title, headings_list, rows_listing)

scrap_price()
