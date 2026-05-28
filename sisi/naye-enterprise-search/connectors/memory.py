"""
MEMORY.md 连接器 - 搜索长期记忆
"""

import os
import re
import glob
from datetime import datetime
from typing import List
import sys
sys.path.append('..')
from commands.search import SearchResult


class MemoryConnector:
    """MEMORY.md 和 memory/*.md 搜索连接器"""
    
    def __init__(self, config: dict):
        self.root_path = os.path.expanduser(config["root_path"])
        self.pattern = config["file_pattern"]
        self.index_fields = config.get("index_fields", [])
        self._build_index()
    
    def _build_index(self):
        """构建倒排索引"""
        self.index = {}
        
        # 索引所有memory文件
        files = glob.glob(f"{self.root_path}/**/{self.pattern}", recursive=True)
        
        for filepath in files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 提取日期（从文件名或内容）
                date = self._extract_date(filepath, content)
                
                # 分词索引
                words = self._tokenize(content)
                for word in words:
                    if word not in self.index:
                        self.index[word] = []
                    self.index[word].append({
                        "path": filepath,
                        "date": date,
                        "content": content[:5000]  # 存储前5000字符
                    })
            except Exception as e:
                print(f"索引失败 {filepath}: {e}")
    
    def _extract_date(self, filepath: str, content: str) -> datetime:
        """从文件名或内容提取日期"""
        # 尝试从文件名提取 2026-05-28
        date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', filepath)
        if date_match:
            return datetime(*map(int, date_match.groups()))
        
        # 尝试从内容提取
        content_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', content[:500])
        if content_match:
            return datetime(*map(int, content_match.groups()))
        
        return datetime.now()
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 提取中文字符和英文单词
        chinese = re.findall(r'[\u4e00-\u9fff]+', text)
        english = re.findall(r'[a-zA-Z_]+', text)
        return chinese + english
    
    def search(self, keywords: List[str], filters: dict = None) -> List[SearchResult]:
        """搜索memory文件"""
        results = []
        
        for keyword in keywords:
            # 查找包含关键词的文档
            matches = self.index.get(keyword, [])
            
            for match in matches:
                # 应用过滤
                if filters:
                    if "after" in filters and match["date"] < filters["after"]:
                        continue
                    if "before" in filters and match["date"] > filters["before"]:
                        continue
                
                # 提取摘要
                excerpt = self._extract_excerpt(match["content"], keyword)
                
                # 计算分数
                score = self._calculate_score(match["content"], keywords)
                
                results.append(SearchResult(
                    source="memory",
                    title=os.path.basename(match["path"]),
                    excerpt=excerpt,
                    path=match["path"],
                    score=score,
                    timestamp=match["date"]
                ))
        
        return results
    
    def _extract_excerpt(self, content: str, keyword: str, context=100) -> str:
        """提取关键词周围的摘要"""
        idx = content.find(keyword)
        if idx == -1:
            return content[:200]
        
        start = max(0, idx - context)
        end = min(len(content), idx + len(keyword) + context)
        
        excerpt = content[start:end]
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(content):
            excerpt = excerpt + "..."
        
        return excerpt.replace(keyword, f"**{keyword}**")
    
    def _calculate_score(self, content: str, keywords: List[str]) -> float:
        """计算相关性分数"""
        score = 0.0
        content_lower = content.lower()
        
        for kw in keywords:
            count = content_lower.count(kw.lower())
            score += count * 0.1  # 每次出现+0.1
        
        # 标题匹配额外加分
        first_line = content.split('\n')[0] if content else ""
        for kw in keywords:
            if kw in first_line:
                score += 0.5
        
        return min(score, 1.0)  # 最高1.0


if __name__ == "__main__":
    # 测试
    config = {
        "root_path": "~/.openclaw/workspace/memory",
        "file_pattern": "*.md",
        "index_fields": ["date", "topic"]
    }
    
    connector = MemoryConnector(config)
    results = connector.search(["梁越"])
    
    for r in results[:3]:
        print(f"\n来源: {r.source}")
        print(f"标题: {r.title}")
        print(f"分数: {r.score:.2f}")
        print(f"摘要: {r.excerpt[:200]}...")
