"""
Prompt 模板模块 - 使用 Jinja2 管理 Prompt

模板文件位于 templates/ 目录下:
- researcher.j2      - 素材收集
- search_query.j2    - 搜索查询生成
- planner.j2         - 大纲规划
- writer.j2          - 内容撰写
- writer_enhance.j2  - 内容深化
- coder.j2           - 代码生成
- artist.j2          - 配图生成
- questioner.j2      - 追问检查
- reviewer.j2        - 质量审核
- assembler_header.j2 - 文章头部
- assembler_footer.j2 - 文章尾部
"""

from .prompt_manager import PromptManager, get_prompt_manager

__all__ = [
    'PromptManager',
    'get_prompt_manager',
]
