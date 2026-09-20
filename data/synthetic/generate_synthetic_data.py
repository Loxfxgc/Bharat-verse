"""
BharatVerse - Synthetic Data Generator
Generates campus resources, relationships, schedules, and 90 days of hourly
occupancy logs with realistic temporal patterns, anomalies, and constraint triggers.
"""

import json
import random
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_campus_data():
    print("Generating BharatVerse Synthetic Campus Dataset...")

    # 1. Buildings
    buildings = [
        {"building_id": "BLD_A", "name": "Aryabhata Academic Block", "floors": 4, "location": "North Campus"},
        {"building_id": "BLD_B", "name": "Bhabha Science & Tech Block", "floors": 5, "location": "East Campus"},
        {"building_id": "BLD_C", "name": "Ramanujan Computing Complex", "floors": 3, "location": "West Campus"},
    ]

    # 2. Rooms (Universal Resource Model)
    rooms = [
        # Block A (flagship DS301 case included)
        {"resource_id": "ROOM_R101", "name": "Room R101", "type": "room", "capacity": 60, "building_id": "BLD_A", "floor": 1, "status": "occupied", "capabilities": ["projector"], "cost_per_hour": 50, "location": "Block A - Floor 1"},
        {"resource_id": "ROOM_R102", "name": "Room R102", "type": "room", "capacity": 100, "building_id": "BLD_A", "floor": 1, "status": "available", "capabilities": ["projector", "computer", "audio"], "cost_per_hour": 75, "location": "Block A - Floor 1"},
        {"resource_id": "ROOM_R103", "name": "Room R103", "type": "room", "capacity": 80, "building_id": "BLD_A", "floor": 1, "status": "available", "capabilities": ["projector"], "cost_per_hour": 60, "location": "Block A - Floor 1"},
        {"resource_id": "ROOM_R104", "name": "Room R104", "type": "room", "capacity": 120, "building_id": "BLD_A", "floor": 1, "status": "occupied", "capabilities": ["projector", "computer", "audio", "smartboard"], "cost_per_hour": 110, "location": "Block A - Floor 1"},
        {"resource_id": "ROOM_R201", "name": "Room R201", "type": "room", "capacity": 70, "building_id": "BLD_A", "floor": 2, "status": "available", "capabilities": ["projector"], "cost_per_hour": 55, "location": "Block A - Floor 2"},
        {"resource_id": "ROOM_R202", "name": "Room R202", "type": "room", "capacity": 90, "building_id": "BLD_A", "floor": 2, "status": "maintenance", "capabilities": ["projector", "computer"], "cost_per_hour": 70, "location": "Block A - Floor 2"},
        {"resource_id": "ROOM_R203", "name": "Room R203", "type": "room", "capacity": 60, "building_id": "BLD_A", "floor": 2, "status": "available", "capabilities": ["projector"], "cost_per_hour": 50, "location": "Block A - Floor 2"},
        {"resource_id": "ROOM_AUD1", "name": "Dr. Kalam Auditorium", "type": "auditorium", "capacity": 300, "building_id": "BLD_A", "floor": 3, "status": "available", "capabilities": ["projector", "computer", "audio", "stage_lighting", "broadcast"], "cost_per_hour": 250, "location": "Block A - Floor 3"},

        # Block B
        {"resource_id": "ROOM_B101", "name": "Hall B101", "type": "room", "capacity": 150, "building_id": "BLD_B", "floor": 1, "status": "available", "capabilities": ["projector", "audio", "smartboard"], "cost_per_hour": 120, "location": "Block B - Floor 1"},
        {"resource_id": "ROOM_B102", "name": "Room B102", "type": "room", "capacity": 50, "building_id": "BLD_B", "floor": 1, "status": "occupied", "capabilities": ["projector"], "cost_per_hour": 45, "location": "Block B - Floor 1"},
        {"resource_id": "ROOM_B201", "name": "Room B201", "type": "room", "capacity": 75, "building_id": "BLD_B", "floor": 2, "status": "available", "capabilities": ["projector", "computer"], "cost_per_hour": 65, "location": "Block B - Floor 2"},
        {"resource_id": "ROOM_B202", "name": "Room B202", "type": "room", "capacity": 85, "building_id": "BLD_B", "floor": 2, "status": "reserved", "capabilities": ["projector"], "cost_per_hour": 65, "location": "Block B - Floor 2"},
        {"resource_id": "ROOM_PHY_LAB", "name": "Advanced Physics Lab", "type": "laboratory", "capacity": 40, "building_id": "BLD_B", "floor": 3, "status": "available", "capabilities": ["lab_equipment", "sensors", "power_bench"], "cost_per_hour": 90, "location": "Block B - Floor 3"},
        {"resource_id": "ROOM_CHEM_LAB", "name": "Nanotech Chemistry Lab", "type": "laboratory", "capacity": 35, "building_id": "BLD_B", "floor": 4, "status": "available", "capabilities": ["fume_hood", "chemical_bench", "sensors"], "cost_per_hour": 100, "location": "Block B - Floor 4"},

        # Block C (Computing)
        {"resource_id": "ROOM_C101", "name": "Computing Lab Alpha", "type": "laboratory", "capacity": 60, "building_id": "BLD_C", "floor": 1, "status": "occupied", "capabilities": ["computer", "gpu_cluster", "projector", "high_speed_net"], "cost_per_hour": 130, "location": "Block C - Floor 1"},
        {"resource_id": "ROOM_C102", "name": "AI & Robotics Lab", "type": "laboratory", "capacity": 45, "building_id": "BLD_C", "floor": 1, "status": "available", "capabilities": ["gpu_cluster", "robotics_kit", "projector", "computer"], "cost_per_hour": 150, "location": "Block C - Floor 1"},
        {"resource_id": "ROOM_C201", "name": "Seminar Room C201", "type": "seminar", "capacity": 55, "building_id": "BLD_C", "floor": 2, "status": "available", "capabilities": ["smartboard", "video_conf", "audio"], "cost_per_hour": 80, "location": "Block C - Floor 2"},
        {"resource_id": "ROOM_C202", "name": "IoT Innovation Lab", "type": "laboratory", "capacity": 40, "building_id": "BLD_C", "floor": 2, "status": "available", "capabilities": ["iot_nodes", "sensors", "soldering_stations", "computer"], "cost_per_hour": 95, "location": "Block C - Floor 2"},
    ]

    # Additional standard rooms to reach 25 campus spaces
    for i in range(301, 308):
        rooms.append({
            "resource_id": f"ROOM_R{i}",
            "name": f"Lecture Room R{i}",
            "type": "room",
            "capacity": random.choice([50, 65, 80, 100, 110]),
            "building_id": random.choice(["BLD_A", "BLD_B"]),
            "floor": 3,
            "status": random.choice(["available", "available", "occupied", "maintenance"]),
            "capabilities": ["projector", "computer"] if i % 2 == 0 else ["projector"],
            "cost_per_hour": random.randint(45, 85),
            "location": f"Academic Wing - Level 3"
        })

    # 3. Faculty Members
    faculty = [
        {"faculty_id": "FAC_X", "name": "Dr. X (Prof. A. Sengupta)", "department": "Computer Science & AI", "title": "Professor", "email": "asengupta@campus.edu", "expertise": ["Machine Learning", "Data Science"]},
        {"faculty_id": "FAC_ROY", "name": "Dr. Vikram Roy", "department": "Computer Science", "title": "Associate Professor", "email": "vroy@campus.edu", "expertise": ["Algorithms", "Distributed Systems"]},
        {"faculty_id": "FAC_PRIYA", "name": "Dr. Priya Patel", "department": "Data Science", "title": "Assistant Professor", "email": "ppatel@campus.edu", "expertise": ["Data Analytics", "Deep Learning"]},
        {"faculty_id": "FAC_SHARMA", "name": "Prof. Rajesh Sharma", "department": "Electronics", "title": "Professor", "email": "rsharma@campus.edu", "expertise": ["IoT Systems", "Embedded Sensors"]},
        {"faculty_id": "FAC_MEERA", "name": "Dr. Meera Iyer", "department": "Mechanical Eng", "title": "Associate Professor", "email": "miyer@campus.edu", "expertise": ["Robotics", "Automation"]},
        {"faculty_id": "FAC_VERMA", "name": "Dr. Amit Verma", "department": "Physics", "title": "Assistant Professor", "email": "averma@campus.edu", "expertise": ["Quantum Mechanics", "Optics"]},
        {"faculty_id": "FAC_ANANYA", "name": "Dr. Ananya Das", "department": "Mathematics", "title": "Associate Professor", "email": "adas@campus.edu", "expertise": ["Optimization", "Stochastics"]},
        {"faculty_id": "FAC_KAPOOR", "name": "Dr. Sunil Kapoor", "department": "Management & Systems", "title": "Professor", "email": "skapoor@campus.edu", "expertise": ["Operations Research", "Logistics"]},
    ]

    # 4. Courses
    courses = [
        {
            "course_id": "CRS_DS301",
            "code": "DS301",
            "name": "Data Science & Big Data Systems",
            "enrolled_students": 85,
            "faculty_id": "FAC_X",
            "required_capabilities": ["projector", "computer"],
            "current_room_id": "ROOM_R101", # Problem: R101 capacity is 60! 85 students!
            "day": "Monday",
            "time_slot": "09:00 - 11:00",
            "priority": "high",
        },
        {
            "course_id": "CRS_CS101",
            "code": "CS101",
            "name": "Data Structures & Algorithms",
            "enrolled_students": 95,
            "faculty_id": "FAC_ROY",
            "required_capabilities": ["projector"],
            "current_room_id": "ROOM_R104",
            "day": "Monday",
            "time_slot": "11:15 - 13:15",
            "priority": "high",
        },
        {
            "course_id": "CRS_AI401",
            "code": "AI401",
            "name": "Deep Learning & Neural Networks Lab",
            "enrolled_students": 42,
            "faculty_id": "FAC_PRIYA",
            "required_capabilities": ["computer", "gpu_cluster"],
            "current_room_id": "ROOM_C101",
            "day": "Tuesday",
            "time_slot": "14:00 - 16:00",
            "priority": "medium",
        },
        {
            "course_id": "CRS_IOT201",
            "code": "IOT201",
            "name": "IoT Architectures & Edge Intelligence",
            "enrolled_students": 38,
            "faculty_id": "FAC_SHARMA",
            "required_capabilities": ["sensors", "iot_nodes"],
            "current_room_id": "ROOM_C202",
            "day": "Wednesday",
            "time_slot": "09:00 - 11:00",
            "priority": "medium",
        },
        {
            "course_id": "CRS_ROB302",
            "code": "ROB302",
            "name": "Autonomous Robotics Lab",
            "enrolled_students": 32,
            "faculty_id": "FAC_MEERA",
            "required_capabilities": ["robotics_kit", "gpu_cluster"],
            "current_room_id": "ROOM_C102",
            "day": "Thursday",
            "time_slot": "10:00 - 12:00",
            "priority": "high",
        },
        {
            "course_id": "CRS_OPT501",
            "code": "OPT501",
            "name": "Operations Research & Optimization",
            "enrolled_students": 72,
            "faculty_id": "FAC_ANANYA",
            "required_capabilities": ["projector", "computer"],
            "current_room_id": "ROOM_R103",
            "day": "Friday",
            "time_slot": "14:00 - 16:00",
            "priority": "medium",
        },
        {
            "course_id": "CRS_MGT405",
            "code": "MGT405",
            "name": "Enterprise Supply Chain Optimization",
            "enrolled_students": 110,
            "faculty_id": "FAC_KAPOOR",
            "required_capabilities": ["projector", "audio"],
            "current_room_id": "ROOM_B101",
            "day": "Wednesday",
            "time_slot": "11:15 - 13:15",
            "priority": "medium",
        },
    ]

    # Add more courses
    for i in range(10, 25):
        c_code = f"GEN{i*10}"
        c_size = random.randint(35, 110)
        c_fac = random.choice(faculty)["faculty_id"]
        c_room = random.choice(rooms)["resource_id"]
        courses.append({
            "course_id": f"CRS_{c_code}",
            "code": c_code,
            "name": f"Advanced Topic Course {c_code}",
            "enrolled_students": c_size,
            "faculty_id": c_fac,
            "required_capabilities": ["projector"],
            "current_room_id": c_room,
            "day": random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
            "time_slot": random.choice(["09:00 - 11:00", "11:15 - 13:15", "14:00 - 16:00"]),
            "priority": random.choice(["low", "medium", "high"]),
        })

    # 5. Equipment
    equipment = [
        {"equipment_id": "EQP_PROJ_01", "name": "4K Laser Projector Pro", "type": "projector", "status": "functional", "room_id": "ROOM_R102"},
        {"equipment_id": "EQP_PROJ_02", "name": "Optoma Classroom Projector", "type": "projector", "status": "functional", "room_id": "ROOM_R101"},
        {"equipment_id": "EQP_GPU_01", "name": "NVIDIA DGX A100 Workstation", "type": "gpu_cluster", "status": "functional", "room_id": "ROOM_C101"},
        {"equipment_id": "EQP_AUDIO_01", "name": "JBL Conference Mic & Surround", "type": "audio", "status": "functional", "room_id": "ROOM_R102"},
        {"equipment_id": "EQP_ROBOT_01", "name": "TurtleBot3 Mobile Manipulators (x6)", "type": "robotics_kit", "status": "functional", "room_id": "ROOM_C102"},
        {"equipment_id": "EQP_IOT_01", "name": "ESP32 & LoRa Gateway Testbed", "type": "iot_nodes", "status": "functional", "room_id": "ROOM_C202"},
    ]

    # 6. Graph Nodes and Edges (for Neo4j / NetworkX graph layer)
    nodes = []
    edges = []

    for b in buildings:
        nodes.append({"id": b["building_id"], "label": "Building", "name": b["name"]})

    for r in rooms:
        nodes.append({"id": r["resource_id"], "label": "Room", "name": r["name"], "capacity": r["capacity"]})
        edges.append({"source": r["resource_id"], "target": r["building_id"], "relation": "LOCATED_IN"})

    for f in faculty:
        nodes.append({"id": f["faculty_id"], "label": "Faculty", "name": f["name"], "dept": f["department"]})

    for c in courses:
        nodes.append({"id": c["course_id"], "label": "Course", "name": c["name"], "enrolled": c["enrolled_students"]})
        edges.append({"source": c["course_id"], "target": c["faculty_id"], "relation": "TAUGHT_BY"})
        edges.append({"source": c["course_id"], "target": c["current_room_id"], "relation": "SCHEDULED_IN"})
        for cap in c["required_capabilities"]:
            edges.append({"source": c["course_id"], "target": cap, "relation": "REQUIRES_CAPABILITY"})

    for eq in equipment:
        nodes.append({"id": eq["equipment_id"], "label": "Equipment", "name": eq["name"]})
        edges.append({"source": eq["equipment_id"], "target": eq["room_id"], "relation": "INSTALLED_IN"})

    # 7. Generate 90 days of Hourly Occupancy / Resource Sensor Data
    base_date = datetime(2026, 6, 20, 0, 0, 0)
    records = []

    # Choose a representative set of rooms for dense time series
    tracked_rooms = rooms[:12]

    for day_offset in range(90):
        current_day = base_date + timedelta(days=day_offset)
        day_of_week = current_day.weekday() # 0 = Monday, 6 = Sunday
        is_weekend = 1 if day_of_week >= 5 else 0
        is_exam_week = 1 if 40 <= day_offset <= 54 else 0

        for r in tracked_rooms:
            cap = r["capacity"]
            for hour in range(24):
                # Normal operational occupancy curve
                if is_weekend:
                    expected_occ = int(cap * random.uniform(0.0, 0.15))
                elif 0 <= hour <= 7:
                    expected_occ = 0
                elif 8 <= hour <= 12: # Morning peak
                    expected_occ = int(cap * random.uniform(0.55, 0.95))
                elif 13 <= hour <= 14: # Lunch lull
                    expected_occ = int(cap * random.uniform(0.20, 0.45))
                elif 15 <= hour <= 18: # Afternoon session
                    expected_occ = int(cap * random.uniform(0.50, 0.90))
                elif 19 <= hour <= 21: # Evening clubs/library
                    expected_occ = int(cap * random.uniform(0.10, 0.35))
                else:
                    expected_occ = 0

                if is_exam_week and not is_weekend and 9 <= hour <= 17:
                    expected_occ = min(cap, int(expected_occ * 1.25))

                actual_occ = expected_occ
                is_anomaly = 0

                # Inject realistic anomalies (2% probability)
                anomaly_roll = random.random()
                if anomaly_roll < 0.015:
                    # Off-hours spike (e.g. at 2 AM or Sunday)
                    if hour in [1, 2, 3, 23] or is_weekend:
                        actual_occ = min(cap, int(cap * random.uniform(0.70, 0.98)))
                        is_anomaly = 1
                    # Sudden severe overcrowding
                    elif actual_occ > 0:
                        actual_occ = int(cap * random.uniform(1.15, 1.40)) # Beyond max cap
                        is_anomaly = 1
                elif anomaly_roll > 0.99:
                    # Ghost class (scheduled but 0 people)
                    if 9 <= hour <= 16 and not is_weekend:
                        actual_occ = 0
                        is_anomaly = 1

                utilization = round((actual_occ / cap) * 100.0, 2)
                timestamp_str = (current_day + timedelta(hours=hour)).strftime("%Y-%m-%d %H:%M:%S")

                records.append({
                    "timestamp": timestamp_str,
                    "room_id": r["resource_id"],
                    "day_of_week": day_of_week,
                    "hour": hour,
                    "is_weekend": is_weekend,
                    "exam_period": is_exam_week,
                    "room_capacity": cap,
                    "equipment_count": len(r["capabilities"]),
                    "cost_per_hour": r["cost_per_hour"],
                    "actual_occupancy": actual_occ,
                    "utilization_ratio": utilization,
                    "is_anomaly": is_anomaly
                })

    df_occupancy = pd.DataFrame(records)

    # Save to files
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DATA_DIR, "..", "processed"), exist_ok=True)

    with open(os.path.join(DATA_DIR, "campus_resources.json"), "w") as f:
        json.dump({
            "buildings": buildings,
            "rooms": rooms,
            "faculty": faculty,
            "courses": courses,
            "equipment": equipment
        }, f, indent=2)

    with open(os.path.join(DATA_DIR, "graph_nodes_edges.json"), "w") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

    df_occupancy.to_csv(os.path.join(DATA_DIR, "historical_occupancy.csv"), index=False)
    print(f"Generated {len(rooms)} rooms, {len(faculty)} faculty, {len(courses)} courses, {len(equipment)} equipment items.")
    print(f"Generated {len(records)} hourly occupancy sensor entries saved to data/synthetic/historical_occupancy.csv.")
    print(f"Graph dataset saved to data/synthetic/graph_nodes_edges.json.")

if __name__ == "__main__":
    generate_campus_data()
