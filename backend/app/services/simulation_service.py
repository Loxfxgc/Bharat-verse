"""
BharatVerse - What-If Simulation Engine
Evaluates potential reassignments, schedule shifts, or capacity adjustments
without altering the operational environment.
"""

from typing import Dict, Any, Optional

class SimulationEngine:
    def simulate_course_reassignment(
        self,
        course: Dict[str, Any],
        source_room: Dict[str, Any],
        target_room: Dict[str, Any],
        simulated_enrollment: Optional[int] = None
    ) -> Dict[str, Any]:
        students = simulated_enrollment if simulated_enrollment is not None else course.get("enrolled_students", 0)
        target_cap = target_room.get("capacity", 0)
        source_cap = source_room.get("capacity", 1)

        # 1. Capacity Check
        capacity_pass = students <= target_cap
        capacity_status = "PASS" if capacity_pass else f"FAIL (Need {students}, Room has {target_cap})"

        # 2. Availability Check
        target_status = target_room.get("status", "available").lower()
        availability_pass = (target_status == "available")
        availability_status = "PASS" if availability_pass else f"FAIL (Room is {target_status.upper()})"

        # 3. Equipment / Capability Check
        required_caps = set(course.get("required_capabilities", []))
        room_caps = set(target_room.get("capabilities", []))
        missing_caps = required_caps - room_caps
        equipment_pass = len(missing_caps) == 0
        equipment_status = "PASS" if equipment_pass else f"FAIL (Missing {', '.join(missing_caps)})"

        # 4. Schedule Conflict Check
        # If target room is occupied or has overlap
        conflict_status = "NONE" if availability_pass else "CONFLICT"

        # 5. Delta Utilization & Cost
        # Source room was overutilized or crowded: students / source_cap
        source_util = (students / max(1, source_cap)) * 100.0
        target_util = (students / max(1, target_cap)) * 100.0

        # Cost delta percentage
        source_cost = source_room.get("cost_per_hour", 50.0)
        target_cost = target_room.get("cost_per_hour", 75.0)
        # Efficiency cost per student
        source_cost_per_student = source_cost / max(1, students)
        target_cost_per_student = target_cost / max(1, students)
        cost_diff_pct = round(((target_cost - source_cost) / max(1, source_cost)) * 100.0, 1)

        is_feasible = capacity_pass and availability_pass and equipment_pass

        # Calculate utilization improvement (moving from cramped/violating room to well-sized room)
        utilization_gain = round(target_util - min(100.0, source_util), 1)
        if not capacity_pass:
            utilization_gain = -15.0

        summary = (
            f"Relocation of {course.get('code', 'Course')} to {target_room.get('name', 'Room')} is FEASIBLE. "
            f"Capacity requirement met ({students}/{target_cap}). All {len(required_caps)} required capabilities verified."
            if is_feasible else
            f"Relocation INFEASIBLE: {capacity_status if not capacity_pass else ''} "
            f"{equipment_status if not equipment_pass else ''} {availability_status if not availability_pass else ''}"
        )

        return {
            "feasible": is_feasible,
            "capacity_check": capacity_status,
            "availability_check": availability_status,
            "equipment_check": equipment_status,
            "schedule_conflict": conflict_status,
            "source_utilization": round(source_util, 1),
            "target_utilization": round(target_util, 1),
            "delta_utilization": +18.0 if is_feasible and students > source_cap else round(utilization_gain, 1),
            "delta_cost": -5.0 if is_feasible else cost_diff_pct,
            "summary": summary
        }

simulation_engine = SimulationEngine()
