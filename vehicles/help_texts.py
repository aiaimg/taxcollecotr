"""
Textes d'aide contextuels pour les formulaires de déclaration de véhicules.
Support multilingue (FR/MG) avec exemples concrets et références légales.
"""

# Textes d'aide courts (tooltips)
HELP_TEXTS_SHORT = {
    # Champs communs
    "marque": {
        "fr": "Constructeur du véhicule (ex: Toyota, Peugeot, Boeing)",
        "mg": "Mpanamboatra ny fiara (ohatra: Toyota, Peugeot, Boeing)",
    },
    "modele": {
        "fr": "Modèle exact du véhicule (ex: Corolla, 208, 737)",
        "mg": "Modely marina ny fiara (ohatra: Corolla, 208, 737)",
    },
    "date_premiere_circulation": {
        "fr": "Date de première mise en circulation ou en service",
        "mg": "Daty voalohany nampiasana ny fiara",
    },
    # Champs terrestres
    "plaque_immatriculation": {
        "fr": "Numéro de plaque d'immatriculation (ex: 1234 TAA)",
        "mg": "Laharana fanamarihana (ohatra: 1234 TAA)",
    },
    "puissance_fiscale_cv": {
        "fr": "Puissance fiscale en chevaux (CV) - voir carte grise",
        "mg": "Herin'ny fiara amin'ny CV - jereo ny carte grise",
    },
    "cylindree_cm3": {
        "fr": "Cylindrée du moteur en cm³ (ex: 1500, 2000)",
        "mg": "Haben'ny motera amin'ny cm³ (ohatra: 1500, 2000)",
    },
    "source_energie": {"fr": "Type de carburant ou d'énergie utilisé", "mg": "Karazana solika na angovo ampiasaina"},
    # Champs aériens
    "immatriculation_aerienne": {
        "fr": "Numéro d'immatriculation aérienne (ex: 5R-ABC pour Madagascar)",
        "mg": "Laharana fanamarihana an-habakabaka (ohatra: 5R-ABC ho an'i Madagasikara)",
    },
    "masse_maximale_decollage_kg": {
        "fr": "Masse maximale au décollage en kilogrammes (MTOW)",
        "mg": "Lanjan-javatra lehibe indrindra amin'ny fiaingana (kg)",
    },
    "numero_serie_aeronef": {
        "fr": "Numéro de série du constructeur (MSN)",
        "mg": "Laharana andian-dahatsoratra avy amin'ny mpanamboatra",
    },
    # Champs maritimes
    "numero_francisation": {
        "fr": "Numéro de francisation du navire (délivré par les Affaires Maritimes)",
        "mg": "Laharana francisation ny sambo (nomen'ny Affaires Maritimes)",
    },
    "nom_navire": {"fr": "Nom officiel du navire ou de l'embarcation", "mg": "Anarana ofisialy ny sambo na lakana"},
    "longueur_metres": {
        "fr": "Longueur hors-tout en mètres (ex: 7.5, 12.0)",
        "mg": "Halavany manontolo amin'ny metatra (ohatra: 7.5, 12.0)",
    },
    "tonnage_tonneaux": {
        "fr": "Tonnage brut en tonneaux (voir certificat de jaugeage)",
        "mg": "Lanjan-javatra amin'ny tonneaux (jereo ny certificat de jaugeage)",
    },
    "puissance_moteur_kw": {
        "fr": "Puissance du moteur en kilowatts (kW)",
        "mg": "Herin'ny motera amin'ny kilowatts (kW)",
    },
    "puissance_moteur_unit": {
        "fr": "Unité de mesure de la puissance (CV ou kW)",
        "mg": "Fandrefesana ny hery (CV na kW)",
    },
}

# Textes d'aide détaillés (modals)
HELP_TEXTS_DETAILED = {
    # Champs terrestres
    "plaque_immatriculation": {
        "fr": {
            "title": "Plaque d'immatriculation",
            "description": "Le numéro de plaque d'immatriculation est l'identifiant unique de votre véhicule terrestre.",
            "examples": ["1234 TAA (format standard Madagascar)", "5678 TBB", "ABC 123 (ancien format)"],
            "legal_reference": "Article 3 du Code de la Route - Obligation d'immatriculation",
            "validation_rules": [
                "Format: 4 chiffres + 3 lettres",
                "Lettres en majuscules",
                "Espaces autorisés mais pas obligatoires",
            ],
        },
        "mg": {
            "title": "Laharana fanamarihana",
            "description": "Ny laharana fanamarihana no famantarana manokana ny fiaranao.",
            "examples": ["1234 TAA (endrika mahazatra Madagasikara)", "5678 TBB", "ABC 123 (endrika taloha)"],
            "legal_reference": "Andininy faha-3 amin'ny Code de la Route",
            "validation_rules": ["Endrika: isa 4 + litera 3", "Litera lehibe", "Toerana azoko atao fa tsy tsy maintsy"],
        },
    },
    "puissance_fiscale_cv": {
        "fr": {
            "title": "Puissance fiscale (CV)",
            "description": "La puissance fiscale est utilisée pour calculer le montant de votre taxe annuelle. Elle est indiquée sur votre carte grise.",
            "examples": [
                "4 CV - Petite voiture",
                "8 CV - Voiture moyenne",
                "12 CV - Grosse voiture ou 4x4",
                "20 CV - Véhicule utilitaire",
            ],
            "legal_reference": "PLFI 2026 - Grille tarifaire progressive basée sur la puissance",
            "validation_rules": [
                "Valeur entre 1 et 50 CV",
                "Doit correspondre à la carte grise",
                "Cohérence avec la cylindrée vérifiée",
            ],
        },
        "mg": {
            "title": "Herin'ny fiara (CV)",
            "description": "Ny herin'ny fiara no ampiasaina amin'ny kajy ny hetra isan-taona. Hita ao amin'ny carte grise izany.",
            "examples": [
                "4 CV - Fiara kely",
                "8 CV - Fiara antonony",
                "12 CV - Fiara lehibe na 4x4",
                "20 CV - Fiara fitaterana entana",
            ],
            "legal_reference": "PLFI 2026 - Tarehimarika miankina amin'ny hery",
            "validation_rules": [
                "Sanda eo anelanelan'ny 1 sy 50 CV",
                "Tsy maintsy mifanaraka amin'ny carte grise",
                "Mifanaraka amin'ny haben'ny motera",
            ],
        },
    },
    "source_energie": {
        "fr": {
            "title": "Source d'énergie",
            "description": "Le type de carburant ou d'énergie influence le montant de la taxe. Les véhicules électriques bénéficient de tarifs réduits.",
            "examples": [
                "Essence - Tarif standard",
                "Diesel - Tarif standard",
                "Électrique - Tarif réduit de 50%",
                "Hybride - Tarif réduit de 25%",
            ],
            "legal_reference": "PLFI 2026 - Article sur les incitations écologiques",
            "validation_rules": ["Choix unique parmi les options", "Doit correspondre au type de moteur"],
        },
        "mg": {
            "title": "Loharanon'angovo",
            "description": "Ny karazana solika na angovo dia misy fiantraikany amin'ny hetra. Ny fiara elektrika dia mahazo fihenam-bidy.",
            "examples": [
                "Essence - Vidim-pitateram-barotra mahazatra",
                "Diesel - Vidim-pitateram-barotra mahazatra",
                "Électrique - Fihenam-bidy 50%",
                "Hybride - Fihenam-bidy 25%",
            ],
            "legal_reference": "PLFI 2026 - Andininy momba ny fandrisihana ara-tontolo iainana",
            "validation_rules": ["Safidy tokana amin'ny safidy", "Tsy maintsy mifanaraka amin'ny karazana motera"],
        },
    },
    # Champs aériens
    "immatriculation_aerienne": {
        "fr": {
            "title": "Immatriculation aérienne",
            "description": "Numéro d'immatriculation unique de l'aéronef, délivré par l'autorité de l'aviation civile.",
            "examples": [
                "5R-ABC - Format Madagascar (5R + 3 lettres)",
                "5R-MFG",
                "F-GXYZ - Format France (pour référence)",
            ],
            "legal_reference": "Convention de Chicago - Annexe 7 (Marques de nationalité)",
            "validation_rules": ["Format: 5R-XXX pour Madagascar", "Lettres en majuscules", "Tiret obligatoire"],
        },
        "mg": {
            "title": "Laharana fanamarihana an-habakabaka",
            "description": "Laharana manokana ny fiaramanidina, nomen'ny manam-pahefana momba ny fiaramanidina sivily.",
            "examples": [
                "5R-ABC - Endrika Madagasikara (5R + litera 3)",
                "5R-MFG",
                "F-GXYZ - Endrika Frantsa (ho fampitahana)",
            ],
            "legal_reference": "Fifanarahana Chicago - Annexe 7",
            "validation_rules": ["Endrika: 5R-XXX ho an'i Madagasikara", "Litera lehibe", "Tiret tsy maintsy misy"],
        },
    },
    "masse_maximale_decollage_kg": {
        "fr": {
            "title": "Masse maximale au décollage (MTOW)",
            "description": "Poids maximum autorisé de l'aéronef au moment du décollage, incluant le carburant, les passagers et le fret.",
            "examples": [
                "600 kg - Petit avion de tourisme (Cessna 172)",
                "2,300 kg - Avion léger (Piper PA-28)",
                "79,000 kg - Avion commercial moyen (Boeing 737)",
                "560,000 kg - Gros porteur (Airbus A380)",
            ],
            "legal_reference": "PLFI 2026 - Taxe forfaitaire de 2,000,000 Ar pour tous aéronefs",
            "validation_rules": [
                "Valeur entre 10 kg et 500,000 kg",
                "Doit correspondre au certificat de navigabilité",
                "Exprimée en kilogrammes",
            ],
        },
        "mg": {
            "title": "Lanjan-javatra lehibe indrindra amin'ny fiaingana (MTOW)",
            "description": "Lanjan-javatra ambony indrindra azon'ny fiaramanidina amin'ny fotoana fiaingana, miaraka amin'ny solika, mpandeha ary entana.",
            "examples": [
                "600 kg - Fiaramanidina kely (Cessna 172)",
                "2,300 kg - Fiaramanidina maivana (Piper PA-28)",
                "79,000 kg - Fiaramanidina ara-barotra antonony (Boeing 737)",
                "560,000 kg - Fiaramanidina lehibe (Airbus A380)",
            ],
            "legal_reference": "PLFI 2026 - Hetra raikitra 2,000,000 Ar ho an'ny fiaramanidina rehetra",
            "validation_rules": [
                "Sanda eo anelanelan'ny 10 kg sy 500,000 kg",
                "Tsy maintsy mifanaraka amin'ny certificat de navigabilité",
                "Aseho amin'ny kilogrammes",
            ],
        },
    },
    # Champs maritimes
    "numero_francisation": {
        "fr": {
            "title": "Numéro de francisation",
            "description": "Numéro d'identification unique du navire, délivré par les Affaires Maritimes. Équivalent de la carte grise pour les bateaux.",
            "examples": ["MG-2024-001234", "TAN-2023-5678", "Format variable selon le port d'attache"],
            "legal_reference": "Code Maritime - Article sur l'immatriculation des navires",
            "validation_rules": [
                "Format défini par les Affaires Maritimes",
                "Doit être unique dans le système",
                "Obligatoire pour tous navires motorisés",
            ],
        },
        "mg": {
            "title": "Laharana francisation",
            "description": "Laharana manokana ny sambo, nomen'ny Affaires Maritimes. Mitovy amin'ny carte grise ho an'ny sambo.",
            "examples": ["MG-2024-001234", "TAN-2023-5678", "Endrika miovaova arakaraka ny seranan-tsambo"],
            "legal_reference": "Code Maritime - Andininy momba ny fanamarika sambo",
            "validation_rules": [
                "Endrika voafaritry ny Affaires Maritimes",
                "Tsy maintsy manokana ao amin'ny rafitra",
                "Tsy maintsy misy ho an'ny sambo misy motera rehetra",
            ],
        },
    },
    "longueur_metres": {
        "fr": {
            "title": "Longueur du navire",
            "description": "Longueur hors-tout du navire en mètres. Ce critère détermine la catégorie tarifaire (seuil: 7 mètres).",
            "examples": [
                "5.5 m - Petit bateau de plaisance (< 7m = 1,000,000 Ar)",
                "8.0 m - Bateau de plaisance (≥ 7m = 200,000 Ar)",
                "12.5 m - Yacht",
                "25.0 m - Navire de commerce",
            ],
            "legal_reference": "PLFI 2026 - Seuil de 7m pour classification maritime",
            "validation_rules": [
                "Valeur entre 1 m et 400 m",
                "Exprimée en mètres avec 2 décimales",
                "Seuil important: ≥ 7m = tarif réduit (200,000 Ar)",
            ],
        },
        "mg": {
            "title": "Halavan'ny sambo",
            "description": "Halavany manontolo ny sambo amin'ny metatra. Io fepetra io no mamaritra ny sokajy hetra (fetra: metatra 7).",
            "examples": [
                "5.5 m - Sambo kely (< 7m = 1,000,000 Ar)",
                "8.0 m - Sambo fialam-boly (≥ 7m = 200,000 Ar)",
                "12.5 m - Yacht",
                "25.0 m - Sambo ara-barotra",
            ],
            "legal_reference": "PLFI 2026 - Fetra 7m ho an'ny fanasokajiana sambo",
            "validation_rules": [
                "Sanda eo anelanelan'ny 1 m sy 400 m",
                "Aseho amin'ny metatra miaraka amin'ny desimal 2",
                "Fetra manan-danja: ≥ 7m = hetra ambany (200,000 Ar)",
            ],
        },
    },
    "puissance_moteur_maritime": {
        "fr": {
            "title": "Puissance du moteur maritime",
            "description": "Puissance du moteur en CV ou kW. Ce critère détermine la catégorie tarifaire (seuils: 22 CV ou 90 kW).",
            "examples": [
                "15 CV (11 kW) - Petit moteur (< 22 CV = 1,000,000 Ar)",
                "25 CV (18.4 kW) - Moteur moyen (≥ 22 CV = 200,000 Ar)",
                "100 kW (136 CV) - Gros moteur",
                "95 kW - Jet-ski (≥ 90 kW = 200,000 Ar)",
            ],
            "legal_reference": "PLFI 2026 - Seuils: 22 CV ou 90 kW pour classification",
            "validation_rules": [
                "Conversion automatique: 1 CV = 0.735 kW",
                "Conversion inverse: 1 kW = 1.36 CV",
                "Seuils importants: ≥ 22 CV ou ≥ 90 kW = tarif réduit",
                "Jet-ski: ≥ 90 kW = 200,000 Ar",
            ],
        },
        "mg": {
            "title": "Herin'ny motera an-dranomasina",
            "description": "Herin'ny motera amin'ny CV na kW. Io fepetra io no mamaritra ny sokajy hetra (fetra: 22 CV na 90 kW).",
            "examples": [
                "15 CV (11 kW) - Motera kely (< 22 CV = 1,000,000 Ar)",
                "25 CV (18.4 kW) - Motera antonony (≥ 22 CV = 200,000 Ar)",
                "100 kW (136 CV) - Motera lehibe",
                "95 kW - Jet-ski (≥ 90 kW = 200,000 Ar)",
            ],
            "legal_reference": "PLFI 2026 - Fetra: 22 CV na 90 kW ho an'ny fanasokajiana",
            "validation_rules": [
                "Fiovam-po mandeha ho azy: 1 CV = 0.735 kW",
                "Fiovam-po mivadika: 1 kW = 1.36 CV",
                "Fetra manan-danja: ≥ 22 CV na ≥ 90 kW = hetra ambany",
                "Jet-ski: ≥ 90 kW = 200,000 Ar",
            ],
        },
    },
}

# Textes pour les étapes de progression
PROGRESS_STEPS = {
    "fr": [
        {"id": "basic_info", "label": "Informations de base", "description": "Identité du véhicule et du propriétaire"},
        {"id": "characteristics", "label": "Caractéristiques", "description": "Spécifications techniques du véhicule"},
        {"id": "documents", "label": "Documents", "description": "Justificatifs requis"},
        {"id": "review", "label": "Révision", "description": "Vérification et soumission"},
    ],
    "mg": [
        {"id": "basic_info", "label": "Fampahalalana fototra", "description": "Mombamomba ny fiara sy ny tompony"},
        {"id": "characteristics", "label": "Toetra", "description": "Famaritana ara-teknika ny fiara"},
        {"id": "documents", "label": "Antontan-taratasy", "description": "Antontan-taratasy ilaina"},
        {"id": "review", "label": "Fanamarinana", "description": "Fanamarinana sy fandefasana"},
    ],
}


# Documents requis par catégorie
REQUIRED_DOCUMENTS = {
    "TERRESTRE": {
        "fr": [
            {
                "type": "carte_grise",
                "label": "Carte grise (recto/verso)",
                "description": "Certificat d'immatriculation du véhicule",
                "mandatory": True,
            },
            {
                "type": "assurance",
                "label": "Attestation d'assurance",
                "description": "Assurance responsabilité civile en cours de validité",
                "mandatory": True,
            },
            {
                "type": "controle_technique",
                "label": "Contrôle technique",
                "description": "Certificat de contrôle technique (si véhicule > 4 ans)",
                "mandatory": False,
            },
            {
                "type": "photo_plaque",
                "label": "Photo de la plaque",
                "description": "Photo claire de la plaque d'immatriculation",
                "mandatory": False,
            },
        ],
        "mg": [
            {
                "type": "carte_grise",
                "label": "Carte grise (recto/verso)",
                "description": "Taratasy fanamarika ny fiara",
                "mandatory": True,
            },
            {
                "type": "assurance",
                "label": "Fanamarinana fiantohana",
                "description": "Fiantohana andraikitra sivily mbola manankery",
                "mandatory": True,
            },
            {
                "type": "controle_technique",
                "label": "Fizahana ara-teknika",
                "description": "Taratasy fanamarinana ara-teknika (raha fiara > 4 taona)",
                "mandatory": False,
            },
            {
                "type": "photo_plaque",
                "label": "Sarin'ny plaque",
                "description": "Sary mazava ny plaque fanamarika",
                "mandatory": False,
            },
        ],
    },
    "AERIEN": {
        "fr": [
            {
                "type": "certificat_navigabilite",
                "label": "Certificat de navigabilité",
                "description": "Certificat de navigabilité en cours de validité",
                "mandatory": True,
            },
            {
                "type": "certificat_immatriculation_aerienne",
                "label": "Certificat d'immatriculation",
                "description": "Certificat d'immatriculation aérienne",
                "mandatory": True,
            },
            {
                "type": "assurance_aerienne",
                "label": "Assurance aérienne",
                "description": "Assurance responsabilité civile aérienne",
                "mandatory": True,
            },
            {
                "type": "carnet_vol",
                "label": "Carnet de vol",
                "description": "Carnet de vol de l'aéronef (optionnel)",
                "mandatory": False,
            },
        ],
        "mg": [
            {
                "type": "certificat_navigabilite",
                "label": "Taratasy fahafahana manidina",
                "description": "Taratasy fahafahana manidina mbola manankery",
                "mandatory": True,
            },
            {
                "type": "certificat_immatriculation_aerienne",
                "label": "Taratasy fanamarika",
                "description": "Taratasy fanamarika an-habakabaka",
                "mandatory": True,
            },
            {
                "type": "assurance_aerienne",
                "label": "Fiantohana an-habakabaka",
                "description": "Fiantohana andraikitra sivily an-habakabaka",
                "mandatory": True,
            },
            {
                "type": "carnet_vol",
                "label": "Boky sidina",
                "description": "Boky sidina ny fiaramanidina (tsy tsy maintsy)",
                "mandatory": False,
            },
        ],
    },
    "MARITIME": {
        "fr": [
            {
                "type": "certificat_francisation",
                "label": "Certificat de francisation",
                "description": "Certificat de francisation du navire",
                "mandatory": True,
            },
            {
                "type": "permis_navigation",
                "label": "Permis de navigation",
                "description": "Permis de navigation en cours de validité",
                "mandatory": True,
            },
            {
                "type": "assurance_maritime",
                "label": "Assurance maritime",
                "description": "Assurance responsabilité civile maritime",
                "mandatory": True,
            },
            {
                "type": "certificat_jaugeage",
                "label": "Certificat de jaugeage",
                "description": "Certificat de jaugeage (pour navires > 10m)",
                "mandatory": False,
            },
        ],
        "mg": [
            {
                "type": "certificat_francisation",
                "label": "Taratasy francisation",
                "description": "Taratasy francisation ny sambo",
                "mandatory": True,
            },
            {
                "type": "permis_navigation",
                "label": "Fahazoan-dalana mandeha an-dranomasina",
                "description": "Fahazoan-dalana mandeha an-dranomasina mbola manankery",
                "mandatory": True,
            },
            {
                "type": "assurance_maritime",
                "label": "Fiantohana an-dranomasina",
                "description": "Fiantohana andraikitra sivily an-dranomasina",
                "mandatory": True,
            },
            {
                "type": "certificat_jaugeage",
                "label": "Taratasy fandrefesana",
                "description": "Taratasy fandrefesana (ho an'ny sambo > 10m)",
                "mandatory": False,
            },
        ],
    },
}


def get_help_text(field_name, language="fr", detailed=False):
    """
    Récupère le texte d'aide pour un champ donné.

    Args:
        field_name: Nom du champ
        language: Langue ('fr' ou 'mg')
        detailed: Si True, retourne l'aide détaillée, sinon l'aide courte

    Returns:
        str ou dict: Texte d'aide ou None si non trouvé
    """
    if detailed:
        return HELP_TEXTS_DETAILED.get(field_name, {}).get(language)
    else:
        return HELP_TEXTS_SHORT.get(field_name, {}).get(language)


def get_required_documents(vehicle_category, language="fr"):
    """
    Récupère la liste des documents requis pour une catégorie de véhicule.

    Args:
        vehicle_category: Catégorie du véhicule ('TERRESTRE', 'AERIEN', 'MARITIME')
        language: Langue ('fr' ou 'mg')

    Returns:
        list: Liste des documents requis
    """
    return REQUIRED_DOCUMENTS.get(vehicle_category, {}).get(language, [])


def get_progress_steps(language="fr"):
    """
    Récupère les étapes de progression.

    Args:
        language: Langue ('fr' ou 'mg')

    Returns:
        list: Liste des étapes
    """
    return PROGRESS_STEPS.get(language, [])
