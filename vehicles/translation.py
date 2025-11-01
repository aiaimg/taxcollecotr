from modeltranslation.translator import register, TranslationOptions
from .models import GrilleTarifaire

# Note: Vehicule model doesn't have translatable text fields
# Only GrilleTarifaire has fields that might need translation

# @register(GrilleTarifaire)
# class GrilleTarifaireTranslationOptions(TranslationOptions):
#     fields = ()  # No text fields to translate in current model