"""
Complexity analyzer — heuristic task analysis for decomposition.

Extracted from TaskDecompositionService.ComplexityAnalyzer.
Analyzes task descriptions to infer complexity, capabilities, and effort estimates.
No external dependencies.
"""

import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass, field

from orchestrator.tasks.entity import TaskComplexity, TaskEstimate


# --- Keyword databases ---

TECHNICAL_KEYWORDS: Set[str] = {
    "api", "database", "auth", "oauth", "jwt", "websocket", "graphql",
    "microservice", "docker", "kubernetes", "terraform", "ci/cd",
    "redis", "postgres", "mysql", "mongodb", "elasticsearch",
    "nginx", "load balancer", "cdn", "s3", "lambda", "serverless",
    "react", "vue", "angular", "typescript", "webpack", "vite",
    "grpc", "kafka", "rabbitmq", "celery", "celery",
    "encryption", "tls", "ssl", "cors", "xss", "csrf",
    "migrate", "schema", "index", "partition", "shard",
    "cache", "memcached", "rate limit", "throttle",
    "webhook", "callback", "polling", "streaming",
}

CAPABILITY_KEYWORDS: Dict[str, str] = {
    # Backend capabilities
    "api": "backend_api",
    "endpoint": "backend_api",
    "rest": "backend_api",
    "graphql": "backend_api",
    "grpc": "backend_api",
    "database": "database",
    "sql": "database",
    "schema": "database",
    "migration": "database",
    "redis": "caching",
    "cache": "caching",
    "auth": "authentication",
    "login": "authentication",
    "oauth": "authentication",
    "jwt": "authentication",
    "session": "authentication",
    # Frontend capabilities
    "ui": "frontend",
    "frontend": "frontend",
    "react": "frontend",
    "vue": "frontend",
    "angular": "frontend",
    "css": "frontend",
    "html": "frontend",
    "component": "frontend",
    # Infrastructure
    "docker": "devops",
    "kubernetes": "devops",
    "deploy": "devops",
    "ci/cd": "devops",
    "terraform": "devops",
    "nginx": "devops",
    "monitoring": "observability",
    "logging": "observability",
    "metrics": "observability",
    "tracing": "observability",
    # Testing
    "test": "testing",
    "unit test": "testing",
    "integration": "testing",
    "e2e": "testing",
    # Security
    "security": "security",
    "encryption": "security",
    "xss": "security",
    "csrf": "security",
    "sanitiz": "security",
}

# Complexity multipliers for specific patterns
COMPLEXITY_SIGNALS: Dict[str, int] = {
    "refactor": 2,
    "migrate": 2,
    "optimiz": 1,
    "redesign": 3,
    "proof of concept": -1,
    "poc": -1,
    "mvp": 0,
    "prototype": -1,
    "simple": -1,
    "quick": -1,
    "hack": -1,
    "production": 2,
    "scalable": 2,
    "distributed": 3,
    "real-time": 2,
    "async": 1,
    "concurrent": 2,
    "multi-tenant": 3,
    "multi-region": 3,
    "internationalization": 2,
    "i18n": 2,
    "accessibility": 1,
    "a11y": 1,
    "audit": 2,
    "compliance": 2,
}


@dataclass
class AnalysisResult:
    """Result of complexity analysis."""
    word_count: int = 0
    sentence_count: int = 0
    technical_term_count: int = 0
    technical_terms_found: List[str] = field(default_factory=list)
    capabilities_required: List[str] = field(default_factory=list)
    complexity_score: float = 0.0
    complexity_level: TaskComplexity = TaskComplexity.MODERATE
    estimate: TaskEstimate = field(default_factory=TaskEstimate)
    signals: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)


class ComplexityAnalyzer:
    """
    Heuristic task complexity analyzer.

    Analyzes task descriptions to infer:
    - Complexity level (trivial → expert)
    - Required capabilities (backend, frontend, devops, etc.)
    - PERT-style effort estimates
    - Risk factors

    Usage:
        analyzer = ComplexityAnalyzer()
        result = analyzer.analyze("Build a real-time chat API with WebSocket support and Redis caching")
        print(result.complexity_level)  # TaskComplexity.COMPLEX
        print(result.capabilities_required)  # ['backend_api', 'caching']
    """

    def __init__(
        self,
        technical_keywords: Set[str] = None,
        capability_map: Dict[str, str] = None,
        complexity_signals: Dict[str, int] = None,
    ):
        self.technical_keywords = technical_keywords or TECHNICAL_KEYWORDS
        self.capability_map = capability_map or CAPABILITY_KEYWORDS
        self.complexity_signals = complexity_signals or COMPLEXITY_SIGNALS

    def analyze(self, description: str, title: str = "") -> AnalysisResult:
        """Analyze a task description for complexity."""
        text = f"{title} {description}".lower().strip()
        result = AnalysisResult()

        # Basic metrics
        words = text.split()
        result.word_count = len(words)
        sentences = re.split(r'[.!?]+', text)
        result.sentence_count = len([s for s in sentences if s.strip()])

        # Technical term detection
        result.technical_terms_found = [
            kw for kw in self.technical_keywords if kw in text
        ]
        result.technical_term_count = len(result.technical_terms_found)

        # Capability inference
        caps = set()
        for keyword, capability in self.capability_map.items():
            if keyword in text:
                caps.add(capability)
        result.capabilities_required = sorted(caps)

        # Complexity signals
        for signal, modifier in self.complexity_signals.items():
            if signal in text:
                result.signals.append(signal)
                result.complexity_score += modifier

        # Calculate base complexity score
        base_score = 0.0

        # Word count contributes (longer descriptions → more complex)
        if result.word_count > 100:
            base_score += 2
        elif result.word_count > 50:
            base_score += 1
        elif result.word_count < 15:
            base_score -= 1

        # Technical terms contribute
        base_score += min(result.technical_term_count * 0.5, 3)

        # Capability breadth contributes
        cap_count = len(result.capabilities_required)
        if cap_count > 4:
            base_score += 3
            result.risk_factors.append("multi-domain task spanning many capabilities")
        elif cap_count > 2:
            base_score += 1.5
        elif cap_count == 0:
            base_score -= 0.5
            result.risk_factors.append("no specific capabilities detected")

        result.complexity_score += base_score

        # Map score to complexity level
        result.complexity_level = self._score_to_level(result.complexity_score)

        # Generate PERT estimate based on complexity
        result.estimate = self._estimate_from_level(result.complexity_level)

        return result

    def estimate_from_text(self, description: str, title: str = "") -> TaskEstimate:
        """Quick shortcut: get just the PERT estimate from description text."""
        result = self.analyze(description, title)
        return result.estimate

    def _score_to_level(self, score: float) -> TaskComplexity:
        if score <= -1:
            return TaskComplexity.TRIVIAL
        elif score <= 2:
            return TaskComplexity.SIMPLE
        elif score <= 4:
            return TaskComplexity.MODERATE
        elif score <= 7:
            return TaskComplexity.COMPLEX
        return TaskComplexity.EXPERT

    def _estimate_from_level(self, level: TaskComplexity) -> TaskEstimate:
        """Generate PERT estimates based on complexity level."""
        estimates = {
            TaskComplexity.TRIVIAL: TaskEstimate(
                optimistic_hours=0.05, likely_hours=0.15, pessimistic_hours=0.5,
                confidence=0.8,
            ),
            TaskComplexity.SIMPLE: TaskEstimate(
                optimistic_hours=0.25, likely_hours=1.0, pessimistic_hours=2.0,
                confidence=0.7,
            ),
            TaskComplexity.MODERATE: TaskEstimate(
                optimistic_hours=1.0, likely_hours=3.0, pessimistic_hours=6.0,
                confidence=0.6,
            ),
            TaskComplexity.COMPLEX: TaskEstimate(
                optimistic_hours=3.0, likely_hours=8.0, pessimistic_hours=16.0,
                confidence=0.4,
            ),
            TaskComplexity.EXPERT: TaskEstimate(
                optimistic_hours=8.0, likely_hours=16.0, pessimistic_hours=40.0,
                confidence=0.3,
            ),
        }
        return estimates[level]

    def batch_analyze(self, descriptions: List[str]) -> List[AnalysisResult]:
        """Analyze multiple task descriptions."""
        return [self.analyze(d) for d in descriptions]
