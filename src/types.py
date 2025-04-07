from typing import TypeAlias, TypedDict

StringOrPageDataList: TypeAlias = str | list['PageData']


class UserInfo(TypedDict):
    full_name: str
    date: str
    national_number: str
    address: str
    postal_code: str


class Summary(TypedDict):
    TOTAL_TAX_BASIS_IN_EUR: str
    TOTAL_TAX_AMOUNT_IN_EUR: str
    TOTAL_TRANSACTIONS: str


class PageData(TypedDict):
    rate: str
    summary: Summary


class ExtractedData(TypedDict):
    page_0: dict[str, UserInfo]
    page_X: dict[str, StringOrPageDataList]
