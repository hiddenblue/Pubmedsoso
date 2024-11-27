# -*- coding: utf-8 -*-
import random
import re
import sqlite3
import time
from timevar import savetime

import os
from enum import Enum
from typing import List, Optional

from lxml import etree
import requests


class SingleDocInfo:
    def __init__(
            self,
            PMCID: str = "",
            abstract: Optional['Abstract'] = None,
            affiliations: Optional[List[str]] = None,
            keyword: str = "",
            PMID: str = "",
    ):
        self.PMCID = PMCID
        self.abstract = abstract if abstract else Abstract()
        self.affiliations = affiliations if affiliations else []
        self.keyword = keyword
        self.PMID = PMID


class ABS_PartEnumType(Enum):
    Background = "Background"
    Methods = "Methods"
    Results = "Results"
    Conclusions = "Conclusions"
    Registration = "Registration"
    Keywords = "Keywords"


class Abstract:
    def __init__(
            self,
            background: str = "",
            methods: str = "",
            results: str = "",
            conclusions: str = "",
            registration: str = "",
            keywords: str = "",
    ):
        self.background = background
        self.methods = methods
        self.results = results
        self.conclusions = conclusions
        self.registration = registration
        self.keywords = keywords

    def to_complete_abs(self) -> str:
        """
        输出一个格式化后的完整摘要
        """
        parts = []
        if self.background:
            parts.append(f"Background: {self.background.strip()}")
        if self.methods:
            parts.append(f"Methods: {self.methods.strip()}")
        if self.results:
            parts.append(f"Results: {self.results.strip()}")
        if self.conclusions:
            parts.append(f"Conclusions: {self.conclusions.strip()}")
        if self.registration:
            parts.append(f"Registration: {self.registration.strip()}")
        if self.keywords:
            parts.append(f"Keywords: {self.keywords.strip()}")
        return "\n".join(parts)


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
    base_url = "https://pubmed.ncbi.nlm.nih.gov/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"
    }

    request_url = f"{base_url}{PMID}"
    try:
        response = requests.get(request_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return SingleDocInfo()

    if os.getenv("DEBUG"):
        parser = etree.HTMLParser()
        html_etree = etree.parse("./Pubmed2.html", parser)
    else:
        html = response.content.decode("utf-8")
        html_etree = etree.HTML(html)

    # 提取PMCID和DOI
    PMCID_elem = html_etree.xpath("//ul[@id='full-view-identifiers']//a[@class='id-link']/text()")
    PMCID = next((item.strip() for item in PMCID_elem if 'PMC' in item), "")
    DOI = next((item.strip() for item in PMCID_elem if '.' in item), "")

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

    # 创建Abstract实例
    abstract_obj = Abstract(
        background=background,
        methods=methods,
        results=results,
        conclusions=conclusions,
        registration=registration,
        keywords=keywords,
    )

    return SingleDocInfo(
        PMCID=PMCID,
        abstract=abstract_obj,
        affiliations=Affiliation,
        keyword=keywords,
        PMID=PMID,
    )


# print(getinfo(34794508))

def savedata3(singleinfo: SingleDocInfo, dbpath: str):
    tablename = 'pubmed%s' % savetime
    conn = None
    cursor = None
    try:
        # Connect to the database
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()

        # Prepare the data
        pmcid = singleinfo.PMCID
        abstract_str = singleinfo.abstract.to_complete_abs()
        affiliations_str = '\n'.join(singleinfo.affiliations)
        keyword = singleinfo.keyword
        pmid = singleinfo.PMID

        # Execute the update statement
        cursor.execute(f"UPDATE {tablename} SET PMCID = ?, abstract = ?, affiliations = ?, keyword = ? WHERE PMID = ?",
                       (pmcid, abstract_str, affiliations_str, keyword, pmid))
        print(f"单个页面数据写入成功 对应PMID为{pmid}\n")

    except sqlite3.Error as e:
        print(f"当前页面数据保存失败: {e}\n")
    finally:
        if conn:
            conn.commit()
            conn.close()
        if cursor:
            cursor.close()


def readdata1(dbpath, freemark):  # 读取数据库，返回想查询的文献的PMID
    tablename = 'pubmed%s' % savetime
    print(tablename)
    try:
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        try:

            if freemark == 1:
                sql = "SELECT PMCID,doctitle FROM %s WHERE freemark = '2'" % tablename
                # 根据设置的freemark参数，查找数据库文献的信息,free = 1用于查找所有免费文献用来下载，而free = 2用于拿数据所有文献去获得详细信息
                print(sql)
                cursor.execute(sql)
                print("sql执行成功\n")
                result = cursor.fetchall()
                print(result)
                print('读取sql信息成功 数据类型为PMCID和doctitle\n')
                return result
            elif freemark == 0:
                sql = "SELECT PMID FROM %s" % tablename  # 查找数据库文献的信息
                cursor.execute(sql)
                result = cursor.fetchall()
                for i in range(len(result)):
                    result[i] = result[i][0]
                print(result)
                print('读取sql信息成功，数据类型为PMID\n')
                return result

        except:
            print("目标数据库读取失败\n")
        finally:
            conn.commit()
            cursor.close()
    except:
        print("连接数据库失败，请检查目标数据库\n")


def geteachinfo(dbpath):
    tablename = 'pubmed%s' % savetime
    print('PyCharm\n')
    PMID_list = readdata1(dbpath, 0)
    if PMID_list == None:
        print("数据库读取出错，内容为空\n")
    for i in range(len(PMID_list)):
        singleDocInfo = get_single_info(PMID_list[i])

        savedata3(singleDocInfo, dbpath)
        time.sleep(random.randint(0, 2))

if __name__ == '__main__':
    PMID = "28233351"
    ret = get_single_info(PMID)
    print("PMCID:", ret.PMCID)
    print("PMID:", ret.PMID)
    print("Affiliations:")
    for aff in ret.affiliations:
        print(aff)
    print("Abstract:")
    print(ret.abstract.to_complete_abs())