"""
Utilitaires pour la gestion des véhicules
Contient la logique de conversion entre cylindrée (Cm3) et puissance fiscale (CV)
"""

def get_puissance_fiscale_from_cylindree(cylindree_cm3):
    """
    Détermine la puissance fiscale (CV) à partir de la cylindrée (Cm3)
    basé sur la grille tarifaire officielle.
    
    Args:
        cylindree_cm3 (int): Cylindrée en cm³
        
    Returns:
        int: Puissance fiscale suggérée (borne inférieure de la plage)
        None: Si la cylindrée est invalide
        
    CORRESPONDANCES OFFICIELLES :
    - De 1 à 4 CV = 0 à 250 Cm3
    - De 5 à 9 CV = 251 à 500 Cm3  
    - De 10 à 12 CV = 501 à 1000 Cm3
    - De 13 à 15 CV = Supérieure à 1000 Cm3
    - Supérieure à 15 CV = (véhicules très puissants)
    """
    if cylindree_cm3 is None or cylindree_cm3 <= 0:
        return None
        
    if 0 <= cylindree_cm3 <= 250:
        return 1  # Plage 1-4 CV
    elif 251 <= cylindree_cm3 <= 500:
        return 5  # Plage 5-9 CV
    elif 501 <= cylindree_cm3 <= 1000:
        return 10  # Plage 10-12 CV
    elif cylindree_cm3 > 1000:
        return 13  # Plage 13-15 CV (et plus)
    
    return None


def get_plage_cv_description(cylindree_cm3):
    """
    Retourne une description textuelle de la plage de CV correspondant à une cylindrée
    
    Args:
        cylindree_cm3 (int): Cylindrée en cm³
        
    Returns:
        str: Description de la plage de CV
    """
    if cylindree_cm3 is None or cylindree_cm3 <= 0:
        return "Cylindrée invalide"
        
    if 0 <= cylindree_cm3 <= 250:
        return "1 à 4 CV"
    elif 251 <= cylindree_cm3 <= 500:
        return "5 à 9 CV"
    elif 501 <= cylindree_cm3 <= 1000:
        return "10 à 12 CV"
    elif cylindree_cm3 > 1000:
        return "13 CV et plus"
    
    return "Plage inconnue"


def get_plage_cv_complete(cylindree_cm3):
    """
    Retourne la plage complète de CV (min, max) pour une cylindrée donnée
    
    Args:
        cylindree_cm3 (int): Cylindrée en cm³
        
    Returns:
        tuple: (cv_min, cv_max, description) ou None si invalide
    """
    if cylindree_cm3 is None or cylindree_cm3 <= 0:
        return None
        
    if 0 <= cylindree_cm3 <= 250:
        return (1, 4, "De 1 à 4 CV")
    elif 251 <= cylindree_cm3 <= 500:
        return (5, 9, "De 5 à 9 CV")
    elif 501 <= cylindree_cm3 <= 1000:
        return (10, 12, "De 10 à 12 CV")
    elif cylindree_cm3 > 1000:
        return (13, 15, "De 13 à 15 CV")
    
    return None


def get_conversion_info(cylindree_cm3):
    """
    Retourne toutes les informations de conversion pour une cylindrée
    
    Args:
        cylindree_cm3 (int): Cylindrée en cm³
        
    Returns:
        dict: Informations complètes de conversion
    """
    if cylindree_cm3 is None or cylindree_cm3 <= 0:
        return {
            'valid': False,
            'message': 'Cylindrée invalide'
        }
    
    plage_info = get_plage_cv_complete(cylindree_cm3)
    cv_suggere = get_puissance_fiscale_from_cylindree(cylindree_cm3)
    exemples = get_exemples_vehicules_par_cylindree(cylindree_cm3)
    
    if plage_info:
        cv_min, cv_max, description = plage_info
        return {
            'valid': True,
            'cylindree': cylindree_cm3,
            'cv_min': cv_min,
            'cv_max': cv_max,
            'cv_suggere': cv_suggere,
            'plage_description': description,
            'message': f"Pour {cylindree_cm3}cm³, la puissance fiscale est généralement {description}",
            'exemples_vehicules': exemples,
            'conseil': f"Nous suggérons {cv_suggere} CV comme valeur de départ"
        }
    
    return {
        'valid': False,
        'message': 'Impossible de déterminer la plage de CV'
    }


def get_exemples_vehicules_par_cylindree(cylindree_cm3):
    """
    Retourne des exemples de véhicules typiques pour une cylindrée donnée
    
    Args:
        cylindree_cm3 (int): Cylindrée en cm³
        
    Returns:
        list: Liste d'exemples de véhicules
    """
    if cylindree_cm3 is None or cylindree_cm3 <= 0:
        return []
        
    if 0 <= cylindree_cm3 <= 250:
        return ["Scooter 125cc", "Moto légère", "Cyclomoteur"]
    elif 251 <= cylindree_cm3 <= 500:
        return ["Moto moyenne cylindrée", "Scooter 400cc"]
    elif 501 <= cylindree_cm3 <= 1000:
        return ["Petite voiture", "Moto sportive"]
    elif 1001 <= cylindree_cm3 <= 1600:
        return ["Voiture compacte", "Berline moyenne"]
    elif 1601 <= cylindree_cm3 <= 2500:
        return ["Berline", "SUV moyen"]
    elif cylindree_cm3 > 2500:
        return ["Grosse berline", "SUV", "Véhicule de luxe"]
    
    return []


def valider_coherence_cylindree_cv(cylindree_cm3, puissance_fiscale_cv):
    """
    Valide la cohérence entre la cylindrée et la puissance fiscale saisies
    
    Args:
        cylindree_cm3 (int): Cylindrée en cm³
        puissance_fiscale_cv (int): Puissance fiscale en CV
        
    Returns:
        tuple: (bool, str) - (est_coherent, message_erreur)
    """
    if cylindree_cm3 is None or puissance_fiscale_cv is None:
        return False, "Cylindrée et puissance fiscale sont requises"
    
    cv_suggere = get_puissance_fiscale_from_cylindree(cylindree_cm3)
    plage_description = get_plage_cv_description(cylindree_cm3)
    
    # Vérification des plages
    if 0 <= cylindree_cm3 <= 250 and not (1 <= puissance_fiscale_cv <= 4):
        return False, f"Pour une cylindrée de {cylindree_cm3}cm³, la puissance fiscale devrait être entre 1 et 4 CV"
    elif 251 <= cylindree_cm3 <= 500 and not (5 <= puissance_fiscale_cv <= 9):
        return False, f"Pour une cylindrée de {cylindree_cm3}cm³, la puissance fiscale devrait être entre 5 et 9 CV"
    elif 501 <= cylindree_cm3 <= 1000 and not (10 <= puissance_fiscale_cv <= 12):
        return False, f"Pour une cylindrée de {cylindree_cm3}cm³, la puissance fiscale devrait être entre 10 et 12 CV"
    elif cylindree_cm3 > 1000 and puissance_fiscale_cv < 13:
        return False, f"Pour une cylindrée de {cylindree_cm3}cm³, la puissance fiscale devrait être d'au moins 13 CV"
    
    return True, "Cohérence validée"