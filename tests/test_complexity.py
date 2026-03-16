"""
Tests for complexity analyzer.
"""

import pytest
from orchestrator.tasks.complexity import ComplexityAnalyzer, AnalysisResult
from orchestrator.tasks.entity import TaskComplexity


@pytest.fixture
def analyzer():
    return ComplexityAnalyzer()


class TestComplexityAnalyzer:

    def test_trivial_task(self, analyzer):
        result = analyzer.analyze("Fix typo in README")
        assert result.complexity_level == TaskComplexity.TRIVIAL
        assert result.word_count < 15

    def test_simple_task(self, analyzer):
        result = analyzer.analyze("Add a new API endpoint to fetch user profiles with pagination")
        assert result.complexity_level in (TaskComplexity.SIMPLE, TaskComplexity.MODERATE)
        assert "backend_api" in result.capabilities_required

    def test_complex_task(self, analyzer):
        result = analyzer.analyze(
            "Migrate the authentication system from JWT to OAuth2 with database schema changes, "
            "Redis session caching, API endpoint updates, and comprehensive integration tests"
        )
        assert result.complexity_level in (TaskComplexity.COMPLEX, TaskComplexity.EXPERT)
        assert len(result.capabilities_required) >= 3
        assert "authentication" in result.capabilities_required
        assert "database" in result.capabilities_required or "caching" in result.capabilities_required

    def test_expert_task(self, analyzer):
        result = analyzer.analyze(
            "Redesign the distributed microservice architecture for multi-region deployment "
            "with real-time WebSocket streaming, Kubernetes orchestration, Terraform infrastructure, "
            "Redis caching layer, PostgreSQL sharding, and production-grade observability with "
            "distributed tracing, metrics aggregation, and security audit compliance"
        )
        assert result.complexity_level == TaskComplexity.EXPERT
        assert len(result.technical_terms_found) >= 5
        assert "multi-region" in result.signals

    def test_capability_detection(self, analyzer):
        result = analyzer.analyze(
            "Build a React frontend component with CSS styling and Vue.js integration"
        )
        assert "frontend" in result.capabilities_required

    def test_multiple_capabilities(self, analyzer):
        result = analyzer.analyze(
            "Deploy the API with Docker, set up Nginx load balancing, and configure PostgreSQL database"
        )
        assert "backend_api" in result.capabilities_required
        assert "devops" in result.capabilities_required
        assert "database" in result.capabilities_required

    def test_complexity_signals(self, analyzer):
        result = analyzer.analyze("Refactor the production database migration for scalability")
        assert "refactor" in result.signals
        assert "production" in result.signals
        assert result.complexity_score > 3

    def test_quick_hack_reduces_score(self, analyzer):
        result = analyzer.analyze("Quick hack to fix the simple prototype")
        assert result.complexity_score <= 1  # quick + simple + hack all reduce

    def test_risk_factors(self, analyzer):
        result = analyzer.analyze(
            "Build a distributed system with REST API, React frontend, "
            "PostgreSQL database, Redis caching, and Docker deployment"
        )
        assert len(result.risk_factors) > 0
        assert any("multi-domain" in r for r in result.risk_factors)

    def test_estimate_generation(self, analyzer):
        result = analyzer.analyze("Build a REST API endpoint")
        est = result.estimate
        assert est.optimistic_hours > 0
        assert est.likely_hours > est.optimistic_hours
        assert est.pessimistic_hours > est.likely_hours
        assert 0 < est.confidence <= 1.0

    def test_estimate_from_text(self, analyzer):
        est = analyzer.estimate_from_text("Add a button to the UI")
        assert est.expected_hours > 0

    def test_empty_description(self, analyzer):
        result = analyzer.analyze("")
        assert result.word_count == 0
        assert result.technical_term_count == 0

    def test_batch_analyze(self, analyzer):
        results = analyzer.batch_analyze([
            "Fix typo",
            "Build real-time WebSocket chat with Redis and database",
        ])
        assert len(results) == 2
        assert results[0].complexity_level in (TaskComplexity.TRIVIAL, TaskComplexity.SIMPLE)
        assert results[1].complexity_level in (TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.EXPERT)

    def test_title_contributes(self, analyzer):
        with_title = analyzer.analyze(
            description="implement endpoint",
            title="Distributed Kubernetes microservice deployment"
        )
        without_title = analyzer.analyze("implement endpoint")
        assert with_title.complexity_score > without_title.complexity_score
