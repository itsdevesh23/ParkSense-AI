"""
backend/routes/facility_routes.py
Public and customer-facing parking facility discovery and prediction routes.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from backend.services.facility_service import facility_service
from backend.auth import get_current_user, UserProfile

router = APIRouter(prefix="/api/facilities", tags=["Facilities"])


@router.get("")
def list_facilities(
    search: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = Query("name", enum=["name", "vacancies", "capacity", "occupancy", "trend"]),
    min_capacity: Optional[int] = None,
    has_ev: Optional[bool] = None,
    user: UserProfile = Depends(get_current_user)
):
    """
    Returns facilities with search, filter, and sorting options.
    """
    facilities = facility_service.list_facilities(user_role=user.role, assigned_facilities=user.assigned_facilities)

    # Filtering
    if search:
        s = search.lower()
        facilities = [f for f in facilities if s in f["name"].lower() or s in f["operator"].lower() or s in f["address"].lower() or s in f["system_code"].lower()]

    if status and status != "All":
        facilities = [f for f in facilities if f["status"].lower() == status.lower()]

    if min_capacity is not None:
        facilities = [f for f in facilities if f["capacity"] >= min_capacity]

    if has_ev is not None and has_ev:
        facilities = [f for f in facilities if f.get("has_ev", False)]

    # Sorting
    if sort_by == "vacancies":
        facilities = sorted(facilities, key=lambda x: x["vacant_bays"], reverse=True)
    elif sort_by == "capacity":
        facilities = sorted(facilities, key=lambda x: x["capacity"], reverse=True)
    elif sort_by == "occupancy":
        facilities = sorted(facilities, key=lambda x: x["occupancy_pct"], reverse=True)
    elif sort_by == "trend":
        facilities = sorted(facilities, key=lambda x: x["trend_delta"], reverse=True)
    else:
        facilities = sorted(facilities, key=lambda x: x["name"])

    return {
        "total_count": len(facilities),
        "data_notice": "Historical Benchmark Replay (Birmingham Municipal IoT Stream - UCI Machine Learning Repository)",
        "facilities": facilities
    }


@router.get("/{lot_id}")
def get_facility_detail(lot_id: str, user: UserProfile = Depends(get_current_user)):
    facility = facility_service.get_facility(lot_id)
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility '{lot_id}' not found.")
    return facility


@router.get("/{lot_id}/occupancy")
def get_facility_occupancy(
    lot_id: str,
    limit: int = Query(24, ge=6, le=72),
    user: UserProfile = Depends(get_current_user)
):
    facility = facility_service.get_facility(lot_id)
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility '{lot_id}' not found.")

    history = facility_service.get_facility_occupancy_history(lot_id, limit=limit)
    return {
        "facility_id": lot_id,
        "facility_name": facility["name"],
        "capacity": facility["capacity"],
        "history_points": len(history),
        "timeline": history
    }


@router.get("/{lot_id}/forecast")
def get_facility_forecast(
    lot_id: str,
    horizon: int = Query(30, enum=[30, 60]),
    user: UserProfile = Depends(get_current_user)
):
    facility = facility_service.get_facility(lot_id)
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility '{lot_id}' not found.")

    history = facility_service.get_facility_occupancy_history(lot_id, limit=12)
    bays_key = "forecast_30m_bays" if horizon == 30 else "forecast_60m_bays"
    ratio_key = "forecast_30m_ratio" if horizon == 30 else "forecast_60m_ratio"

    return {
        "facility_id": lot_id,
        "facility_name": facility["name"],
        "horizon_minutes": horizon,
        "current_vacant_bays": facility["vacant_bays"],
        "forecast_vacant_bays": facility[bays_key],
        "forecast_availability_ratio": facility[ratio_key],
        "delta_bays": facility[bays_key] - facility["vacant_bays"],
        "model_architecture": "Personalized Attention-LSTM (FedAvg + Local Fine-Tuning)",
        "model_mae_ratio": facility["model_mae_ratio"],
        "model_mae_spaces": facility["model_mae_spaces"],
        "data_notice": "Inference generated from trained PyTorch client model using 6-step temporal lookback"
    }
