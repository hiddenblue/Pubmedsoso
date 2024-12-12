from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


class ABS_PartEnumType(Enum):
    Background = "Background"
    Methods = "Methods"
    Results = "Results"
    Conclusions = "Conclusions"
    Registration = "Registration"
    Keywords = "Keywords"


class ArticleFreeType(Enum):
    NoneFreeArticle = "None"
    FreeArticle = "FreeArticle"
    FreePMCArticle = "FreePMCArticle"


@dataclass
class TempPMID:
    PMCID: str
    PMID: str
    doctitle: str


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
        return ' '.join([self.doctitle,
                         self.short_author,
                         self.full_author,
                         self.short_journal,
                         self.full_journal,
                         self.PMID,
                         str(self.freemark.value),
                         str(self.reviewmark)]
                        )


class SingleDocInfo:
    """
    表示通过单个文献打开页面获得的信息，非数据库中包含完整属性的记录
    """

    def __init__(
            self,
            PMCID: str = "",
            doi: str = "",
            abstract: Optional['Abstract'] = None,
            affiliations: Optional[List[str]] = None,
            keyword: str = "",
            PMID: str = "",
    ):
        self.PMCID = PMCID
        self.doi = doi
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
            abstract: str = "",
    ):
        self.background = background
        self.methods = methods
        self.results = results
        self.conclusions = conclusions
        self.registration = registration
        self.keywords = keywords
        self.abstract = abstract

    def to_complete_abs(self) -> str:
        """
        输出一个格式化后的完整摘要
        """
        parts = []
        if self.background:
            parts.append(self.background.strip())
        if self.methods:
            parts.append(self.methods.strip())
        if self.results:
            parts.append(self.results.strip())
        if self.conclusions:
            parts.append(self.conclusions.strip())
        if self.registration:
            parts.append(self.registration.strip())
        if self.keywords:
            parts.append(self.keywords.strip())
        if self.abstract:
            parts.append(f"Abstract: {self.abstract.strip()}")
        return "\n".join(parts)


@dataclass
class Publication:
    """
    这个类将数据库里面所有的数据整合成了一个大的类
    
    """
    doctitle: str
    short_author: str
    full_author: str
    short_journal: str
    full_journal: str
    doi: str
    pmid: str
    pmcid: str
    abstract: str
    keyword: str
    affiliations: str
    freemark: str
    reviewmark: bool
    savepath: str

    def __repr__(self) -> str:
        return (f"Publication(doctitle='{self.doctitle}', short_author='{self.short_author}', "
                f"full_author='{self.full_author}', short_journal='{self.short_journal}', "
                f"full_journal='{self.full_journal}', doi='{self.doi}', pmid={self.pmid}, pmcid='{self.pmcid}', "
                f"abstract='{self.abstract}', keyword='{self.keyword}', affiliations='{self.affiliations}', "
                f"freemark={self.freemark}, reviewmark={self.reviewmark}, savepath='{self.savepath}')")

    def to_dict(self) -> dict:
        return {
            "doctitle": self.doctitle,
            "short_author": self.short_author,
            "full_author": self.full_author,
            "short_journal": self.short_journal,
            "full_journal": self.full_journal,
            "doi": self.doi,
            "pmid": self.pmid,
            "pmcid": self.pmcid,
            "abstract": self.abstract,
            "keyword": self.keyword,
            "affiliations": self.affiliations,
            "freemark": self.freemark,
            "reviewmark": self.reviewmark,
            "savepath": self.savepath
        }
