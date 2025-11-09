"""
Monitoring and observability for production deployment
Metrics, health checks, and system monitoring
"""

import time
import psutil
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Collect and aggregate metrics for monitoring
    Thread-safe metrics collection
    """

    def __init__(self, retention_minutes: int = 60):
        self.retention = timedelta(minutes=retention_minutes)
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()

    def record_counter(self, name: str, value: int = 1, tags: Dict[str, str] = None):
        """Increment a counter metric"""
        with self._lock:
            key = self._build_key(name, tags)
            self._counters[key] += value

    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric"""
        with self._lock:
            key = self._build_key(name, tags)
            self._gauges[key] = value

    def record_histogram(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a histogram value"""
        with self._lock:
            key = self._build_key(name, tags)
            point = MetricPoint(
                timestamp=datetime.utcnow(),
                value=value,
                tags=tags or {}
            )
            self._metrics[key].append(point)
            self._cleanup_old_metrics(key)

    def get_counter(self, name: str, tags: Dict[str, str] = None) -> int:
        """Get counter value"""
        with self._lock:
            key = self._build_key(name, tags)
            return self._counters.get(key, 0)

    def get_gauge(self, name: str, tags: Dict[str, str] = None) -> float:
        """Get gauge value"""
        with self._lock:
            key = self._build_key(name, tags)
            return self._gauges.get(key, 0.0)

    def get_histogram_stats(self, name: str, tags: Dict[str, str] = None) -> Dict[str, float]:
        """Get histogram statistics (min, max, mean, p50, p95, p99)"""
        with self._lock:
            key = self._build_key(name, tags)
            points = list(self._metrics.get(key, []))

        if not points:
            return {}

        values = sorted([p.value for p in points])
        n = len(values)

        return {
            'count': n,
            'min': values[0],
            'max': values[-1],
            'mean': sum(values) / n,
            'p50': values[int(n * 0.5)],
            'p95': values[int(n * 0.95)] if n >= 20 else values[-1],
            'p99': values[int(n * 0.99)] if n >= 100 else values[-1]
        }

    def _build_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """Build metric key with tags"""
        if not tags:
            return name
        tag_str = ','.join(f'{k}={v}' for k, v in sorted(tags.items()))
        return f'{name}{{{tag_str}}}'

    def _cleanup_old_metrics(self, key: str):
        """Remove metrics older than retention period"""
        cutoff = datetime.utcnow() - self.retention
        metrics = self._metrics[key]

        while metrics and metrics[0].timestamp < cutoff:
            metrics.popleft()

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all current metrics"""
        with self._lock:
            return {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': {
                    key: self.get_histogram_stats(key)
                    for key in self._metrics.keys()
                }
            }


class SystemMonitor:
    """
    Monitor system resources (CPU, memory, disk)
    """

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get current system metrics"""
        return {
            'cpu': {
                'percent': psutil.cpu_percent(interval=0.1),
                'count': psutil.cpu_count(),
                'per_cpu': psutil.cpu_percent(interval=0.1, percpu=True)
            },
            'memory': {
                'percent': psutil.virtual_memory().percent,
                'total_mb': psutil.virtual_memory().total / (1024 * 1024),
                'available_mb': psutil.virtual_memory().available / (1024 * 1024),
                'used_mb': psutil.virtual_memory().used / (1024 * 1024)
            },
            'disk': {
                'percent': psutil.disk_usage('/').percent,
                'total_gb': psutil.disk_usage('/').total / (1024 * 1024 * 1024),
                'free_gb': psutil.disk_usage('/').free / (1024 * 1024 * 1024)
            }
        }

    @staticmethod
    def check_system_health() -> Dict[str, Any]:
        """Check if system is healthy"""
        metrics = SystemMonitor.get_system_metrics()

        health_status = {
            'healthy': True,
            'warnings': [],
            'critical': []
        }

        # Check CPU
        if metrics['cpu']['percent'] > 90:
            health_status['critical'].append('CPU usage above 90%')
            health_status['healthy'] = False
        elif metrics['cpu']['percent'] > 75:
            health_status['warnings'].append('CPU usage above 75%')

        # Check Memory
        if metrics['memory']['percent'] > 90:
            health_status['critical'].append('Memory usage above 90%')
            health_status['healthy'] = False
        elif metrics['memory']['percent'] > 80:
            health_status['warnings'].append('Memory usage above 80%')

        # Check Disk
        if metrics['disk']['percent'] > 90:
            health_status['critical'].append('Disk usage above 90%')
            health_status['healthy'] = False
        elif metrics['disk']['percent'] > 80:
            health_status['warnings'].append('Disk usage above 80%')

        return health_status


class HealthCheck:
    """
    Comprehensive health check for all system components
    """

    def __init__(self):
        self.checks: Dict[str, callable] = {}

    def register_check(self, name: str, check_func: callable):
        """Register a health check function"""
        self.checks[name] = check_func

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {
            'healthy': True,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }

        for name, check_func in self.checks.items():
            try:
                check_result = check_func()
                results['checks'][name] = {
                    'status': 'healthy' if check_result.get('healthy', True) else 'unhealthy',
                    'details': check_result
                }

                if not check_result.get('healthy', True):
                    results['healthy'] = False

            except Exception as e:
                results['checks'][name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                results['healthy'] = False

        return results


class PerformanceTracker:
    """
    Track performance metrics for operations
    """

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector

    def track_compression(self, duration_ms: float, strategy: str, tokens_saved: int):
        """Track compression operation metrics"""
        self.metrics.record_histogram('compression.duration_ms', duration_ms, {'strategy': strategy})
        self.metrics.record_counter('compression.count', 1, {'strategy': strategy})
        self.metrics.record_counter('compression.tokens_saved', tokens_saved)

    def track_tale_optimization(self, duration_ms: float, strategy: str, within_budget: bool):
        """Track TALE optimization metrics"""
        self.metrics.record_histogram('tale.duration_ms', duration_ms, {'strategy': strategy})
        self.metrics.record_counter('tale.count', 1, {'strategy': strategy})
        self.metrics.record_counter('tale.budget_compliance', 1 if within_budget else 0)

    def track_api_request(self, endpoint: str, method: str, status_code: int, duration_ms: float):
        """Track API request metrics"""
        tags = {'endpoint': endpoint, 'method': method, 'status': str(status_code)}
        self.metrics.record_histogram('api.request.duration_ms', duration_ms, tags)
        self.metrics.record_counter('api.request.count', 1, tags)

    def track_cache_hit(self, cache_type: str, hit: bool):
        """Track cache hit/miss"""
        self.metrics.record_counter(
            'cache.hits' if hit else 'cache.misses',
            1,
            {'cache_type': cache_type}
        )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        return {
            'compression': {
                'total_count': self.metrics.get_counter('compression.count'),
                'tokens_saved': self.metrics.get_counter('compression.tokens_saved'),
                'latency': self.metrics.get_histogram_stats('compression.duration_ms')
            },
            'tale': {
                'total_count': self.metrics.get_counter('tale.count'),
                'compliance_rate': self._calculate_rate('tale.budget_compliance', 'tale.count'),
                'latency': self.metrics.get_histogram_stats('tale.duration_ms')
            },
            'api': {
                'total_requests': self.metrics.get_counter('api.request.count'),
                'latency': self.metrics.get_histogram_stats('api.request.duration_ms')
            },
            'cache': {
                'hit_rate': self._calculate_cache_hit_rate()
            }
        }

    def _calculate_rate(self, numerator_metric: str, denominator_metric: str) -> float:
        """Calculate rate between two metrics"""
        numerator = self.metrics.get_counter(numerator_metric)
        denominator = self.metrics.get_counter(denominator_metric)
        return (numerator / denominator * 100) if denominator > 0 else 0.0

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        hits = self.metrics.get_counter('cache.hits')
        misses = self.metrics.get_counter('cache.misses')
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0


# Global instances
_metrics_collector: Optional[MetricsCollector] = None
_performance_tracker: Optional[PerformanceTracker] = None
_health_check: Optional[HealthCheck] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_performance_tracker() -> PerformanceTracker:
    """Get global performance tracker instance"""
    global _performance_tracker
    if _performance_tracker is None:
        _performance_tracker = PerformanceTracker(get_metrics_collector())
    return _performance_tracker


def get_health_check() -> HealthCheck:
    """Get global health check instance"""
    global _health_check
    if _health_check is None:
        _health_check = HealthCheck()
        _setup_default_health_checks(_health_check)
    return _health_check


def _setup_default_health_checks(health_check: HealthCheck):
    """Setup default health checks"""

    def check_system_resources():
        return SystemMonitor.check_system_health()

    def check_metrics_collector():
        metrics = get_metrics_collector()
        return {
            'healthy': True,
            'metrics_count': len(metrics.get_all_metrics())
        }

    health_check.register_check('system', check_system_resources)
    health_check.register_check('metrics', check_metrics_collector)


if __name__ == "__main__":
    # Test monitoring
    print("Testing monitoring system...\n")

    # Test metrics collection
    metrics = get_metrics_collector()
    metrics.record_counter('test.requests', 100)
    metrics.record_gauge('test.active_users', 42)
    for i in range(100):
        metrics.record_histogram('test.latency', 10 + i * 0.5)

    print("Metrics collected:")
    print(f"  Counter: {metrics.get_counter('test.requests')}")
    print(f"  Gauge: {metrics.get_gauge('test.active_users')}")
    print(f"  Histogram stats: {metrics.get_histogram_stats('test.latency')}")

    # Test system monitoring
    print("\nSystem metrics:")
    system_metrics = SystemMonitor.get_system_metrics()
    print(f"  CPU: {system_metrics['cpu']['percent']}%")
    print(f"  Memory: {system_metrics['memory']['percent']}%")
    print(f"  Disk: {system_metrics['disk']['percent']}%")

    # Test health checks
    print("\nHealth check:")
    health = get_health_check()
    health_status = health.run_all_checks()
    print(f"  Overall: {'✓ HEALTHY' if health_status['healthy'] else '✗ UNHEALTHY'}")
    for check_name, check_result in health_status['checks'].items():
        print(f"  {check_name}: {check_result['status']}")

    print("\n✓ Monitoring system test completed")
