"""
Health scoring for tasks and sessions.

Monitors execution health based on elapsed time vs estimates,
failure patterns, and system resource usage.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from orchestrator.tasks.entity import TaskEntity, TaskEstimate


@dataclass
class HealthIndicator:
    """A single health indicator with score and reason."""
    name: str
    score: float           # 0.0 to 1.0
    reason: str
    severity: str = "info"  # info, warning, critical


@dataclass
class HealthReport:
    """Complete health report for a task or system."""
    overall_score: float
    indicators: List[HealthIndicator] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def status(self) -> str:
        if self.overall_score >= 0.8:
            return "healthy"
        elif self.overall_score >= 0.5:
            return "warning"
        return "critical"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "status": self.status,
            "indicators": [
                {"name": i.name, "score": i.score, "reason": i.reason, "severity": i.severity}
                for i in self.indicators
            ],
            "recommendations": self.recommendations,
            "timestamp": self.timestamp,
        }


class HealthScorer:
    """
    Calculates health scores for tasks and systems.

    Evaluates multiple dimensions:
    - Time health: elapsed vs estimated time
    - State health: based on current status
    - Dependency health: are dependencies satisfied?
    - Failure health: recent failure patterns

    Usage:
        scorer = HealthScorer()
        task = TaskEntity(title="Build API")
        task.start()
        report = scorer.score_task(task)
        print(report.status)  # "healthy"
    """

    # Time ratio thresholds
    ON_TRACK_THRESHOLD = 0.7
    AT_RISK_THRESHOLD = 0.9
    OVERDUE_THRESHOLD = 1.0

    def score_task(self, task: TaskEntity) -> HealthReport:
        """Generate health report for a single task."""
        indicators = []
        recommendations = []

        # 1. State-based health
        state_score, state_reason = self._score_state(task)
        indicators.append(HealthIndicator("state", state_score, state_reason))

        # 2. Time-based health (if in progress with estimate)
        time_score = 1.0
        if task.status == "in_progress" and task.started_at and task.estimate.expected_hours > 0:
            time_score, time_reason, time_severity = self._score_time(task)
            indicators.append(HealthIndicator("time", time_score, time_reason, time_severity))
            if time_score < self.AT_RISK_THRESHOLD:
                recommendations.append(
                    f"Task may exceed estimate ({task.estimate.expected_hours:.1f}h). "
                    f"Consider scope reduction or adding resources."
                )

        # 3. Dependency health
        if task.dependencies:
            dep_score, dep_reason = self._score_dependencies(task)
            indicators.append(HealthIndicator("dependencies", dep_score, dep_reason))
            if dep_score < 1.0:
                recommendations.append("Check blocked dependencies before proceeding.")

        # 4. Hierarchy health (if has children)
        if task.children:
            hier_score, hier_reason = self._score_hierarchy(task)
            indicators.append(HealthIndicator("hierarchy", hier_score, hier_reason))

        # Calculate overall score (weighted average)
        if not indicators:
            overall = 0.8
        else:
            weights = {"state": 0.3, "time": 0.3, "dependencies": 0.2, "hierarchy": 0.2}
            total_weight = sum(weights.get(i.name, 0.1) for i in indicators)
            overall = sum(
                i.score * weights.get(i.name, 0.1) for i in indicators
            ) / total_weight if total_weight > 0 else 0.8

        return HealthReport(
            overall_score=min(max(overall, 0.0), 1.0),
            indicators=indicators,
            recommendations=recommendations,
        )

    def score_system(self, tasks: List[TaskEntity]) -> HealthReport:
        """Generate health report for a system of tasks."""
        if not tasks:
            return HealthReport(overall_score=1.0, recommendations=[])

        indicators = []
        recommendations = []

        # Score each task
        task_scores = []
        failed_count = 0
        blocked_count = 0
        in_progress_count = 0

        for task in tasks:
            report = self.score_task(task)
            task_scores.append(report.overall_score)

            if task.status == "failed":
                failed_count += 1
            elif task.status == "blocked":
                blocked_count += 1
            elif task.status == "in_progress":
                in_progress_count += 1

        # System-level indicators
        avg_score = sum(task_scores) / len(task_scores) if task_scores else 1.0
        indicators.append(HealthIndicator(
            "task_health", avg_score,
            f"{len(tasks)} tasks, avg score {avg_score:.2f}"
        ))

        # Failure rate
        failure_rate = failed_count / len(tasks) if tasks else 0
        fail_score = max(0, 1.0 - failure_rate * 2)  # 50% failure → 0.0
        indicators.append(HealthIndicator(
            "failure_rate", fail_score,
            f"{failed_count}/{len(tasks)} failed ({failure_rate:.0%})",
            "critical" if failure_rate > 0.3 else "warning" if failure_rate > 0.1 else "info",
        ))
        if failure_rate > 0.2:
            recommendations.append(
                f"High failure rate ({failure_rate:.0%}). Review error patterns."
            )

        # Blockage rate
        block_rate = blocked_count / len(tasks) if tasks else 0
        block_score = max(0, 1.0 - block_rate * 3)
        indicators.append(HealthIndicator(
            "blockage", block_score,
            f"{blocked_count}/{len(tasks)} blocked",
            "warning" if block_rate > 0.2 else "info",
        ))
        if block_rate > 0.1:
            recommendations.append("Some tasks are blocked. Check dependency chains.")

        # Overall
        weights = {"task_health": 0.4, "failure_rate": 0.35, "blockage": 0.25}
        overall = sum(
            i.score * weights.get(i.name, 0.1) for i in indicators
        ) / sum(weights.get(i.name, 0.1) for i in indicators)

        return HealthReport(
            overall_score=min(max(overall, 0.0), 1.0),
            indicators=indicators,
            recommendations=recommendations,
        )

    def _score_state(self, task: TaskEntity) -> tuple:
        state_scores = {
            "pending": (0.8, "Waiting to start"),
            "ready": (0.85, "Ready to begin"),
            "in_progress": (0.9, "Actively executing"),
            "blocked": (0.3, "Blocked - waiting on dependencies"),
            "paused": (0.5, "Paused - may need attention"),
            "completed": (1.0, "Successfully completed"),
            "failed": (0.0, "Failed - needs intervention"),
            "cancelled": (0.5, "Cancelled"),
        }
        score, reason = state_scores.get(task.status, (0.5, f"Unknown state: {task.status}"))
        return score, reason

    def _score_time(self, task: TaskEntity) -> tuple:
        elapsed = (datetime.now(timezone.utc) - task.started_at).total_seconds() / 3600
        estimated = task.estimate.expected_hours
        ratio = elapsed / estimated if estimated > 0 else 0

        if ratio > self.OVERDUE_THRESHOLD:
            overdue_pct = (ratio - 1) * 100
            return 0.2, f"Overdue by {overdue_pct:.0f}%", "critical"
        elif ratio > self.AT_RISK_THRESHOLD:
            return 0.5, f"At risk ({ratio:.0%} of estimate used)", "warning"
        elif ratio > self.ON_TRACK_THRESHOLD:
            return 0.8, f"On track ({ratio:.0%} of estimate used)", "info"
        else:
            return 0.95, f"Ahead of schedule ({ratio:.0%} of estimate)", "info"

    def _score_dependencies(self, task: TaskEntity) -> tuple:
        deps = task.dependencies
        required = [d for d in deps if d.is_required]
        if not required:
            return 1.0, "No blocking dependencies"
        # Simplified: if task is in_progress, deps must be satisfied
        if task.status == "in_progress":
            return 0.9, f"{len(required)} dependencies satisfied"
        return 0.7, f"{len(required)} dependencies pending"

    def _score_hierarchy(self, task: TaskEntity) -> tuple:
        total = len(task.children)
        if total == 0:
            return 1.0, "No subtasks"

        completed = sum(1 for c in task.children if c.status == "completed")
        failed = sum(1 for c in task.children if c.status == "failed")
        ratio = completed / total if total > 0 else 0

        if failed > 0:
            return 0.3, f"{failed}/{total} subtasks failed", "critical"
        elif ratio == 1.0:
            return 1.0, "All subtasks complete"
        elif ratio > 0.5:
            return 0.7, f"{completed}/{total} subtasks complete"
        else:
            return 0.5, f"{completed}/{total} subtasks complete"
