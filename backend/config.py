import os
from pydantic import BaseModel, Field

class AppConfig(BaseModel):
    """
    Global configuration for RRIS backend.
    Centralizes environment variables and shared settings
    used across ingestion, intelligence, fusion, scoring, and API layers.
    """

    # --- Environment ---
    environment: str = Field(default=os.getenv("RRIS_ENV", "development"))

    # --- Logging ---
    log_level: str = Field(default=os.getenv("RRIS_LOG_LEVEL", "INFO"))

    # --- NWS Ingestion ---
    nws_zone: str = Field(default=os.getenv("RRIS_NWS_ZONE", "TXZ035"))
    nws_user_agent: str = Field(
        default=os.getenv("RRIS_NWS_USER_AGENT", "(RRIS_Capstone, your.email@ttu.edu)")
    )
    nws_poll_interval: int = Field(
        default=int(os.getenv("RRIS_NWS_POLL_INTERVAL", "60"))  # seconds
    )

    # --- PDF Ingestion ---
    pdf_temp_dir: str = Field(
        default=os.getenv("RRIS_PDF_TEMP_DIR", "/tmp/rris_pdf")
    )

    # --- Fusion Engine ---
    fusion_distance_threshold_m: int = Field(
        default=int(os.getenv("RRIS_FUSION_DISTANCE_THRESHOLD", "150"))
    )
    fusion_time_threshold_s: int = Field(
        default=int(os.getenv("RRIS_FUSION_TIME_THRESHOLD", "900"))  # 15 minutes
    )

    # --- Priority Scoring ---
    priority_weights: dict = Field(
        default_factory=lambda: {
            "severity": 0.45,
            "injuries": 0.25,
            "hazards": 0.15,
            "agencies_needed": 0.10,
            "confidence": 0.05,
        }
    )

    # --- Confidence Model ---
    confidence_weights: dict = Field(
        default_factory=lambda: {
            "source_reliability": 0.5,
            "recency": 0.3,
            "consistency": 0.2,
        }
    )

    # --- Explainability ---
    enable_explainability: bool = Field(
        default=bool(int(os.getenv("RRIS_EXPLAINABILITY", "1")))
    )

    # --- Simulator ---
    simulator_speed: float = Field(
        default=float(os.getenv("RRIS_SIMULATOR_SPEED", "1.0"))
    )


# Singleton-style config instance
config = AppConfig()

