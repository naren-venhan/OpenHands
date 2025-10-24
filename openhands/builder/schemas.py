from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Literal


class TypographyToken(BaseModel):
    family: str
    weight: int
    size: str
    lineHeight: str


class ThemeTokens(BaseModel):
    colors: dict[str, str] = Field(default_factory=dict)
    typography: dict[str, TypographyToken] = Field(default_factory=dict)
    spacing: list[int] = Field(default_factory=list)
    radii: list[int] = Field(default_factory=list)
    shadows: list[str] = Field(default_factory=list)


SectionType = Literal['hero', 'productGrid', 'banner', 'footer']


class Section(BaseModel):
    type: SectionType
    variant: str | None = None
    props: dict[str, Any] = Field(default_factory=dict)


class LayoutPage(BaseModel):
    page: str
    sections: list[Section]


class LayoutMap(BaseModel):
    __root__: list[LayoutPage] = Field(default_factory=list)

    def pages(self) -> list[LayoutPage]:
        return self.__root__


class Price(BaseModel):
    amount: float
    currency: str


class ProductVariant(BaseModel):
    name: str
    options: list[str]


class Product(BaseModel):
    id: str
    slug: str
    title: str
    description: str | None = None
    images: list[str] = Field(default_factory=list)
    price: Price
    variants: list[ProductVariant] = Field(default_factory=list)
    attributes: dict[str, str] = Field(default_factory=dict)


class Catalog(BaseModel):
    products: list[Product] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)


class AuditScores(BaseModel):
    performance: float
    accessibility: float
    bestPractices: float
    seo: float


class CWV(BaseModel):
    lcp: float
    cls: float
    inp: float


class SEOReport(BaseModel):
    scores: AuditScores
    cwv: CWV
    issues: list[str] = Field(default_factory=list)


class Remediation(BaseModel):
    id: str
    priority: Literal['P0', 'P1', 'P2']
    desc: str
    fix: str
    fileHints: list[str] = Field(default_factory=list)


class BuildArtifact(BaseModel):
    repoRef: str
    branch: str
    commitSha: str
    previewUrl: str
    testSummary: dict[str, int] = Field(default_factory=dict)
    lighthouseSummary: AuditScores | None = None
