from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Union

class ABS_PartEnumType(Enum):
    Background = "Background"
    Methods = "Methods"
    Results = "Results"
    Conclusions = "Conclusions"
    Registration = "Registration"
    Keywords = "Keywords"

class ArticleFreeType(Enum):
    NoneFreeArticle = 0
    FreeArticle = 1
    FreePMCArticle = 2

@dataclass
class SingleSearchData:
    """
    存储搜索页面每一条结果获得的信息
    """
    doctitle: str
    short_author: str
    full_author: str
    short_journal: str
    full_journal: str
    PMID: str
    freemark: ArticleFreeType
    reviewmark: bool

    def to_string(self) -> str:
        """
        将所有字段用空格连接成一个字符串
        """
        return ' '.join([
            self.doctitle,
            self.short_author,
            self.full_author,
            self.short_journal,
            self.full_journal,
            self.PMID,
            str(self.freemark.value),
            str(self.reviewmark)
        ])

class SingleDocInfo:
    """
    表示通过单个文献打开页面获得的信息，非数据库中包含完整属性的记录
    """
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