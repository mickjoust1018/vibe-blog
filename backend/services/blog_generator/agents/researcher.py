"""
Researcher Agent - 素材收集
"""

import json
import logging
from typing import Dict, Any, List, Optional

from ..prompts.prompt_manager import get_prompt_manager

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """
    主题素材收集师 - 负责联网搜索收集背景资料
    """
    
    def __init__(self, llm_client, search_service=None):
        """
        初始化 Researcher Agent
        
        Args:
            llm_client: LLM 客户端
            search_service: 搜索服务 (可选，如果不提供则跳过搜索)
        """
        self.llm = llm_client
        self.search_service = search_service
    
    def generate_search_queries(self, topic: str, target_audience: str) -> List[str]:
        """
        生成搜索查询
        
        Args:
            topic: 技术主题
            target_audience: 目标受众
            
        Returns:
            搜索查询列表
        """
        # 默认搜索策略
        default_queries = [
            f"{topic} 教程 tutorial",
            f"{topic} 最佳实践 best practices",
            f"{topic} 常见问题 FAQ",
        ]
        
        if not self.llm:
            return default_queries
        
        try:
            pm = get_prompt_manager()
            prompt = pm.render_search_query(
                topic=topic,
                target_audience=target_audience
            )
            
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            queries = json.loads(response)
            if isinstance(queries, list):
                return queries
            return default_queries
            
        except Exception as e:
            logger.warning(f"生成搜索查询失败: {e}，使用默认查询")
            return default_queries
    
    def search(self, topic: str, target_audience: str, max_results: int = 10) -> List[Dict]:
        """
        执行搜索
        
        Args:
            topic: 技术主题
            target_audience: 目标受众
            max_results: 最大结果数
            
        Returns:
            搜索结果列表
        """
        if not self.search_service:
            logger.warning("搜索服务未配置，跳过搜索")
            return []
        
        queries = self.generate_search_queries(topic, target_audience)
        all_results = []
        
        for query in queries:
            try:
                result = self.search_service.search(query, max_results=max_results // len(queries))
                if result.get('success') and result.get('results'):
                    all_results.extend(result['results'])
            except Exception as e:
                logger.error(f"搜索失败 [{query}]: {e}")
        
        # 去重
        seen_urls = set()
        unique_results = []
        for item in all_results:
            url = item.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(item)
        
        return unique_results[:max_results]
    
    def summarize(
        self,
        topic: str,
        search_results: List[Dict],
        target_audience: str,
        search_depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        整理搜索结果，生成背景知识摘要
        
        Args:
            topic: 技术主题
            search_results: 搜索结果
            target_audience: 目标受众
            search_depth: 搜索深度
            
        Returns:
            整理后的结果
        """
        if not search_results:
            return {
                "background_knowledge": f"关于 {topic} 的背景知识将在后续章节中详细介绍。",
                "key_concepts": [],
                "top_references": []
            }
        
        pm = get_prompt_manager()
        prompt = pm.render_researcher(
            topic=topic,
            search_depth=search_depth,
            target_audience=target_audience,
            search_results=search_results[:10]
        )
        
        try:
            response = self.llm.chat(
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 提取 JSON（处理 markdown 代码块）
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            
            # 尝试解析 JSON
            result = json.loads(json_str)
            key_concepts = result.get("key_concepts", [])
            
            # 调试：打印实际返回内容
            logger.info(f"LLM 返回 key_concepts 类型: {type(key_concepts)}, 值: {key_concepts}")
            
            # 如果 key_concepts 为空但有其他可能的字段名
            if not key_concepts:
                # 尝试其他可能的字段名
                for alt_key in ['keyConcepts', 'concepts', 'core_concepts', 'keywords']:
                    if result.get(alt_key):
                        key_concepts = result.get(alt_key)
                        logger.info(f"使用备选字段 {alt_key}: {key_concepts}")
                        break
            
            if key_concepts:
                logger.info(f"核心概念: {[c.get('name', c) if isinstance(c, dict) else c for c in key_concepts[:5]]}")
            
            return {
                "background_knowledge": result.get("background_knowledge", ""),
                "key_concepts": key_concepts,
                "top_references": result.get("top_references", [])
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}, 响应内容: {response[:500] if response else 'None'}")
        except Exception as e:
            logger.error(f"整理搜索结果失败: {e}")
        
        # 返回简单摘要
        return {
            "background_knowledge": '\n'.join([
                item.get('content', '')[:200] for item in search_results[:3]
            ]),
            "key_concepts": [],
            "top_references": [
                {"title": item.get('title', ''), "url": item.get('url', '')}
                    for item in search_results[:5]
                ]
            }
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行素材收集
        
        Args:
            state: 共享状态
            
        Returns:
            更新后的状态
        """
        topic = state.get('topic', '')
        target_audience = state.get('target_audience', 'intermediate')
        
        logger.info(f"开始收集素材: {topic}")
        
        # 1. 执行搜索
        search_results = self.search(topic, target_audience)
        
        # 2. 整理结果
        summary = self.summarize(
            topic=topic,
            search_results=search_results,
            target_audience=target_audience
        )
        
        # 3. 更新状态
        state['search_results'] = search_results
        state['background_knowledge'] = summary.get('background_knowledge', '')
        state['key_concepts'] = [
            c.get('name', c) if isinstance(c, dict) else c
            for c in summary.get('key_concepts', [])
        ]
        state['reference_links'] = [
            r.get('url', r) if isinstance(r, dict) else r
            for r in summary.get('top_references', [])
        ]
        
        logger.info(f"素材收集完成: {len(search_results)} 条结果, {len(state['key_concepts'])} 个核心概念")
        
        return state
