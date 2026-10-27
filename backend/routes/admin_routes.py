"""
backend/routes/admin_routes.py
System Administrator routes for platform-wide monitoring,
Federated Learning fleet telemetry, model benchmark laboratory, and dataset audit.
Strictly restricted to 'admin' role.
"""

from fastapi import APIRouter, Depends, Query
from typing import Dict, Any, List
from backend.auth import require_role, UserProfile
from backend.services.facility_service import facility_service
from backend.services.benchmark_service import benchmark_service
from backend.services.audit_service import audit_service

router = APIRouter(prefix="/api/admin", tags=["System Administrator"])


@router.get("/overview")
def get_admin_overview(user: UserProfile = Depends(require_role(["admin"]))):
    facilities = facility_service.list_facilities(user_role="admin", assigned_facilities=["*"])
    kpis = benchmark_service.get_summary_kpis()

    total_capacity = sum(f["capacity"] for f in facilities)
    total_occupied = sum(f["occupied_bays"] for f in facilities)
    total_vacant = sum(f["vacant_bays"] for f in facilities)

    return {
        "admin_name": user.name,
        "total_configured_facilities": len(facilities),
        "total_fleet_capacity": total_capacity,
        "current_total_occupied": total_occupied,
        "current_total_vacant": total_vacant,
        "city_occupancy_rate_pct": round((total_occupied / total_capacity) * 100.0, 1),
        "fl_clients_count": len(facilities),
        "active_training_round": kpis["active_training_round"],
        "federated_algorithm": kpis["federated_algorithm"],
        "privacy_mode": kpis["privacy_mode"],
        "kpis": kpis,
        "facilities": facilities
    }


@router.get("/registry")
def get_admin_registry(user: UserProfile = Depends(require_role(["admin"]))):
    facilities = facility_service.list_facilities(user_role="admin", assigned_facilities=["*"])
    return {
        "count": len(facilities),
        "registry": facilities
    }


@router.get("/federated")
def get_admin_federated_monitor(user: UserProfile = Depends(require_role(["admin"]))):
    kpis = benchmark_service.get_summary_kpis()
    round_scaling = benchmark_service.get_round_scaling()
    per_lot_audit = benchmark_service.get_per_lot_audit()

    return {
        "cluster_name": "Birmingham Municipal IoT Edge Cluster",
        "participating_nodes": 30,
        "aggregation_server": "FedAvg Synchronous Parameter Coordinator",
        "hyperparameters": {
            "local_epochs": 2,
            "local_batch_size": 32,
            "learning_rate": 0.001,
            "weight_decay": 1e-5,
            "communication_rounds": 8,
            "personalization_epochs": 3,
            "personalization_lr": 0.0003,
            "loss_criterion": "Mean Squared Error (MSELoss)"
        },
        "round_scaling": round_scaling,
        "round_scaling_experiment": {
            "description": "Controlled 30-Client Round Scaling Experiment (batch_size=64, seed=42)",
            "progression": round_scaling,
            "conclusion": "Demonstrates diminishing returns from additional global rounds under non-IID client heterogeneity"
        },
        "personalization": {
            "fedavg_mae": kpis["fedavg_30m_mae"],
            "personalized_mae": kpis["pers_30m_mae"],
            "gain_pct": kpis["gain_30m_pct"],
            "std_reduction": kpis["inter_lot_variance_reduction_pct"]
        },
        "headline_improvements": {
            "pooled_mae_30m": {
                "global_fedavg": kpis["fedavg_30m_mae"],
                "personalized_fedavg": kpis["pers_30m_mae"],
                "reduction_pct": kpis["gain_30m_pct"]
            },
            "pooled_mae_60m": {
                "global_fedavg": kpis["fedavg_60m_mae"],
                "personalized_fedavg": kpis["pers_60m_mae"],
                "reduction_pct": kpis["gain_60m_pct"]
            },
            "inter_lot_variance_reduction_pct": kpis["inter_lot_variance_reduction_pct"]
        },
        "client_audit_records": per_lot_audit
    }


@router.get("/benchmarks")
def get_admin_benchmarks(
    horizon: str = Query("30min", enum=["30min", "60min", "both"]),
    user: UserProfile = Depends(require_role(["admin"]))
):
    b30 = benchmark_service.get_benchmark("30min")
    b60 = benchmark_service.get_benchmark("60min")
    kpis = benchmark_service.get_summary_kpis()
    if horizon == "both":
        return {
            "horizon_30min": b30,
            "horizon_60min": b60,
            "benchmark_30min": b30,
            "benchmark_60min": b60,
            "kpis": kpis
        }
    tbl = b30 if horizon == "30min" else b60
    return {
        "horizon": horizon,
        "benchmark_table": tbl,
        "benchmark_30min": b30,
        "benchmark_60min": b60,
        "kpis": kpis
    }


@router.get("/audit")
def get_admin_data_audit(user: UserProfile = Depends(require_role(["admin"]))):
    summary = audit_service.get_audit_summary()
    per_lot = benchmark_service.get_per_lot_audit()
    return {
        **summary,
        "total_records": summary.get("total_raw_records", 35717),
        "per_lot_audit": per_lot
    }
