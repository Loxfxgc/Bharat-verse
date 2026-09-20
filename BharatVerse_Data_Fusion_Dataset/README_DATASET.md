# BharatVerse Data Fusion Dataset

Synthetic Smart Campus dataset designed directly against the Phase 4 README.

## Scale
- Students: 1,000
- Faculty: 50
- Courses: 100
- Rooms: 30
- Equipment: 100
- Schedules: 500
- Enrollment edges: 6,266
- IoT room readings: 14,400
- Operational events: 500

## Fusion design
Raw source systems intentionally use different schemas/names:
LMS, ERP, HR, Asset Register, IoT and OpsLog.
They are fused into `processed/universal_resource_model.csv`.

## ML
`processed/fused_ml_room_occupancy.csv` contains:
day_of_week, hour, course-related temporal context, historical occupancy,
lag features, rolling occupancy, capacity, utilization and anomaly labels.

## Optimization
`processed/scenario_candidates.csv` contains candidate room allocations,
capacity slack, equipment feasibility, schedule conflict, faculty availability,
cost, distance, hard-feasibility and a sample objective score.

The final OR-Tools implementation should recompute the objective and constraints
rather than treating `allocation_score` as ground truth.

## Important synthetic events
Known abnormal occupancy was injected for R003 and R017 on selected timestamps
so Isolation Forest / rule validation has a measurable anomaly case.

## Data-fusion fields
`processed/fusion_lineage.csv` documents how heterogeneous source fields map
into the canonical model.

## Recommended pipeline
raw -> validation -> normalization -> fusion -> digital twin state -> prediction/anomaly
-> scenario -> optimization -> recommendation -> approval -> outcome -> feedback.

## Caveat
All records are synthetic and suitable for development/demo/testing only.
