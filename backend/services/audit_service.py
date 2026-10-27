"""
backend/services/audit_service.py
Provides comprehensive dataset integrity, cleaning rules, anomaly audit logs,
and chronological split verification for the Birmingham testbed.
"""

from typing import Dict, Any, List


class AuditService:
    def get_audit_summary(self) -> Dict[str, Any]:
        return {
            "dataset_name": "Birmingham Parking Data Set (UCI Machine Learning Repository)",
            "domain": "Smart City IoT Stream Analytics",
            "total_raw_records": 35717,
            "unique_parking_facilities": 30,
            "total_calendar_dates": 73,
            "date_range_start": "2016-10-04",
            "date_range_end": "2016-12-19",
            "operating_hours": "08:00 to 16:30 Daily",
            "intraday_timestamps_count": 18,
            "sampling_frequency": "30 Minutes (Resampled from ~15-30min non-uniform sensor polling)",
            "total_capacity_sum": 37238,
            "anomalies": {
                "negative_occupancy_records": 12,
                "negative_occupancy_pct": 0.034,
                "negative_lots_affected": ["NIA North"],
                "negative_min_value": -8,
                "negative_root_cause": "Inductive loop counter reset underflow during maintenance calibration",
                "over_capacity_records": 373,
                "over_capacity_pct": 1.044,
                "over_capacity_lots_affected": [
                    "BHMBCCTHL01 (peak 403 / 387 bays)",
                    "BHMBCCMKT01",
                    "BHMBRCBRG01",
                    "BHMBRCBRG02",
                    "Broad Street",
                    "NIA South",
                    "Others-CCCPS105a",
                    "Others-CCCPS119a"
                ],
                "over_capacity_root_cause": "Unstriped aisle overflow parking and temporary barrier gate overrides during event peaks",
                "total_clipped_records": 385,
                "total_clipped_pct": 1.078,
                "cleaning_rule": "Enforced strict boundary clipping to [0, Nominal Capacity] without deleting rows to preserve uniform 30-min temporal continuity"
            },
            "split_protocol": {
                "strategy": "Strict Chronological Partition (Zero Future Leakage)",
                "train_pct": 70.0,
                "train_samples": 15299,
                "val_pct": 15.0,
                "val_samples": 3276,
                "test_pct": 15.0,
                "test_samples": 3293,
                "lookback_steps": 6,
                "lookback_elapsed_hours": 2.5,
                "lookback_nominal_hours": 3.0,
                "intraday_valid_windows_per_day": 11,
                "overnight_handling": "Windows strictly isolated within each single operating day; zero cross-day boundary bridging"
            },
            "feature_engineering": [
                {
                    "name": "AvailabilityRatio",
                    "type": "Target & Sequence Feature",
                    "formula": "(Capacity - Occupancy) / Capacity",
                    "range": "[0.0, 1.0]",
                    "description": "Normalized vacant bay proportion ensuring scale-invariant cross-facility generalization"
                },
                {
                    "name": "SinHour",
                    "type": "Temporal Diurnal",
                    "formula": "sin(2 * pi * Hour / 24.0)",
                    "range": "[-1.0, 1.0]",
                    "description": "Sine projection of continuous daily operating hour"
                },
                {
                    "name": "CosHour",
                    "type": "Temporal Diurnal",
                    "formula": "cos(2 * pi * Hour / 24.0)",
                    "range": "[-1.0, 1.0]",
                    "description": "Cosine projection of continuous daily operating hour"
                },
                {
                    "name": "DayOfWeek",
                    "type": "Weekly Calendar",
                    "formula": "Timestamp.dt.dayofweek / 7.0",
                    "range": "[0.0, 1.0)",
                    "description": "Normalized weekday index to separate weekend leisure from weekday commuter turnover"
                }
            ]
        }


audit_service = AuditService()
