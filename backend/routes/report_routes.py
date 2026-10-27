"""
backend/routes/report_routes.py
Report generation and CSV streaming endpoints for facility operators and administrators.
"""

from fastapi import APIRouter, Response, Query, Depends
import pandas as pd
import io
from backend.auth import get_current_user, UserProfile
from backend.services.facility_service import facility_service
from backend.services.benchmark_service import benchmark_service

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/occupancy.csv")
def export_occupancy_csv(user: UserProfile = Depends(get_current_user)):
    facilities = facility_service.list_facilities(user_role=user.role, assigned_facilities=user.assigned_facilities)
    df = pd.DataFrame(facilities)

    # Filter to permitted export columns
    export_cols = [
        "id", "name", "operator", "capacity", "occupied_bays", "vacant_bays",
        "occupancy_pct", "status", "forecast_30m_bays", "forecast_60m_bays",
        "model_mae_ratio", "model_mae_spaces", "hourly_rate"
    ]
    df_export = df[[c for c in export_cols if c in df.columns]]

    stream = io.StringIO()
    df_export.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=parksense_facility_occupancy_report.csv"}
    )


@router.get("/benchmarks.csv")
def export_benchmarks_csv(
    horizon: str = Query("30min", enum=["30min", "60min"]),
    user: UserProfile = Depends(get_current_user)
):
    benchmarks = benchmark_service.get_benchmark(horizon)
    df = pd.DataFrame(benchmarks)

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=parksense_benchmark_{horizon}.csv"}
    )


@router.get("/audit.csv")
def export_audit_csv(user: UserProfile = Depends(get_current_user)):
    records = benchmark_service.get_per_lot_audit()
    df = pd.DataFrame(records)

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=parksense_per_lot_evaluation_audit.csv"}
    )
