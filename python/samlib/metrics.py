"""Metrics and monitoring for Python SAMLib.

This module provides tools to monitor agent and channel performance.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional
from collections import defaultdict

@dataclass
class AgentMetrics:
    """Metrics for a single agent."""
    messages_processed: int = 0
    messages_sent: int = 0
    processing_time: float = 0.0
    last_processed: Optional[float] = None
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average message processing time."""
        if self.messages_processed == 0:
            return 0.0
        return self.processing_time / self.messages_processed

class MetricsCollector:
    """Collects and reports metrics for the agent system."""
    
    def __init__(self):
        self._metrics: Dict[str, AgentMetrics] = defaultdict(AgentMetrics)
        
    def record_processed(self, agent_name: str, processing_time: float) -> None:
        """Record a processed message."""
        metrics = self._metrics[agent_name]
        metrics.messages_processed += 1
        metrics.processing_time += processing_time
        metrics.last_processed = time.time()
        
    def record_sent(self, agent_name: str) -> None:
        """Record a sent message."""
        self._metrics[agent_name].messages_sent += 1
        
    def get_metrics(self, agent_name: str) -> AgentMetrics:
        """Get metrics for a specific agent."""
        return self._metrics[agent_name]
        
    def report(self) -> str:
        """Generate a human-readable metrics report."""
        lines = ["Agent System Metrics:"]
        lines.append("-" * 50)
        
        for name, metrics in sorted(self._metrics.items()):
            lines.append(f"Agent: {name}")
            lines.append(f"  Messages Processed: {metrics.messages_processed}")
            lines.append(f"  Messages Sent: {metrics.messages_sent}")
            lines.append(f"  Avg Processing Time: {metrics.average_processing_time:.6f}s")
            if metrics.last_processed:
                last = time.strftime("%H:%M:%S", time.localtime(metrics.last_processed))
                lines.append(f"  Last Processed: {last}")
            lines.append("-" * 30)
            
        return "\n".join(lines)

# Global metrics collector instance
collector = MetricsCollector()

async def with_metrics(agent_name: str, coro):
    """Decorator to track metrics for an agent task."""
    start = time.time()
    try:
        result = await coro
        collector.record_processed(agent_name, time.time() - start)
        return result
    except Exception as e:
        # Still record the processing time even if there's an error
        collector.record_processed(agent_name, time.time() - start)
        raise
