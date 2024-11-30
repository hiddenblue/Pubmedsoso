# -*- coding: utf-8 -*-
import os
import re
import time
from typing import List

from lxml import etree

from DBHelper import DBSaveInfo, DBFetchAllPMID
from DataType import ABS_PartEnumType, SingleDocInfo, Abstract
from ExcelHelper import ExcelHelper
from WebHelper import WebHelper
from timevar import savetime
from LogHelper import print_error


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


def get_single_info(PMID: str) -> SingleDocInfo:
    try:
        html = WebHelper.GetHTML(PMID)
    except Exception as e:
        print_error(f"请求失败: {e}")
        return SingleDocInfo()

    if os.getenv("LOCAL_DEBUG"):
        parser = etree.HTMLParser()
        html_etree = etree.parse("./Pubmed2.html", parser)
    else:
        html_etree = etree.HTML(html)

    # 提取PMCID和DOI
    PMCID_elem = html_etree.xpath(".//span[@class='identifier pmc']//a[@class='id-link']/text()")
    if len(PMCID_elem) != 0:
        PMCID = [pmcid.strip() for pmcid in PMCID_elem if "PMC" in pmcid][0]
    else:
        PMCID = ""
    print("PMCID", PMCID)
    
    doi = ""
    DOI_elem = html_etree.xpath(".//ul[@id='full-view-identifiers']//span[@class='identifier doi']/a[@class='id-link']/text()")
    if len(DOI_elem) != 0:
        doi = DOI_elem[0].strip()
    print("DOI", doi)
    

    # Affiliation  type list[str]
    Affiliation = []

    affi_elem = html_etree.xpath("//div[@class='expanded-authors']")
    if len(affi_elem) == 0:
        Affiliation = []
    else:
        # 有两组重复的附属单位，我们取第一组就行了
        affi_elem = affi_elem[0]
        # print(affi_elem)
        affi_list = affi_elem.xpath(".//li[@data-affiliation-id]/text()")
        # print(affi_list)

        for i in range(len(affi_list)):
            # 利用正则去掉多余的空格
            temp_affitem = re.sub(r'\s{2,}', '', str(affi_list[i]).strip()).strip()
            Affiliation.append(str(i + 1) + "." + temp_affitem)
        print("Affiliation", Affiliation)

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
    print("abstract", abstract_obj.to_complete_abs())

    return SingleDocInfo(
        PMCID=PMCID,
        doi=doi,
        abstract=abstract_obj,
        affiliations=Affiliation,
        keyword=keywords,
        PMID=PMID,
    )


def geteachinfo(dbpath):
    tablename = 'pubmed%s' % savetime

    PMID_list = DBFetchAllPMID(dbpath, tablename)
    if PMID_list == None:
        print("数据库读取出错，内容为空\n")
    for i in range(len(PMID_list)):
        print("当前序号: ", i)
        singleDocInfo = get_single_info(PMID_list[i].PMID)

        DBSaveInfo(singleDocInfo, dbpath)
        # todo
        # 异步执行提供速度
        # todo
        # 通过cache机制来大幅提高单页检索的效率，已经存在的文献直接从本地的数据库进行加载
        time.sleep(0.1)
    ExcelHelper.PD_To_excel(dbpath)


if __name__ == '__main__':
    PMID = "30743289"
    ret = get_single_info(PMID)
    print("PMCID:", ret.PMCID)
    print("PMID:", ret.PMID)
    print("DOI:", ret.doi)
    print("Affiliations:")
    for aff in ret.affiliations:
        print(aff)
    print("Abstract:")
    print(ret.abstract.to_complete_abs())
