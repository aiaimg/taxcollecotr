"""
OCR utilities for extracting information from carte grise biométrique (Madagascar)
Uses Tesseract OCR (via tesserocr) for text extraction and pattern matching for field identification
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import tesserocr
from PIL import Image

logger = logging.getLogger(__name__)


class CarteGriseOCR:
    """
    OCR processor specifically designed for Madagascar carte grise biométrique
    """

    # Common patterns found in carte grise
    PATTERNS = {
        "plate": r"([0-9]{1,4}\s*[A-Z]{2,3})",
        "vin": r"([A-Z0-9]{8,17})",
        "date": r"(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",
        "power_cv": r"(\d+)\s*(?:CV|cv)",
        "cylindree": r"(\d+)\s*(?:cm3|CM3|cc|CC)",
    }

    # Common field labels in French (carte grise)
    FIELD_LABELS = {
        "plate": ["immatriculation", "plaque", "n°"],
        "owner": ["propriétaire", "nom", "titulaire"],
        "brand": ["marque"],
        "model": ["modèle", "model"],
        "vin": ["châssis", "vin", "numéro de série"],
        "color": ["couleur", "color"],
        "date": ["première circulation", "mise en circulation", "date"],
        "power": ["puissance", "cv"],
        "energy": ["énergie", "carburant", "essence", "diesel"],
    }

    @staticmethod
    def preprocess_image(image_path: str) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        """
        try:
            img = Image.open(image_path)

            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Resize if too small (improve OCR)
            width, height = img.size
            if width < 1000:
                scale = 1000 / width
                new_size = (int(width * scale), int(height * scale))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Convert to grayscale
            img = img.convert("L")

            # Enhance contrast
            from PIL import ImageEnhance

            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)

            return img

        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise

    @staticmethod
    def extract_text(image_path: str, lang="fra") -> str:
        """
        Extract text from image using Tesseract OCR (via tesserocr)
        """
        try:
            img = CarteGriseOCR.preprocess_image(image_path)

            # Use tesserocr API for better performance
            with tesserocr.PyTessBaseAPI(lang=lang, psm=tesserocr.PSM.AUTO) as api:
                api.SetImage(img)
                text = api.GetUTF8Text()

            return text

        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""

    @staticmethod
    def extract_plate_number(text: str) -> Optional[str]:
        """Extract plate number from text"""
        pattern = CarteGriseOCR.PATTERNS["plate"]
        matches = re.findall(pattern, text, re.IGNORECASE)

        if matches:
            # Clean and format plate number
            plate = matches[0].replace(" ", "").upper()
            return plate

        return None

    @staticmethod
    def extract_vin(text: str) -> Optional[str]:
        """Extract VIN/chassis number from text"""
        pattern = CarteGriseOCR.PATTERNS["vin"]
        matches = re.findall(pattern, text, re.IGNORECASE)

        if matches:
            return matches[0].upper()

        return None

    @staticmethod
    def extract_date(text: str) -> Optional[str]:
        """Extract date from text and convert to YYYY-MM-DD format"""
        pattern = CarteGriseOCR.PATTERNS["date"]
        matches = re.findall(pattern, text)

        if matches:
            date_str = matches[0]
            # Try different date formats
            for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

        return None

    @staticmethod
    def extract_power_cv(text: str) -> Optional[int]:
        """Extract power in CV from text"""
        pattern = CarteGriseOCR.PATTERNS["power_cv"]
        matches = re.findall(pattern, text, re.IGNORECASE)

        if matches:
            try:
                return int(matches[0])
            except ValueError:
                pass

        return None

    @staticmethod
    def extract_cylindree(text: str) -> Optional[int]:
        """Extract engine displacement (cylindrée) from text"""
        pattern = CarteGriseOCR.PATTERNS["cylindree"]
        matches = re.findall(pattern, text, re.IGNORECASE)

        if matches:
            try:
                return int(matches[0])
            except ValueError:
                pass

        return None

    @staticmethod
    def extract_field_near_label(text: str, label_keywords: list, max_distance: int = 50) -> Optional[str]:
        """
        Extract field value near a label keyword
        """
        text_lower = text.lower()

        for keyword in label_keywords:
            keyword_lower = keyword.lower()
            pos = text_lower.find(keyword_lower)

            if pos != -1:
                # Extract text after the keyword
                start = pos + len(keyword_lower)
                end = min(start + max_distance, len(text))
                value = text[start:end].strip()

                # Clean up the value
                value = re.sub(r"[:\-\s]+", " ", value).strip()

                # Take first line/word
                value = value.split("\n")[0].strip()

                if value:
                    return value

        return None

    @staticmethod
    def extract_owner_name(text: str) -> Optional[str]:
        """Extract owner name from text"""
        return CarteGriseOCR.extract_field_near_label(text, CarteGriseOCR.FIELD_LABELS["owner"])

    @staticmethod
    def extract_brand(text: str) -> Optional[str]:
        """Extract vehicle brand from text"""
        brand = CarteGriseOCR.extract_field_near_label(text, CarteGriseOCR.FIELD_LABELS["brand"])

        if brand:
            # Clean and uppercase
            brand = brand.upper().split()[0]  # Take first word
            return brand

        return None

    @staticmethod
    def extract_model(text: str) -> Optional[str]:
        """Extract vehicle model from text"""
        model = CarteGriseOCR.extract_field_near_label(text, CarteGriseOCR.FIELD_LABELS["model"])

        if model:
            return model.upper()

        return None

    @staticmethod
    def extract_color(text: str) -> Optional[str]:
        """Extract vehicle color from text"""
        return CarteGriseOCR.extract_field_near_label(text, CarteGriseOCR.FIELD_LABELS["color"])

    @staticmethod
    def detect_energy_source(text: str) -> Optional[str]:
        """Detect energy source from text"""
        text_lower = text.lower()

        if "essence" in text_lower or "gasoline" in text_lower:
            return "Essence"
        elif "diesel" in text_lower or "gasoil" in text_lower:
            return "Diesel"
        elif "électrique" in text_lower or "electric" in text_lower:
            return "Electrique"
        elif "hybride" in text_lower or "hybrid" in text_lower:
            return "Hybride"

        return None

    @staticmethod
    def process_carte_grise(image_path: str) -> Dict[str, Any]:
        """
        Main method to process carte grise and extract all information

        Returns:
            dict: Extracted information with confidence scores
        """
        try:
            # Extract text
            text = CarteGriseOCR.extract_text(image_path)

            if not text:
                return {"success": False, "error": "Impossible d'extraire le texte de l'image", "data": {}}

            # Extract all fields
            data = {
                "plaque_immatriculation": CarteGriseOCR.extract_plate_number(text),
                "vin": CarteGriseOCR.extract_vin(text),
                "nom_proprietaire": CarteGriseOCR.extract_owner_name(text),
                "marque": CarteGriseOCR.extract_brand(text),
                "modele": CarteGriseOCR.extract_model(text),
                "couleur": CarteGriseOCR.extract_color(text),
                "date_premiere_circulation": CarteGriseOCR.extract_date(text),
                "puissance_fiscale_cv": CarteGriseOCR.extract_power_cv(text),
                "cylindree_cm3": CarteGriseOCR.extract_cylindree(text),
                "source_energie": CarteGriseOCR.detect_energy_source(text),
            }

            # Calculate confidence score (percentage of fields extracted)
            total_fields = len(data)
            extracted_fields = sum(1 for v in data.values() if v is not None)
            confidence = (extracted_fields / total_fields) * 100

            return {
                "success": True,
                "confidence": round(confidence, 2),
                "data": data,
                "raw_text": text,  # For debugging
            }

        except Exception as e:
            logger.error(f"Error processing carte grise: {str(e)}")
            return {"success": False, "error": str(e), "data": {}}
