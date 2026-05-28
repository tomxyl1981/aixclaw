"""
knowledge/ 连接器 - 搜索知识库
"""

import os
import re
import glob
import yaml
from datetime import datetime
from typing import List, Dict
import sys
sys.path.append('..')
from commands.search import SearchResult


class KnowledgeConnector:
    """knowledge/ 目录搜索连接器"""
    
    def __init__(self, config: dict):
        self.root_path = os.path.expanduser(config["root_path"])
        self.pattern = config["file_pattern"]
        self.index_fields = config.get("index_fields", [])
        self.documents = self._load_documents()
    
    def _load_documents(self) -> List[Dict]:
        """加载所有知识文档"""
        documents = []
        
        files = glob.glob(f"{self.root_path}/**/{self.pattern}", recursive=True)
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析Front Matter（如果有）
                metadata = self._parse_frontmatter(content)
                
                # 提取正文
                body = self._extract_body(content)
                
                documents.append({
                    "path": filepath,
                    "title": metadata.get("title", os.path.basename(filepath)),
                    "category": metadata.get("category", "general"),
                    "tags": metadata.get("tags", []),
                    "project": metadata.get("project", ""),
                    "content": body,
                    "metadata": metadata,
                    "mtime": datetime.fromtimestamp(os.path.getmtime(filepath))
                })
            except Exception as e:
                print(f"加载失败 {filepath}: {e}")
        
        return documents
    
    def _parse_frontmatter(self, content: str) -> dict:
        """解析Markdown Front Matter"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    return yaml.safe_load(parts[1]) or {}
                except:
                    pass
        return {}
    
    def _extract_body(self, content: str) -> str:
        """提取正文（去掉Front Matter）"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    
    def search(self, keywords: List[str], filters: dict = None) -> List[SearchResult]:
        """搜索知识库"""
        results = []
        
        for doc in self.documents:
            # 应用过滤器
            if filters:
                if "category" in filters and doc["category"] != filters["category"]:
                    continue
                if "tag" in filters and filters["tag"] not in doc["tags"]:
                    continue
                if "project" in filters and doc["project"] != filters["project"]:
                    continue
            
            # 计算匹配分数
            score, matched_keywords = self._match_score(doc, keywords)
            
            if score > 0:
                # 提取最佳摘要
                excerpt = self._best_excerpt(doc["content"], matched_keywords)
                
                results.append(SearchResult(
                    source="knowledge",
                    title=doc["title"],
                    excerpt=excerpt,
                    path=doc["path"],
                    score=score,
                    timestamp=doc["mtime"],
                    metadata={
                        "category": doc["category"],
                        "tags": doc["tags"],
                        "project": doc["project"]
                    }
                ))
        
        return results
    
    def _match_score(self, doc: Dict, keywords: List[str]) -> tuple:
        """计算匹配分数和匹配的关键词"""
        score = 0.0
        matched = []
        
        content = doc["content"].lower()
        title = doc["title"].lower()
        
        for kw in keywords:
            kw_lower = kw.lower()
            
            # 标题匹配（高分）
            if kw_lower in title:
                score += 0.4
                matched.append(kw)
            
            # 内容匹配
            count = content.count(kw_lower)
            if count > 0:
                score += min(count * 0.1, 0.4)  # 最高0.4
                if kw not in matched:
                    matched.append(kw)
            
            # 标签匹配（中分）
            if any(kw_lower in tag.lower() for tag in doc["tags"]):
                score += 0.2
                if kw not in matched:
                    matched.append(kw)
        
        return min(score, 1.0), matched
    
    def _best_excerpt(self, content: str, keywords: List[str], max_length=300) -> str:
        """提取最佳摘要（包含最多关键词）"""
        if not keywords:
            return content[:max_length]
        
        # 找到包含最多关键词的段落
        paragraphs = content.split('\n\n')
        best_para = ""
        best_count = 0
        
        for para in paragraphs:
            count = sum(1 for kw in keywords if kw.lower() in para.lower())
            if count > best_count and len(para) <= max_length * 2:
                best_count = count
                best_para = para
        
        if best_para:
            excerpt = best_para[:max_length]
            # 高亮关键词
            for kw in keywords:
                excerpt = excerpt.replace(kw, f"**{kw}**")
                excerpt = excerpt.replace(kw.lower(), f"**{kw.lower()}**")
            return excerpt
        
        return content[:max_length]


if __name__ == "__main__":
    # 测试
    config = {
        "root_path": "~/.openclaw/workspace/knowledge",
        "file_pattern": "*.md",
        "index_fields": ["category", "tags", "project"]
    }
    
    connector = KnowledgeConnector(config)
    results = connector.search(["短剧", "平台"])
    
    print(f"找到 {len(results)} 个结果\n")
    for r in results[:3]:
        print(f"[{r.source}] {r.title}")
        print(f"  分类: {r.metadata.get('category', 'N/A')}")
        print(f"  标签: {', '.join(r.metadata.get('tags', []))}")
        print(f"  分数: {r.score:.2f}")
        print(f"  摘要: {r.excerpt[:150]}...\n")
