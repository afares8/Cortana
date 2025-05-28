import pandas as pd
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ExcelRiskEvaluator:
    """Risk evaluator using the Grupo Magnate legal risk matrix Excel file."""

    def __init__(self):
        self.excel_file = (
            Path(__file__).parent.parent.parent.parent.parent
            / "data"
            / "MATRIZ_JURIDICA_GRUPO_MAGNATE_ABIERTA.xlsx"
        )
        self._risk_matrices = {}
        self._load_risk_matrices()

    def _load_risk_matrices(self):
        """Load all risk matrices from Excel file."""
        try:
            client_df = pd.read_excel(self.excel_file, sheet_name="Tabla 1 Cliente")
            self._risk_matrices["client"] = self._parse_client_table(client_df)

            geo_df = pd.read_excel(
                self.excel_file, sheet_name="Tabla 2 Factor Geográfico"
            )
            self._risk_matrices["geographic"] = self._parse_geographic_table(geo_df)

            products_df = pd.read_excel(
                self.excel_file, sheet_name="Tabla 3 Producto o Servicios"
            )
            self._risk_matrices["products"] = self._parse_products_table(products_df)

            channel_df = pd.read_excel(
                self.excel_file, sheet_name="Tabla 4 Canal Vinculación"
            )
            self._risk_matrices["channel"] = self._parse_channel_table(channel_df)

            logger.info("Risk matrices loaded successfully from Excel file")
        except Exception as e:
            logger.error(f"Error loading risk matrices: {str(e)}")
            self._use_fallback_matrices()

    def _parse_client_table(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Parse client type risk table."""
        risk_map = {}
        for _, row in df.iterrows():
            if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                client_type = str(row.iloc[1]).strip()
                risk_score = self._extract_risk_score(row.iloc[2])
                risk_level = self._extract_risk_level(row.iloc[3])
                if client_type and risk_score is not None:
                    risk_map[client_type.lower()] = {
                        "score": risk_score,
                        "level": risk_level,
                    }
        return risk_map

    def _parse_geographic_table(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Parse geographic risk table."""
        risk_map = {}
        for _, row in df.iterrows():
            if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                country = str(row.iloc[1]).strip()
                risk_score = self._extract_risk_score(row.iloc[2])
                risk_level = self._extract_risk_level(row.iloc[3])
                if country and risk_score is not None:
                    risk_map[country.lower()] = {
                        "score": risk_score,
                        "level": risk_level,
                    }
        return risk_map

    def _parse_products_table(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Parse products/services risk table."""
        risk_map = {}
        for _, row in df.iterrows():
            if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                product = str(row.iloc[1]).strip()
                risk_score = self._extract_risk_score(row.iloc[2])
                risk_level = self._extract_risk_level(row.iloc[3])
                if product and risk_score is not None:
                    risk_map[product.lower()] = {
                        "score": risk_score,
                        "level": risk_level,
                    }
        return risk_map

    def _parse_channel_table(self, df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Parse channel connection risk table."""
        risk_map = {}
        for _, row in df.iterrows():
            if pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]):
                channel = str(row.iloc[1]).strip()
                risk_score = self._extract_risk_score(row.iloc[2])
                risk_level = self._extract_risk_level(row.iloc[3])
                if channel and risk_score is not None:
                    risk_map[channel.lower()] = {
                        "score": risk_score,
                        "level": risk_level,
                    }
        return risk_map

    def _extract_risk_score(self, value) -> Optional[float]:
        """Extract risk score from Excel cell value."""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                import re

                numeric_match = re.search(r"(\d+(\.\d+)?)", value)
                if numeric_match:
                    return float(numeric_match.group(1))
            return None
        except Exception:
            return None

    def _extract_risk_level(self, value) -> str:
        """Extract risk level from Excel cell value."""
        if pd.isna(value):
            return "medium"

        value_str = str(value).lower()
        if "alto" in value_str or "high" in value_str:
            return "high"
        elif "bajo" in value_str or "low" in value_str:
            return "low"
        else:
            return "medium"

    def _use_fallback_matrices(self):
        """Use fallback risk matrices if Excel file cannot be loaded."""
        logger.warning("Using fallback risk matrices")

        self._risk_matrices["client"] = {
            "individual": {"score": 1, "level": "low"},
            "empresa": {"score": 2, "level": "medium"},
            "pep": {"score": 4, "level": "high"},  # PEP clients are always high risk
            "gobierno": {"score": 3, "level": "high"},
            "ong": {"score": 2, "level": "medium"},
            "fideicomiso": {"score": 3, "level": "high"},
        }

        self._risk_matrices["geographic"] = {
            "panama": {"score": 2, "level": "medium"},
            "estados unidos": {"score": 1, "level": "low"},
            "ve": {"score": 4, "level": "high"},  # Venezuela is high risk
            "venezuela": {"score": 4, "level": "high"},
            "colombia": {"score": 2, "level": "medium"},
            "mexico": {"score": 3, "level": "medium"},
            "cuba": {"score": 4, "level": "high"},
            "iran": {"score": 4, "level": "high"},
            "corea del norte": {"score": 4, "level": "high"},
        }

        self._risk_matrices["products"] = {
            "legal": {"score": 1, "level": "low"},
            "finance": {"score": 3, "level": "high"},
            "real estate": {"score": 3, "level": "high"},
            "consulting": {"score": 2, "level": "medium"},
            "technology": {"score": 1, "level": "low"},
            "healthcare": {"score": 1, "level": "low"},
            "education": {"score": 1, "level": "low"},
            "other": {"score": 2, "level": "medium"},
        }

        self._risk_matrices["channel"] = {
            "presencial": {"score": 1, "level": "low"},
            "no presencial": {"score": 3, "level": "high"},
            "referido": {"score": 2, "level": "medium"},
            "digital": {"score": 2, "level": "medium"},
        }

    def calculate_risk(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive risk score for a client."""
        try:
            client_type = client_data.get("client_type", "individual").lower()
            country = client_data.get("country", "unknown").lower()
            industry = client_data.get("industry", "other").lower()
            channel = client_data.get("channel", "presencial").lower()

            client_risk = self._risk_matrices["client"].get(
                client_type, {"score": 2, "level": "medium"}
            )
            geo_risk = self._risk_matrices["geographic"].get(
                country, {"score": 2, "level": "medium"}
            )
            product_risk = self._risk_matrices["products"].get(
                industry, {"score": 2, "level": "medium"}
            )
            channel_risk = self._risk_matrices["channel"].get(
                channel, {"score": 1, "level": "low"}
            )

            total_score = (
                client_risk["score"] * 0.3  # Client type weight
                + geo_risk["score"] * 0.25  # Geographic weight
                + product_risk["score"] * 0.25  # Product/service weight
                + channel_risk["score"] * 0.2  # Channel weight
            )

            if client_type == "pep" or country in [
                "ve",
                "venezuela",
                "cuba",
                "iran",
                "corea del norte",
            ]:
                risk_level = "HIGH"
            elif total_score >= 3.5:
                risk_level = "HIGH"
            elif total_score >= 2.5:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            return {
                "total_score": round(total_score, 2),
                "risk_level": risk_level,
                "components": {
                    "client_type": client_risk,
                    "geographic": geo_risk,
                    "products": product_risk,
                    "channel": channel_risk,
                },
                "details": f"Risk calculated based on Excel matrix factors",
            }
        except Exception as e:
            logger.error(f"Error calculating risk: {str(e)}")
            return {"total_score": 2.0, "risk_level": "MEDIUM", "error": str(e)}


excel_risk_evaluator = ExcelRiskEvaluator()
