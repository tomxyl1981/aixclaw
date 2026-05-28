"""
/naye:search 命令实现 - 那耶村知识库统一搜索
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    source: str
    title: str
    excerpt: str
    path: str
    score: float
    timestamp: Optional[datetime] = None
    metadata: Dict = None


class NayeSearchCommand:
    """那耶村企业搜索命令"""
    
    def __init__(self, mcp_config: dict):
        self.mcp = mcp_config
        self.connectors = self._init_connectors()
    
    def _init_connectors(self):
        """初始化所有连接器"""
        from connectors.memory import MemoryConnector
        from connectors.knowledge import KnowledgeConnector
        from connectors.workspace import WorkspaceConnector
        
        return {
            "memory": MemoryConnector(self.mcp["mcpServers"]["memory"]),
            "knowledge": KnowledgeConnector(self.mcp["mcpServers"]["knowledge"]),
            "workspace": WorkspaceConnector(self.mcp["mcpServers"]["workspace"]),
        }
    
    def execute(self, query: str, filters: dict = None) -> dict:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            filters: 可选过滤条件
                - from: 来源（memory/knowledge/workspace）
                - after: 时间之后
                - before: 时间之前
                - type: 文档类型
        
        Returns:
            搜索结果字典
        """
        # 1. 解析查询意图
        parsed = self._parse_query(query)
        
        # 2. 确定搜索范围
        sources = self._determine_sources(filters)
        
        # 3. 并行搜索所有源
        all_results = []
        for source_name in sources:
            connector = self.connectors.get(source_name)
            if connector:
                results = connector.search(parsed["keywords"], filters)
                all_results.extend(results)
        
        # 4. 去重和排序
        deduped = self._deduplicate(all_results)
        ranked = self._rank_results(deduped, parsed)
        
        # 5. 合成回答
        synthesis = self._synthesize(query, ranked)
        
        return {
            "query": query,
            "parsed": parsed,
            "sources_searched": sources,
            "total_results": len(ranked),
            "results": ranked[:10],  # 返回前10
            "synthesis": synthesis,
            "ch_cost": 0.1
        }
    
    def _parse_query(self, query: str) -> dict:
        """解析查询，提取关键词和意图"""
        # 提取显式过滤器
        filters = {}
        
        # from:xxx
        from_match = re.search(r'from:(\w+)', query)
        if from_match:
            filters["source"] = from_match.group(1)
            query = query.replace(from_match.group(0), '')
        
        # after:YYYY-MM-DD
        after_match = re.search(r'after:(\d{4}-\d{2}-\d{2})', query)
        if after_match:
            filters["after"] = datetime.strptime(after_match.group(1), "%Y-%m-%d")
            query = query.replace(after_match.group(0), '')
        
        # before:YYYY-MM-DD
        before_match = re.search(r'before:(\d{4}-\d{2}-\d{2})', query)
        if before_match:
            filters["before"] = datetime.strptime(before_match.group(1), "%Y-%m-%d")
            query = query.replace(before_match.group(0), '')
        
        # 清理并提取关键词
        keywords = [k.strip() for k in query.split() if k.strip()]
        
        # 意图识别
        intent = self._detect_intent(keywords)
        
        return {
            "keywords": keywords,
            "filters": filters,
            "intent": intent,
            "original": query
        }
    
    def _detect_intent(self, keywords: List[str]) -> str:
        """检测搜索意图"""
        intent_keywords = {
            "project_status": ["项目", "进度", "状态", "进展"],
            "decision": ["决定", "决策", "结论", "方案"],
            "person": ["谁", "负责", "联系"],
            "time": ["什么时候", "时间", "日期"],
            "location": ["哪里", "地点", "位置"],
            "how": ["怎么", "如何", "步骤"],
            "ch": ["CH", "Coin Hour", "费用", "成本"]
        }
        
        for intent, words in intent_keywords.items():
            if any(kw in " ".join(keywords) for kw in words):
                return intent
        
        return "general"
    
    def _determine_sources(self, filters: dict) -> List[str]:
        """确定要搜索的数据源"""
        if filters and "source" in filters:
            return [filters["source"]]
        
        # 默认搜索所有源
        return ["memory", "knowledge", "workspace"]
    
    def _deduplicate(self, results: List[SearchResult]) -> List[SearchResult]:
        """跨源去重"""
        seen = set()
        unique = []
        
        for r in results:
            # 基于内容指纹去重
            fingerprint = hash(r.excerpt[:100])
            if fingerprint not in seen:
                seen.add(fingerprint)
                unique.append(r)
        
        return unique
    
    def _rank_results(self, results: List[SearchResult], parsed: dict) -> List[SearchResult]:
        """结果排序"""
        # 基础分数
        for r in results:
            # 时效性加分（越新越高）
            if r.timestamp:
                days_old = (datetime.now() - r.timestamp).days
                freshness_score = max(0, 1 - days_old / 30)  # 30天内逐渐衰减
                r.score += freshness_score * 0.2
            
            # 意图匹配加分
            if parsed["intent"] == "ch" and "CH" in r.excerpt:
                r.score += 0.3
            
            # 来源权威性（memory > knowledge > workspace）
            source_weight = {"memory": 1.0, "knowledge": 0.9, "workspace": 0.7}
            r.score *= source_weight.get(r.source, 0.5)
        
        # 按分数排序
        return sorted(results, key=lambda x: x.score, reverse=True)
    
    def _synthesize(self, query: str, results: List[SearchResult]) -> str:
        """合成自然语言回答"""
        if not results:
            return f"未找到关于\"{query}\"的相关信息。"
        
        # 提取关键信息
        sources = list(set([r.source for r in results[:3]]))
        
        synthesis = f"根据{', '.join(sources)}中的信息，"
        
        # 根据意图调整回答
        top_result = results[0]
        
        if "项目" in query or "进度" in query:
            synthesis += f"关于项目进度：{top_result.excerpt[:200]}..."
        elif "谁" in query:
            synthesis += f"相关人物信息：{top_result.excerpt[:200]}..."
        elif "CH" in query or "Coin Hour" in query:
            synthesis += f"Coin Hour相关信息：{top_result.excerpt[:200]}..."
        else:
            synthesis += f"找到以下内容：{top_result.excerpt[:200]}..."
        
        return synthesis


# 命令入口
def search(query: str, **filters) -> dict:
    """
    /naye:search 命令入口
    
    使用示例：
        /naye:search 梁越的作品
        /naye:search from:memory CH分配方案
        /naye:search after:2026-05-01 项目进度
    """
    import json
    with open(".aix/mcp.json") as f:
        mcp = json.load(f)
    
    cmd = NayeSearchCommand(mcp)
    return cmd.execute(query, filters)


if __name__ == "__main__":
    # 测试
    result = search("梁越的作品")
    print(json.dumps(result, indent=2, default=str))
