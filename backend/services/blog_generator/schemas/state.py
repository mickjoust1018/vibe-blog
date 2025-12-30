"""
共享状态和数据模型定义
"""

from typing import TypedDict, List, Optional, Literal
from pydantic import BaseModel, Field


class SectionOutline(BaseModel):
    """章节大纲"""
    id: str
    title: str
    key_concept: str
    content_outline: List[str] = Field(default_factory=list)
    image_type: Literal["flowchart", "architecture", "sequence", "comparison", "chart", "none"] = "none"
    image_description: str = ""
    code_blocks: int = 0
    has_output_block: bool = False
    key_quote: str = ""


class BlogOutline(BaseModel):
    """博客大纲"""
    title: str
    subtitle: str
    reading_time: int
    article_type: Literal["problem-solution", "tutorial", "comparison"]
    introduction: str
    core_value: str
    table_of_contents: List[str] = Field(default_factory=list)
    sections: List[SectionOutline] = Field(default_factory=list)
    conclusion_summary_points: List[str] = Field(default_factory=list)
    conclusion_next_steps: str = ""
    reference_links: List[str] = Field(default_factory=list)


class SectionContent(BaseModel):
    """章节内容"""
    id: str
    title: str
    content: str  # Markdown 内容
    image_ids: List[str] = Field(default_factory=list)
    code_ids: List[str] = Field(default_factory=list)


class CodeBlock(BaseModel):
    """代码块"""
    id: str
    code: str
    output: str
    explanation: str
    language: str = "python"


class ImageResource(BaseModel):
    """图片资源"""
    id: str
    render_method: Literal["mermaid", "ai_image", "matplotlib"]
    content: str  # Mermaid 代码 或 AI Prompt 或 Python 代码
    rendered_path: Optional[str] = None  # 渲染后的图片路径
    caption: str


class VaguePoint(BaseModel):
    """模糊点 (Questioner 输出)"""
    location: str  # 段落位置或引用文本
    issue: str  # 问题描述
    question: str  # 追问问题
    suggestion: str  # 建议补充的内容类型


class QuestionResult(BaseModel):
    """追问结果"""
    section_id: str
    is_detailed_enough: bool
    vague_points: List[VaguePoint] = Field(default_factory=list)
    depth_score: int  # 0-100


class ReviewIssue(BaseModel):
    """审核问题"""
    section_id: str
    issue_type: Literal["logic", "accuracy", "completeness", "image", "readability"]
    severity: Literal["high", "medium", "low"]
    description: str
    suggestion: str


class SearchResult(BaseModel):
    """搜索结果"""
    title: str
    url: str
    content: str
    source: str = ""
    publish_date: str = ""
    relevance_score: float = 0.0


class SharedState(TypedDict):
    """Multi-Agent 共享状态"""
    
    # 输入
    topic: str
    article_type: Literal["problem-solution", "tutorial", "comparison"]
    target_audience: Literal["beginner", "intermediate", "advanced"]
    target_length: Literal["short", "medium", "long"]
    source_material: Optional[str]
    
    # 素材收集 (Researcher 输出)
    search_results: List[dict]  # 搜索结果列表
    background_knowledge: Optional[str]  # 背景知识摘要
    key_concepts: List[str]  # 提取的核心概念
    reference_links: List[str]  # 参考链接
    
    # 大纲 (Planner 输出)
    outline: Optional[dict]
    
    # 章节内容 (Writer 输出)
    sections: List[dict]
    
    # 代码块 (Coder 输出)
    code_blocks: List[dict]
    
    # 图片资源 (Artist 输出)
    images: List[dict]
    
    # 追问结果 (Questioner 输出)
    question_results: List[dict]
    all_sections_detailed: bool
    questioning_count: int  # 追问次数，防止无限循环
    
    # 审核结果 (Reviewer 输出)
    review_score: int
    review_issues: List[dict]
    review_approved: bool
    revision_count: int  # 修订次数，防止无限循环
    
    # 最终输出 (Assembler 输出)
    final_markdown: Optional[str]
    final_html: Optional[str]
    output_folder: Optional[str]
    
    # 错误信息
    error: Optional[str]


def create_initial_state(
    topic: str,
    article_type: str = "tutorial",
    target_audience: str = "intermediate",
    target_length: str = "medium",
    source_material: str = None,
) -> SharedState:
    """创建初始状态"""
    return SharedState(
        topic=topic,
        article_type=article_type,
        target_audience=target_audience,
        target_length=target_length,
        source_material=source_material,
        search_results=[],
        background_knowledge=None,
        key_concepts=[],
        reference_links=[],
        outline=None,
        sections=[],
        code_blocks=[],
        images=[],
        question_results=[],
        all_sections_detailed=False,
        questioning_count=0,
        review_score=0,
        review_issues=[],
        review_approved=False,
        revision_count=0,
        final_markdown=None,
        final_html=None,
        output_folder=None,
        error=None,
    )
