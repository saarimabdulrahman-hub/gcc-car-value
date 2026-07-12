from dataclasses import dataclass

@dataclass
class MonitoringConfig:
    psi_threshold_warning: float = 0.1
    psi_threshold_critical: float = 0.2
    mae_degradation_threshold: float = 0.30      # 30% increase
    mape_degradation_threshold: float = 0.30
    min_samples_for_drift: int = 100
    rolling_window_days: int = 7
    retraining_min_interval_days: int = 7
    report_daily_hour: int = 6
    report_weekly_day: str = "Monday"
