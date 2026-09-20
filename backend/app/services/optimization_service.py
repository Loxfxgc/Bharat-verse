"""
BharatVerse - Constraint Optimization Engine
Powered by Google OR-Tools (CP-SAT Solver)
Finds optimal, constraint-compliant resource allocations respecting:
- Capacity constraints (Hard)
- Capability / Equipment constraints (Hard)
- Availability & Operational status (Hard)
- Cost & Utilization optimization (Soft Objective)
"""

from typing import List, Dict, Any, Optional
from ortools.sat.python import cp_model

class ConstraintOptimizer:
    def solve_room_allocation(
        self,
        course: Dict[str, Any],
        available_rooms: List[Dict[str, Any]],
        current_room: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        students = course.get("enrolled_students", 0)
        required_caps = set(course.get("required_capabilities", []))

        # 1. Analyze all candidate rooms and compute feasibility
        evaluated_candidates = []
        feasible_room_indices = []

        for idx, room in enumerate(available_rooms):
            cap = room.get("capacity", 0)
            status = room.get("status", "available").lower()
            room_caps = set(room.get("capabilities", []))
            reasons = []

            # Hard Constraint 1: Capacity
            cap_ok = cap >= students
            if not cap_ok:
                reasons.append(f"Insufficient capacity ({cap} < required {students})")

            # Hard Constraint 2: Equipment / Capabilities
            missing_caps = required_caps - room_caps
            caps_ok = len(missing_caps) == 0
            if not caps_ok:
                reasons.append(f"Missing required equipment: {', '.join(missing_caps)}")

            # Hard Constraint 3: Status / Availability
            avail_ok = (status == "available")
            if not avail_ok:
                reasons.append(f"Room status is currently {status.upper()}")

            is_feasible = cap_ok and caps_ok and avail_ok

            # Soft objective score: smaller difference in capacity (less wasted space) + cost
            waste = max(0, cap - students)
            cost = room.get("cost_per_hour", 50.0)
            score = float(waste * 1.5 + cost * 0.5)

            if is_feasible:
                feasible_room_indices.append(idx)

            evaluated_candidates.append({
                "room_id": room.get("resource_id"),
                "name": room.get("name"),
                "capacity": cap,
                "status": room.get("status"),
                "capabilities": room.get("capabilities", []),
                "cost_per_hour": cost,
                "feasible": is_feasible,
                "rejection_reasons": reasons,
                "objective_score": round(score, 2)
            })

        # 2. Formulate CP-SAT Optimization Model
        model = cp_model.CpModel()
        num_rooms = len(available_rooms)

        # Decision variables: x[r] == 1 if room r is chosen
        x = [model.NewBoolVar(f"room_{i}") for i in range(num_rooms)]

        # Constraint: Exactly one room must be chosen
        model.Add(sum(x) == 1)

        # Hard Constraint: Infeasible rooms cannot be selected
        for i in range(num_rooms):
            if i not in feasible_room_indices:
                model.Add(x[i] == 0)

        # Objective: Minimize weighted waste and cost
        # Convert floats to integer scaled penalties for CP-SAT
        objective_terms = []
        for i in range(num_rooms):
            score_int = int(evaluated_candidates[i]["objective_score"] * 100)
            objective_terms.append(x[i] * score_int)

        model.Minimize(sum(objective_terms))

        # Solve with OR-Tools CP-SAT
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 2.0
        status = solver.Solve(model)

        best_room_id = None
        solver_status_str = "INFEASIBLE"

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            solver_status_str = "OPTIMAL" if status == cp_model.OPTIMAL else "FEASIBLE"
            for i in range(num_rooms):
                if solver.Value(x[i]) == 1:
                    best_room_id = available_rooms[i]["resource_id"]
                    break

        return {
            "solver_status": solver_status_str,
            "best_allocation": best_room_id,
            "evaluated_candidates": evaluated_candidates,
            "total_candidates": num_rooms,
            "feasible_candidates": len(feasible_room_indices)
        }

constraint_optimizer = ConstraintOptimizer()
