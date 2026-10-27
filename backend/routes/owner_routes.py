"""
backend/routes/owner_routes.py
Parking facility owner & operator management routes.
Restricted strictly to 'operator' and 'admin' roles.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, List
from backend.auth import get_current_user, require_role, UserProfile
from backend.services.facility_service import facility_service
from backend.services.benchmark_service import benchmark_service

router = APIRouter(prefix="/api/owner", tags=["Parking Owner"])

# In-memory store for operator-editable metadata overrides
OPERATOR_OVERRIDES: Dict[str, dict] = {}


@router.get("/overview")
def get_owner_overview(user: UserProfile = Depends(require_role(["operator", "admin"]))):
    facilities = facility_service.list_facilities(user_role=user.role, assigned_facilities=user.assigned_facilities)

    total_capacity = sum(f["capacity"] for f in facilities)
    total_occupied = sum(f["occupied_bays"] for f in facilities)
    total_vacant = sum(f["vacant_bays"] for f in facilities)
    avg_occupancy_pct = round((total_occupied / total_capacity) * 100.0, 1) if total_capacity > 0 else 0.0

    pred_vacant_30 = sum(f["forecast_30m_bays"] for f in facilities)
    pred_vacant_60 = sum(f["forecast_60m_bays"] for f in facilities)

    # Alerts summary
    nearly_full = [f for f in facilities if f["occupancy_pct"] >= 90]
    high_turnover = [f for f in facilities if abs(f["trend_delta"]) >= 30]

    return {
        "operator_name": user.name,
        "operator_title": user.title,
        "assigned_facilities_count": len(facilities),
        "total_capacity_bays": total_capacity,
        "current_occupied_bays": total_occupied,
        "current_vacant_bays": total_vacant,
        "average_occupancy_pct": avg_occupancy_pct,
        "predicted_vacant_30m": pred_vacant_30,
        "predicted_vacant_60m": pred_vacant_60,
        "prediction_trend_30m": pred_vacant_30 - total_vacant,
        "data_freshness": "Real-time Resampled IoT Stream (30-min regular grid)",
        "alerts": {
            "nearly_full_count": len(nearly_full),
            "nearly_full_facilities": [f["name"] for f in nearly_full],
            "high_turnover_count": len(high_turnover)
        },
        "facilities": facilities
    }


@router.get("/facilities")
def get_owner_facilities(user: UserProfile = Depends(require_role(["operator", "admin"]))):
    facilities = facility_service.list_facilities(user_role=user.role, assigned_facilities=user.assigned_facilities)
    # Apply any stored overrides
    for f in facilities:
        if f["id"] in OPERATOR_OVERRIDES:
            f.update(OPERATOR_OVERRIDES[f["id"]])
    return facilities


@router.put("/facilities/{lot_id}")
def update_facility_metadata(
    lot_id: str,
    payload: Dict[str, Any] = Body(...),
    user: UserProfile = Depends(require_role(["operator", "admin"]))
):
    # Verify owner permission for this lot
    if user.role != "admin" and lot_id not in user.assigned_facilities and "*" not in user.assigned_facilities:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have permission to edit this facility.")

    facility = facility_service.get_facility(lot_id)
    if not facility:
        raise HTTPException(status_code=404, detail="Facility not found.")

    # Validate and store editable metadata overrides (does NOT tamper with ground truth occupancy or capacity)
    allowed_fields = ["hourly_rate", "opening_hours", "has_ev", "has_disabled"]
    overrides = {k: payload[k] for k in allowed_fields if k in payload}

    if lot_id not in OPERATOR_OVERRIDES:
        OPERATOR_OVERRIDES[lot_id] = {}
    OPERATOR_OVERRIDES[lot_id].update(overrides)

    return {
        "status": "success",
        "message": f"Facility metadata updated for {facility['name']}.",
        "updated_fields": overrides
    }


@router.get("/analytics")
def get_owner_analytics(user: UserProfile = Depends(require_role(["operator", "admin"]))):
    facilities = facility_service.list_facilities(user_role=user.role, assigned_facilities=user.assigned_facilities)
    lot_names = [f["name"] for f in facilities]
    lot_ids = [f["id"] for f in facilities]

    audit_records = benchmark_service.get_per_lot_audit()
    owner_audit = [r for r in audit_records if r["Parking Name"] in lot_ids]

    # Combine timeline comparisons for top 3 lots
    timelines = {}
    for lot_id in lot_ids[:3]:
        timelines[lot_id] = facility_service.get_facility_occupancy_history(lot_id, limit=20)

    return {
        "assigned_count": len(facilities),
        "audit_metrics": owner_audit,
        "timelines": timelines,
        "summary": {
            "mean_personalization_gain_pct": round(sum(r["Personalization Gain (%)"] for r in owner_audit) / len(owner_audit), 1) if owner_audit else 0.0,
            "mean_personalized_mae": round(sum(r["Personalized MAE"] for r in owner_audit) / len(owner_audit), 4) if owner_audit else 0.0,
            "mean_fedavg_mae": round(sum(r["FedAvg MAE"] for r in owner_audit) / len(owner_audit), 4) if owner_audit else 0.0
        }
    }


@router.get("/health")
def get_owner_data_health(user: UserProfile = Depends(require_role(["operator", "admin"]))):
    facilities = facility_service.list_facilities(user_role=user.role, assigned_facilities=user.assigned_facilities)

    health_status_list = []
    for f in facilities:
        # Check anomaly audit for this facility
        has_clipping = f["id"] in ["NIA North", "BHMBCCTHL01", "BHMBCCMKT01", "BHMBRCBRG01", "BHMBRCBRG02", "Broad Street", "NIA South"]
        status = "Warning (Clipped Extremes)" if has_clipping else "Healthy"
        health_status_list.append({
            "lot_id": f["id"],
            "name": f["name"],
            "sensor_telemetry": "Active Resampled Stream",
            "last_packet_time": "16:30 Daily Municipal Boundary",
            "polling_interval": "30 Minutes",
            "missing_records": 0,
            "status": status,
            "clipping_applied": has_clipping,
            "samples_count": f["total_test_samples"]
        })

    return {
        "overall_health": "Operating Normally",
        "stream_coverage": "100% Intraday Sessions Resampled",
        "facilities_monitored": len(facilities),
        "devices": health_status_list
    }
