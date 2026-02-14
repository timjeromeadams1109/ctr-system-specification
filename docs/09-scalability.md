# Section 9 — Scalability and Performance

## 9.1 Compute Load Projections

### 9.1.1 Per-Project Resource Requirements

```yaml
project_sizing:
  small_project:
    description: "3-story, 12 units, ~50 shear walls"
    drawings: 10-15
    estimated_rod_runs: 20-30
    compute_requirements:
      cpu_cores: 2
      memory_gb: 4
      processing_time_minutes: 5-10
      storage_gb: 0.5

  medium_project:
    description: "5-story, 40 units, ~150 shear walls"
    drawings: 30-50
    estimated_rod_runs: 60-100
    compute_requirements:
      cpu_cores: 4
      memory_gb: 8
      processing_time_minutes: 15-30
      storage_gb: 2

  large_project:
    description: "7-story, 100 units, ~300 shear walls"
    drawings: 80-120
    estimated_rod_runs: 150-250
    compute_requirements:
      cpu_cores: 8
      memory_gb: 16
      processing_time_minutes: 45-90
      storage_gb: 5

  complex_project:
    description: "7-story podium, mixed use, irregular geometry"
    drawings: 150+
    estimated_rod_runs: 300+
    compute_requirements:
      cpu_cores: 16
      memory_gb: 32
      processing_time_minutes: 120-180
      storage_gb: 10
```

### 9.1.2 Agent-Specific Resource Profiles

| Agent | CPU Intensity | Memory Profile | I/O Pattern | GPU Benefit |
|-------|---------------|----------------|-------------|-------------|
| Drawing Ingestion | HIGH | HIGH (rasterization) | Burst read | YES (PDF) |
| Geometry Normalization | MEDIUM | MEDIUM | Sequential | NO |
| Shear Wall Detection | HIGH | HIGH | Random access | YES (ML) |
| Load Path Analysis | HIGH | MEDIUM | Sequential | NO |
| Rod Design | MEDIUM | LOW | Sequential | NO |
| Shrinkage Analysis | LOW | LOW | Sequential | NO |
| Clash Detection | HIGH | HIGH | Random access | YES (parallel) |
| Structural Audit | HIGH | MEDIUM | Sequential | NO |
| Report Generation | MEDIUM | HIGH (PDF gen) | Burst write | NO |

---

## 9.2 Memory Management Strategy

### 9.2.1 Memory Budget Allocation

```python
from dataclasses import dataclass
from typing import Dict, Optional
import psutil

@dataclass
class MemoryBudget:
    """Memory allocation for project processing."""
    total_available_gb: float
    drawing_cache_gb: float
    geometry_index_gb: float
    calculation_workspace_gb: float
    report_generation_gb: float
    system_reserve_gb: float

    @classmethod
    def from_system(cls, utilization_target: float = 0.8) -> 'MemoryBudget':
        """Create budget based on available system memory."""
        total = psutil.virtual_memory().total / (1024**3)
        available = total * utilization_target

        return cls(
            total_available_gb=available,
            drawing_cache_gb=available * 0.30,
            geometry_index_gb=available * 0.25,
            calculation_workspace_gb=available * 0.25,
            report_generation_gb=available * 0.15,
            system_reserve_gb=available * 0.05
        )


class MemoryManager:
    """Manage memory allocation across processing stages."""

    def __init__(self, budget: MemoryBudget):
        self.budget = budget
        self.allocations: Dict[str, float] = {}
        self.peak_usage: Dict[str, float] = {}

    def request_allocation(
        self,
        component: str,
        requested_gb: float
    ) -> bool:
        """Request memory allocation for component."""
        category = self._get_category(component)
        category_budget = getattr(self.budget, f"{category}_gb")
        current_usage = sum(
            v for k, v in self.allocations.items()
            if self._get_category(k) == category
        )

        if current_usage + requested_gb <= category_budget:
            self.allocations[component] = requested_gb
            return True

        return False

    def release_allocation(self, component: str):
        """Release memory allocation."""
        if component in self.allocations:
            del self.allocations[component]

    def get_memory_pressure(self) -> Dict[str, float]:
        """Get memory pressure by category."""
        pressure = {}
        for category in ['drawing_cache', 'geometry_index', 'calculation_workspace']:
            budget = getattr(self.budget, f"{category}_gb")
            used = sum(
                v for k, v in self.allocations.items()
                if self._get_category(k) == category
            )
            pressure[category] = used / budget if budget > 0 else 0

        return pressure
```

### 9.2.2 Drawing Cache Strategy

```python
from collections import OrderedDict
from typing import Any
import hashlib

class DrawingCache:
    """LRU cache for parsed drawing data."""

    def __init__(self, max_size_gb: float, eviction_threshold: float = 0.9):
        self.max_size_bytes = int(max_size_gb * 1024**3)
        self.eviction_threshold = eviction_threshold
        self.cache: OrderedDict[str, Dict] = OrderedDict()
        self.sizes: Dict[str, int] = {}
        self.current_size = 0
        self.hits = 0
        self.misses = 0

    def get(self, drawing_id: str) -> Optional[Dict]:
        """Get cached drawing data."""
        if drawing_id in self.cache:
            self.cache.move_to_end(drawing_id)
            self.hits += 1
            return self.cache[drawing_id]

        self.misses += 1
        return None

    def put(self, drawing_id: str, data: Dict, size_bytes: int):
        """Cache drawing data with LRU eviction."""
        # Evict if necessary
        while (self.current_size + size_bytes >
               self.max_size_bytes * self.eviction_threshold):
            if not self.cache:
                break
            oldest_id, _ = self.cache.popitem(last=False)
            self.current_size -= self.sizes.pop(oldest_id)

        self.cache[drawing_id] = data
        self.sizes[drawing_id] = size_bytes
        self.current_size += size_bytes

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0
```

---

## 9.3 Horizontal Scaling Architecture

### 9.3.1 Worker Pool Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           LOAD BALANCER (ALB)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐             ┌───────────────┐             ┌───────────────┐
│   API Server  │             │   API Server  │             │   API Server  │
│   (Stateless) │             │   (Stateless) │             │   (Stateless) │
└───────┬───────┘             └───────┬───────┘             └───────┬───────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           REDIS (Task Queue)                                 │
│                                                                              │
│  Queues: [drawing_parse] [design_calc] [clash_detect] [report_gen]          │
└─────────────────────────────────────────────────────────────────────────────┘
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────┐             ┌───────────────┐             ┌───────────────┐
│  Worker Pool  │             │  Worker Pool  │             │  Worker Pool  │
│   (Drawing)   │             │    (Design)   │             │   (Report)    │
│               │             │               │             │               │
│  Instances:   │             │  Instances:   │             │  Instances:   │
│    2-10       │             │    4-20       │             │    2-8        │
└───────────────┘             └───────────────┘             └───────────────┘
```

### 9.3.2 Auto-Scaling Configuration

```python
from dataclasses import dataclass
from enum import Enum

class ScalingMetric(Enum):
    CPU_UTILIZATION = "cpu"
    MEMORY_UTILIZATION = "memory"
    QUEUE_DEPTH = "queue"
    PROCESSING_TIME = "latency"

@dataclass
class ScalingPolicy:
    """Auto-scaling policy configuration."""
    worker_type: str
    min_instances: int
    max_instances: int
    scale_up_threshold: float
    scale_down_threshold: float
    scale_up_increment: int
    scale_down_increment: int
    cooldown_seconds: int
    metric: ScalingMetric

SCALING_POLICIES = {
    'drawing_workers': ScalingPolicy(
        worker_type='drawing',
        min_instances=2,
        max_instances=10,
        scale_up_threshold=0.7,    # 70% CPU
        scale_down_threshold=0.3,  # 30% CPU
        scale_up_increment=2,
        scale_down_increment=1,
        cooldown_seconds=300,
        metric=ScalingMetric.CPU_UTILIZATION
    ),
    'design_workers': ScalingPolicy(
        worker_type='design',
        min_instances=4,
        max_instances=20,
        scale_up_threshold=100,    # Queue depth
        scale_down_threshold=10,
        scale_up_increment=4,
        scale_down_increment=2,
        cooldown_seconds=180,
        metric=ScalingMetric.QUEUE_DEPTH
    ),
    'clash_workers': ScalingPolicy(
        worker_type='clash',
        min_instances=2,
        max_instances=8,
        scale_up_threshold=0.8,    # 80% memory
        scale_down_threshold=0.4,
        scale_up_increment=2,
        scale_down_increment=1,
        cooldown_seconds=300,
        metric=ScalingMetric.MEMORY_UTILIZATION
    )
}
```

---

## 9.4 Database Optimization

### 9.4.1 Partitioning Strategy

```sql
-- Partition rod_runs by project for isolation and performance
CREATE TABLE rod_runs (
    rod_run_id VARCHAR(50),
    project_id UUID NOT NULL,
    direction VARCHAR(5),
    grid_location VARCHAR(20),
    rod_diameter_in DECIMAL(5,3),
    total_length_ft DECIMAL(6,2),
    max_tension_lb DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (project_id, rod_run_id)
) PARTITION BY HASH (project_id);

-- Create partitions
CREATE TABLE rod_runs_p0 PARTITION OF rod_runs
    FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE rod_runs_p1 PARTITION OF rod_runs
    FOR VALUES WITH (MODULUS 8, REMAINDER 1);
-- ... through p7

-- Partition audit_events by time for efficient archival
CREATE TABLE audit_events (
    event_id VARCHAR(50),
    project_id UUID,
    event_type VARCHAR(50),
    timestamp TIMESTAMPTZ NOT NULL,
    actor_id VARCHAR(100),
    event_data JSONB,
    PRIMARY KEY (timestamp, event_id)
) PARTITION BY RANGE (timestamp);

-- Monthly partitions
CREATE TABLE audit_events_2025_01 PARTITION OF audit_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE audit_events_2025_02 PARTITION OF audit_events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

### 9.4.2 Index Strategy

```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_rod_runs_project_direction
    ON rod_runs(project_id, direction);

CREATE INDEX idx_shear_walls_project_level
    ON shear_walls(project_id, level);

-- Spatial index for geometry queries
CREATE INDEX idx_shear_walls_geometry
    ON shear_walls USING GIST(geometry);

-- Partial indexes for active projects
CREATE INDEX idx_projects_active
    ON projects(organization_id, updated_at DESC)
    WHERE status NOT IN ('ARCHIVED', 'DELETED');

-- BRIN index for time-series data
CREATE INDEX idx_audit_events_timestamp
    ON audit_events USING BRIN(timestamp);

-- Expression index for case-insensitive search
CREATE INDEX idx_projects_name_lower
    ON projects(LOWER(name));
```

### 9.4.3 Connection Pooling

```python
from dataclasses import dataclass

@dataclass
class ConnectionPoolConfig:
    """Database connection pool configuration."""
    min_connections: int = 5
    max_connections: int = 20
    max_overflow: int = 10
    pool_timeout_seconds: int = 30
    pool_recycle_seconds: int = 1800
    pool_pre_ping: bool = True

POOL_CONFIGS = {
    'api_servers': ConnectionPoolConfig(
        min_connections=10,
        max_connections=50,
        max_overflow=20
    ),
    'workers': ConnectionPoolConfig(
        min_connections=2,
        max_connections=10,
        max_overflow=5
    ),
    'reports': ConnectionPoolConfig(
        min_connections=2,
        max_connections=5,
        max_overflow=2
    )
}
```

---

## 9.5 Caching Strategy

### 9.5.1 Multi-Tier Cache Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              L1: In-Memory (Local)                           │
│                                                                              │
│  • Hot calculation results        TTL: 5 minutes                            │
│  • Active session data            Size: 256MB per worker                    │
│  • Parsed geometry primitives                                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              L2: Redis (Shared)                              │
│                                                                              │
│  • Project metadata               TTL: 1 hour                               │
│  • Rod design results             Size: 8GB cluster                         │
│  • User sessions                                                             │
│  • Rate limiting counters                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              L3: S3 (Persistent)                             │
│                                                                              │
│  • Parsed drawing data            TTL: 30 days                              │
│  • Generated reports              Size: Unlimited                           │
│  • Historical snapshots                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.5.2 Cache Key Design

```python
class CacheKeyBuilder:
    """Build cache keys with consistent naming."""

    @staticmethod
    def project_metadata(project_id: str) -> str:
        return f"proj:meta:{project_id}"

    @staticmethod
    def rod_design(project_id: str, rod_run_id: str) -> str:
        return f"proj:{project_id}:rod:{rod_run_id}"

    @staticmethod
    def drawing_geometry(drawing_id: str, layer: str) -> str:
        return f"draw:{drawing_id}:geom:{layer}"

    @staticmethod
    def calculation_result(
        project_id: str,
        calc_type: str,
        params_hash: str
    ) -> str:
        return f"calc:{project_id}:{calc_type}:{params_hash}"

    @staticmethod
    def user_session(user_id: str, session_id: str) -> str:
        return f"sess:{user_id}:{session_id}"
```

---

## 9.6 Performance Benchmarks

### 9.6.1 Target Metrics

| Operation | Target Latency | P95 Latency | Throughput |
|-----------|----------------|-------------|------------|
| Drawing upload | < 2s | < 5s | 10/min |
| Drawing parse | < 30s | < 60s | 5/min |
| Single rod design | < 100ms | < 200ms | 100/s |
| Full project design | < 5min | < 15min | 20/hr |
| Clash detection | < 2min | < 5min | 30/hr |
| Report generation | < 30s | < 60s | 60/hr |
| API response | < 100ms | < 500ms | 1000/s |

### 9.6.2 Load Testing Configuration

```python
@dataclass
class LoadTestScenario:
    """Load test scenario configuration."""
    name: str
    concurrent_users: int
    ramp_up_seconds: int
    duration_seconds: int
    operations_per_user: Dict[str, int]

LOAD_TEST_SCENARIOS = {
    'normal_load': LoadTestScenario(
        name='Normal Business Hours',
        concurrent_users=50,
        ramp_up_seconds=60,
        duration_seconds=3600,
        operations_per_user={
            'project_create': 1,
            'drawing_upload': 5,
            'design_run': 2,
            'report_generate': 1
        }
    ),
    'peak_load': LoadTestScenario(
        name='Peak Load (Month End)',
        concurrent_users=200,
        ramp_up_seconds=120,
        duration_seconds=7200,
        operations_per_user={
            'project_create': 2,
            'drawing_upload': 10,
            'design_run': 4,
            'report_generate': 2
        }
    ),
    'stress_test': LoadTestScenario(
        name='Stress Test',
        concurrent_users=500,
        ramp_up_seconds=300,
        duration_seconds=1800,
        operations_per_user={
            'project_create': 1,
            'drawing_upload': 3,
            'design_run': 1,
            'report_generate': 1
        }
    )
}
```

---

## 9.7 Disaster Recovery

### 9.7.1 Backup Strategy

```yaml
backup_configuration:
  database:
    type: "PostgreSQL"
    strategy: "continuous_archiving"
    wal_archiving: true
    base_backup_frequency: "daily"
    retention_days: 30
    cross_region_replication: true
    rpo_minutes: 5
    rto_minutes: 60

  document_store:
    type: "MongoDB"
    strategy: "oplog_continuous"
    snapshot_frequency: "6_hours"
    retention_days: 14

  file_storage:
    type: "S3"
    versioning: true
    cross_region_replication: true
    lifecycle_rules:
      - transition_to_ia: 30_days
      - transition_to_glacier: 90_days
      - expire: 2555_days  # 7 years

  redis_cache:
    persistence: "rdb_aof"
    snapshot_frequency: "1_hour"
    # Cache is recoverable; no cross-region needed
```

### 9.7.2 Failover Procedures

```python
class FailoverManager:
    """Manage failover between regions."""

    HEALTH_CHECK_INTERVAL = 30  # seconds
    FAILOVER_THRESHOLD = 3  # consecutive failures

    def __init__(self, primary_region: str, secondary_region: str):
        self.primary = primary_region
        self.secondary = secondary_region
        self.failure_count = 0
        self.is_failed_over = False

    def check_primary_health(self) -> bool:
        """Check if primary region is healthy."""
        checks = [
            self._check_database(),
            self._check_api_servers(),
            self._check_workers(),
            self._check_storage()
        ]
        return all(checks)

    def initiate_failover(self):
        """Initiate failover to secondary region."""
        # 1. Promote secondary database
        self._promote_secondary_database()

        # 2. Update DNS to secondary
        self._update_dns_records()

        # 3. Scale up secondary workers
        self._scale_secondary_workers()

        # 4. Invalidate caches
        self._invalidate_caches()

        # 5. Notify operations team
        self._send_failover_notification()

        self.is_failed_over = True

    def initiate_failback(self):
        """Failback to primary region after recovery."""
        # 1. Sync data from secondary to primary
        self._sync_data_to_primary()

        # 2. Verify primary health
        if not self.check_primary_health():
            raise Exception("Primary region not healthy for failback")

        # 3. Switch DNS back to primary
        self._update_dns_records(to_primary=True)

        # 4. Scale down secondary
        self._scale_down_secondary()

        self.is_failed_over = False
```
