import json
import os
import re
from typing import Dict, List


STOPWORDS = {
    "the",
    "and",
    "or",
    "of",
    "to",
    "in",
    "for",
    "on",
    "a",
    "an",
    "with",
    "by",
    "from",
    "at",
    "is",
    "are",
    "be",
}


class ResourceRetriever:
    """Simple RAG retriever using keyword overlap scoring."""

    def __init__(self, resources: List[Dict[str, str]]):
        self.resources = resources

    @classmethod
    def from_file(cls, path: str) -> "ResourceRetriever":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return cls(data)

    def retrieve(self, topic: str, subtopic: str, top_k: int = 3) -> List[Dict[str, str]]:
        query_tokens = self._tokenize(f"{topic} {subtopic}")
        scored = []

        for resource in self.resources:
            score = self._score_resource(resource, query_tokens)
            if score > 0:
                scored.append((score, resource))

        scored.sort(key=lambda item: item[0], reverse=True)
        results = [item[1] for item in scored[:top_k]]
        return [self._format_resource(resource) for resource in results]

    def _score_resource(self, resource: Dict[str, str], query_tokens: List[str]) -> int:
        title_tokens = self._tokenize(resource.get("name", ""))
        topic_tokens = self._tokenize(resource.get("topic", ""))
        subtopic_tokens = self._tokenize(resource.get("subtopic", ""))
        tag_tokens = self._tokenize(" ".join(resource.get("tags", [])))

        score = 0
        score += 3 * self._overlap(query_tokens, tag_tokens)
        score += 2 * self._overlap(query_tokens, title_tokens)
        score += 2 * self._overlap(query_tokens, topic_tokens)
        score += 2 * self._overlap(query_tokens, subtopic_tokens)
        return score

    def _overlap(self, query_tokens: List[str], tokens: List[str]) -> int:
        return len(set(query_tokens) & set(tokens))

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        return [token for token in tokens if token not in STOPWORDS]

    def _format_resource(self, resource: Dict[str, str]) -> Dict[str, str]:
        return {
            "name": resource.get("name", ""),
            "url": resource.get("url", ""),
            "type": resource.get("type", ""),
        }


def get_default_resource_path() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "data", "resources.json")
