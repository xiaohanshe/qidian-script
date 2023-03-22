import time
import requests as req
from bs4 import BeautifulSoup

# 常量
DATA_EID = 'data-eid'
DATA_BID = 'data-bid'
PAGE = 'page'
HREF = 'href'

# 发送请求
def senRequest(protocol='http://',url='www.qidian.com'):
    base_url = protocol + url
    headers = {
        'content-type': 'application/json;charset=utf-8',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.37',
    }
    html = req.get(base_url,headers=headers)
    return BeautifulSoup(html.text)


def getMonthlyTicket(soup):
    """
    获取月票榜数据
    :param soup:
    :return:
    """
    print(soup)


def getCoverRecommend(url):
    """
    获取封面推荐图书信息
    :param url: 爬取地点
    :return: None
    """
    soup = senRequest(protocol='http://',url=url)

    pagination_list = soup.select("ul[class='lbf-pagination-item-list'] > li[class='lbf-pagination-item'] > a")
    last_page = pagination_list[len(pagination_list) - 1]
    total_page = int(last_page.getText())
    page_str = 'page'
    for page in range(1,total_page):
        page_url = page_str + str(page)
        request_url = url + page_url
        print("共"+str(total_page)+"页，正在爬取第"+str(page)+"页...",request_url)
        single_page_soup = senRequest(url=request_url)
        getSinglePageCoverRec(single_page_soup)
        # 暂停一秒再请求下一页
        time.sleep(1)
        # 只看第一页，生产时注释掉
        break


def getSinglePageCoverRec(soup):
    """
    解析一页的封面推荐小说
    :param soup: 某一页的 bs4 对象
    :return: None
    """
    li_list = soup.select("ul[class='cf'] > li")
    book_list = []
    for li in li_list:
        # 爬取封面图片
        tag_img = li.select_one("li > div[class='focus-img'] > a > img")
        img_url = tag_img.get('src')
        img_url = img_url.replace("//",'')
        # 爬取图书信息
        tag_date = li.select_one("li > div[class='info'] > span")
        date_time = tag_date.getText()
        tag_a = li.select_one("li > div[class='info']  a")
        book_url = tag_a.get('href')
        book_name = tag_a.getText()
        # 将数据转为元组，方便序列化
        book_info = (date_time,book_url, book_name,img_url)
        book_list.append(book_info)
        print(book_info)
        print(date_time,book_url, book_name,img_url)
        # 测试时，只看第一条，正常生产时可以放开
        break
        # 返回值，需要时打开，这里我只是看一下就不用返回值了
        # return tuple1
    print(book_list)

def getCategory(soup):
    """
    解析分类列表
    :param soup: BeautifulSoup对象
    :return: None
    """
    classify_list = soup.select_one('#classify-list')
    a_list = classify_list.select('a')
    for aa in a_list:
        # url
        url = aa.get('href')
        # 分类id
        category_id = aa.get('data-eid')
        # 名称
        name = aa.get('title')
        # 分类
        category = aa.select_one('i').getText()
        # 阅读量
        read_number = aa.select_one('b').getText()
        print(url,name,category_id,category,read_number)


def getStrongRecommend(strong_recommend_url):
    """
    解析强推页面
    :param strong_recommend_url: 强推页面url
    :return: None
    """
    soup = senRequest(url=strong_recommend_url)
    page_container = soup.select_one("#page-container")
    page_data_pagemax = page_container.get('data-pagemax')
    total_page = int(page_data_pagemax)
    for page in range(1,total_page):
        page_url = PAGE + str(page)
        req_url = strong_recommend_url + page_url
        print("共" + str(total_page) + "页，正在爬取第" + str(page) + "页...", req_url)
        page_soup = senRequest(url=req_url)
        getSinglePageStrongRec(page_soup)
        # 间隔一秒，请求下一页，请求太频繁实在太缺德了
        time.sleep(1)
        break


def getSanjang(sanjang_url):
    """
    解析三江图书的方法。三江页面和往期强推页面基本一致所以用的同一个方法
    :param sanjang_url: 三江页面的url
    :return: None
    """
    getStrongRecommend(sanjang_url)


def getSinglePageStrongRec(soup):
    tag_li_list = soup.select("li[class='strongrec-list book-list-wrap']")
    book_list = []
    for li in tag_li_list:
        # 时间范围
        tag_h3_from = li.select_one("span[class='date-from']")
        date_from = tag_h3_from.getText().strip()
        tag_h3_to = li.select_one("span[class='date-to']")
        date_to = tag_h3_to.getText().strip()
        li_book_list = li.select("div[class='book-list'] li")
        for li_book in li_book_list:
            # 解析栏目信息
            tag_a_channel = li_book.select_one("a[class='channel']")
            channel_data_eid = tag_a_channel.get(DATA_EID)
            channel_url = tag_a_channel.get(HREF).replace('//','')
            channel_name = tag_a_channel.getText()
            # print(channel_data_eid, channel_url, channel_name)
            # 解析图书信息
            tag_a_book = li_book.select_one("a[class='name']")
            book_id = tag_a_book.get(DATA_BID)
            book_url = tag_a_book.get(HREF).replace('//','')
            book_name = tag_a_book.getText()
            # print(book_id, book_url, book_name)
            # 解析作者信息
            tag_a_author = li_book.select_one("a[class='author']")
            if tag_a_author is not None:
                author_data_eid = tag_a_author.get(DATA_EID)
                author_url = tag_a_author.get(HREF).replace('//', '')
                author_name = tag_a_author.getText()
            else:
                tag_a_author = li_book.select_one("span[class='rec']")
                author_name = tag_a_author.getText()
                author_url = ''
                author_data_eid = ''
            # 转为元组，方便序列化
            book_info = (date_from,date_to,channel_data_eid, channel_url, channel_name,book_id, book_url, book_name,author_data_eid, author_url, author_name)
            book_list.append(book_info)
            print(book_info)
        break
    print(book_list)


def analysis():
    """
    解析方法
    :return:
    """
    # 获取封面推荐图书
    cover_recommend_url = "www.qidian.com/book/coverrec/"
    getCoverRecommend(url=cover_recommend_url)
    # 获取强荐图书
    strong_recommend_url  = "www.qidian.com/book/strongrec/"
    getStrongRecommend(strong_recommend_url=strong_recommend_url)
    # 获取三江
    sanjang_url  = "www.qidian.com/book/sanjiang/"
    getSanjang(sanjang_url=sanjang_url)



if __name__ == '__main__':
    analysis()
