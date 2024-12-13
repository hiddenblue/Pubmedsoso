# -*- coding: utf-8 -*-
import asyncio
import os
import platform
from typing import Optional, List

from lxml import etree

from utils.DataType import ArticleFreeType, SingleSearchData
from utils.LogHelper import print_error
from utils.WebHelper import WebHelper
from utils import DBHelper
from config import projConfig


def parseSearchHtml(html: str) -> Optional[List[SingleSearchData]]:
    """
    Parses the HTML content of a search page and extracts relevant information about articles.
    
    Args:
        html (str): The HTML content of the search page.
        
    Returns:
        Optional[List[SingleSearchData]]: A list of SingleSearchData objects containing parsed data.
                                         Returns None if parsing fails.
    """
    if os.getenv("LOCAL_DEBUG"):
        parser = etree.HTMLParser()
        html_etree = etree.parse("./searchresult.html", parser)
    else:
        html_etree = etree.HTML(html)

    AllSearchElem = html_etree.xpath("(//div[@class='docsum-content'])")
    print(len(AllSearchElem))
    ret = []

    try:
        for index, singleSearchElem in enumerate(AllSearchElem):
            print(index + 1)

            # 1. Document Title
            xpath_expression = './/a[@class="docsum-title"]/text() | .//a[@class="docsum-title"]//b/text()'
            doctitleElem = singleSearchElem.xpath(xpath_expression)
            doctitle = "".join([item.strip() for item in doctitleElem if item.strip()])
            print("doctitle: ", doctitle)

            # 2. Short Author
            short_author = singleSearchElem.xpath(".//span[@class='docsum-authors short-authors']/text()")
            short_author = short_author[0] if short_author else ""
            print("short_author: ", short_author)

            # 3. Full Author
            full_author = singleSearchElem.xpath(".//span[@class='docsum-authors full-authors']/text()")
            full_author = full_author[0] if full_author else ""
            print("full_author: ", full_author)

            # 4. Short Journal
            short_journal_elem = singleSearchElem.xpath(
                ".//span[@class='docsum-journal-citation short-journal-citation']/text()"
            )
            short_journal = short_journal_elem[0] if short_journal_elem else ""

            # 5. Full Journal
            full_journal = singleSearchElem.xpath(
                ".//span[@class='docsum-journal-citation full-journal-citation']/text()"
            )
            full_journal = full_journal[0] if full_journal else ""
            print("short_journal: ", short_journal)
            print("full_journal: ", full_journal)

            # 6. PMID
            PMID = singleSearchElem.xpath(".//span[@class='docsum-pmid']/text()")
            PMID = PMID[0] if PMID else ""
            print("PMID: ", PMID)

            # 7. Free Mark
            freePMCMarkElem = singleSearchElem.xpath(
                ".//span[@class='free-resources spaced-citation-item citation-part']/text()"
            )
            if not freePMCMarkElem:
                FreeMark = ArticleFreeType.NoneFreeArticle
            elif "Free PMC article" in freePMCMarkElem[0]:
                FreeMark = ArticleFreeType.FreePMCArticle
            elif "Free article" in freePMCMarkElem[0]:
                FreeMark = ArticleFreeType.FreeArticle
            else:
                FreeMark = ArticleFreeType.NoneFreeArticle
            print("FreeMark: ", FreeMark)

            # 8. Review Mark
            reviewMark = singleSearchElem.xpath(
                ".//span[@class='publication-type spaced-citation-item citation-part']/text()"
            )
            reviewMark = bool(reviewMark)
            print("reviewMark: ", reviewMark)

            ret.append(SingleSearchData(
                doctitle=doctitle,
                short_journal=short_journal,
                full_journal=full_journal,
                short_author=short_author,
                full_author=full_author,
                PMID=PMID,
                freemark=FreeMark,
                reviewmark=reviewMark
            ))
        print("当前data数据长度%d\n" % len(ret))
        return ret
    except Exception as e:
        print_error("遍历搜索页信息失败: %s\n" % e)
        return []


def SaveSearchData(datalist: List[SingleSearchData], dbpath: str) -> None:
    """
    Saves the list of SingleSearchData objects to an SQLite database.

    Args:
        datalist (List[SingleSearchData]): List of parsed search data.
        dbpath (str): Path to the SQLite database.
    """
    tablename = f'pubmed{projConfig.savetime}'
    for singleSearchData in datalist:
        try:
            sql = f"""
            INSERT INTO {tablename} (
                doctitle, full_author, short_author, full_journal, short_journal, PMID, freemark, reviewmark
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            writeparam = (
                singleSearchData.doctitle,
                singleSearchData.full_author,
                singleSearchData.short_author,
                singleSearchData.full_journal,
                singleSearchData.short_journal,
                singleSearchData.PMID,
                singleSearchData.freemark.value,
                singleSearchData.reviewmark
            )
            DBHelper.DBWriter(dbpath, sql, writeparam)
        except Exception as e:
            print_error("当前项目写入失败: %s\n" % e)
            continue


def spiderpub(parameter: str, page_limit: int, resultNum: int) -> None:
    """
    Main function to scrape PubMed search results.

    Args:
        parameter (str): Search parameters.
        page_limit (int): Maximum number of pages to scrape.
        resultNum (int): Total number of search results.
    """
    datalist = []
    param_list = []
    pagemax = (resultNum + 49) // 50

    print(f"准备获取搜索页面信息第1-{min(page_limit, pagemax)}页")

    # 一次性构建好所有的搜索url参数
    for i in range(1, min(page_limit + 1, pagemax)):
        temp_param = parameter + "&page=" + str(i)
        param_list.append(temp_param)

    try:
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        html_list = asyncio.run(WebHelper.getSearchHtmlAsync(param_list))

    except Exception as e:
        print_error("spiderpub函数出错，请检查结果\n")
        raise

    for html in html_list:
        if html is None:
            print("部分检索页面出错")
            continue
        else:
            SingleSearchPageData = parseSearchHtml(html)
            if SingleSearchPageData is not None:
                datalist.extend(SingleSearchPageData)

    dbpath = 'pubmedsql'
    tablename = f'pubmed{projConfig.savetime}'
    txtname = f"pubmed{projConfig.savetime}.txt"

    try:
        DBHelper.DBCreater(dbpath)
        DBHelper.DBTableCreater(dbpath, tablename)
        SaveSearchData(datalist, dbpath)
    except Exception as e:
        print_error("将搜索信息存储到sqlite3数据库： %s的表: %s 时发生错误: %s" % (dbpath, tablename, e))

    try:
        with open(txtname, "w", encoding='utf-8') as file:
            for singleSearchData in datalist:
                output = singleSearchData.to_string() + '\n'
                file.write(output)
        print("搜索信息导入到txt当中成功")
    except Exception as e:
        print_error("导出到txt时发生错误: ", e)
