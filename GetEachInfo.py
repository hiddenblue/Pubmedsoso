# -*- coding: utf-8 -*-
import asyncio
import os
import re
import time
from typing import List

import requests
from lxml import etree

from config import projConfig
from utils.DBHelper import DBSaveInfo, DBFetchAllPMID
from utils.DataType import ABS_PartEnumType, SingleDocInfo, Abstract
from utils.ExcelHelper import ExcelHelper
from utils.LogHelper import medLog
from utils.WebHelper import WebHelper

# adjust the BATCH_SIZE in config.py
# the default info batch size is 50
BATCH_SIZE = projConfig.InfoBatchSize


def parse_abstract(
        abstract_chunk: List[etree.Element],
        part_name: ABS_PartEnumType,
) -> str:
    """
    从摘要块中提取指定部分的内容

    :param abstract_chunk: 摘要的HTML块
    :param part_name: 要提取的部分名称
    :return: 提取的内容
    """
    ret = ""
    for chunk in abstract_chunk:
        sub_title_elements = chunk.xpath(".//strong[@class='sub-title']")
        for sub_title in sub_title_elements:
            if sub_title.text and part_name.value in sub_title.text:
                text_elements = chunk.xpath(".//text()")
                text = " ".join([item.strip() for item in text_elements if item.strip()])
                ret = re.sub(r'\s{2,}', ' ', text)
                break
    return ret


def get_single_info(session, PMID: str) -> SingleDocInfo:
    try:
        html = WebHelper.GetHtml(session, PMID)
    except Exception as e:
        medLog.error(f"请求失败: {e}")
        return SingleDocInfo()

    if os.getenv("LOCAL_DEBUG"):
        parser = etree.HTMLParser()
        html_etree = etree.parse("./Pubmed2.html", parser)
    else:
        html_etree = etree.HTML(html)
    return parse_single_info(html_etree)


def parse_single_info(html_etree: etree.Element):
    PMID_elem = html_etree.xpath(".//*[@id='full-view-identifiers']//strong[@class='current-id']/text()")
    if len(PMID_elem) != 0:
        PMID = PMID_elem[0]
    else:
        PMID = None
    medLog.debug("PMID: %s" % PMID)

    # 提取PMCID和DOI
    PMCID_elem = html_etree.xpath(".//span[@class='identifier pmc']//a[@class='id-link']/text()")
    if len(PMCID_elem) != 0:
        PMCID = [pmcid.strip() for pmcid in PMCID_elem if "PMC" in pmcid][0]
    else:
        PMCID = ""
    medLog.debug("PMCID %s" % PMCID)

    doi = ""
    DOI_elem = html_etree.xpath(
        ".//ul[@id='full-view-identifiers']//span[@class='identifier doi']/a[@class='id-link']/text()")
    if len(DOI_elem) != 0:
        doi = DOI_elem[0].strip()
    medLog.debug("DOI %s" % doi)

    # Affiliation  type list[str]
    Affiliation = []

    affi_elem = html_etree.xpath("//div[@class='expanded-authors']")
    if len(affi_elem) == 0:
        Affiliation = []
    else:
        # 有两组重复的附属单位，我们取第一组就行了
        affi_elem = affi_elem[0]
        medLog.debug("affi_elem: %s" % affi_elem)
        affi_list = affi_elem.xpath(".//li[@data-affiliation-id]/text()")
        medLog.debug("affi_emem: %s" % affi_list)

        for i in range(len(affi_list)):
            # 利用正则去掉多余的空格
            temp_affitem = re.sub(r'\s{2,}', '', str(affi_list[i]).strip()).strip()
            Affiliation.append(str(i + 1) + "." + temp_affitem)
        medLog.debug("Affiliation %s " % Affiliation)

    # fulltext link
    # not including the pmc link
    # //*[@id="article-page"]/aside/div/div[1]/div[1]/div/a
    # 我们假设只有一个有效的full text link 多了暂时不管
    full_text_link: str = ""
    full_text_elem = html_etree.xpath(".//div[@class='full-text-links']//div[@class='full-text-links-list']/a/@href")
    if len(full_text_elem) != 0:
        full_text_link = full_text_elem[0]
    medLog.debug("full_text_link: %s " % full_text_link)

    # 提取摘要各部分
    abstract_chunk = html_etree.xpath(
        "//body/div[@id='article-page']/main[@id='article-details']/div[@id='abstract']//p"
    )
    background = parse_abstract(abstract_chunk, ABS_PartEnumType.Background)
    methods = parse_abstract(abstract_chunk, ABS_PartEnumType.Methods)
    results = parse_abstract(abstract_chunk, ABS_PartEnumType.Results)
    conclusions = parse_abstract(abstract_chunk, ABS_PartEnumType.Conclusions)
    registration = parse_abstract(abstract_chunk, ABS_PartEnumType.Registration)
    keywords = parse_abstract(abstract_chunk, ABS_PartEnumType.Keywords)

    # 一种特殊情况，只有abstract文字
    abstract_text = html_etree.xpath(".//div[@id='eng-abstract']/p/text()")
    if len(abstract_text) != 0:
        abstract_text = re.sub(r'\s{2,}', ' ', abstract_text[0]).strip()

    # 创建Abstract实例
    abstract_obj = Abstract(
        background=background,
        methods=methods,
        results=results,
        conclusions=conclusions,
        registration=registration,
        keywords=keywords,
        abstract=abstract_text,
    )
    medLog.debug("abstract: \n %s" % abstract_obj.to_complete_abs())

    return SingleDocInfo(
        PMCID=PMCID,
        doi=doi,
        abstract=abstract_obj,
        affiliations=Affiliation,
        keyword=keywords,
        PMID=PMID,
    )


def geteachinfo(dbpath):
    tablename = 'pubmed%s' % projConfig.savetime

    PMID_list = DBFetchAllPMID(dbpath, tablename)
    if PMID_list == None:
        medLog.error("数据库读取出错，内容为空\n")
    start = time.time()

    # 使用异步的asyncio和aiohttp来一次性获取所有文献页面的详细情况
    # 考虑一次性获取的请求数量越多，整个可靠性会下降，我们不妨一次性最多请求50个页面吧,由BATCH_SIZE，默认50

    # 注意BATCH_SIZE的大小

    results = []
    medLog.info("Geteachinfo BATCH_SIZE: %s " % BATCH_SIZE)

    for i in range(0, len(PMID_list), BATCH_SIZE):
        target_pmid: [str] = []
        if i + BATCH_SIZE > len(PMID_list):
            target_pmid = [pmid.PMID for pmid in PMID_list[i:]]
        else:
            target_pmid = [pmid.PMID for pmid in PMID_list[i:i + BATCH_SIZE]]

        try:
            results.extend(asyncio.run(WebHelper.GetAllHtmlAsync(target_pmid)))
        except Exception as e:
            medLog.error("异步爬取singleinfo时发生错误: %s " % e)
            medLog.error("默认自动跳过")
            continue

    medLog.info(len(results))
    end = time.time()
    medLog.info("geteachinfo() takes %.2f seconds" % (end - start))

    for i in range(len(results)):
        medLog.info("当前序号: %s " % i)
        singleDocInfo = parse_single_info(etree.HTML(results[i]))

        DBSaveInfo(singleDocInfo, dbpath)
        # todo
        # 通过cache机制来大幅提高单页检索的效率，已经存在的文献直接从本地的数据库进行加载
    ExcelHelper.PD_To_excel(dbpath)


if __name__ == '__main__':
    PMID = "36191595"
    ret = get_single_info(requests.Session(), PMID)
    print("PMCID:", ret.PMCID)
    print("PMID:", ret.PMID)
    print("DOI:", ret.doi)
    print("Affiliations:")
    for aff in ret.affiliations:
        print(aff)
    print("Abstract:")
    print(ret.abstract.to_complete_abs())
