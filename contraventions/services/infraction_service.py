"""
Service de gestion du catalogue des infractions.
"""

from decimal import Decimal

from django.db import transaction

from contraventions.models import TypeInfraction


class InfractionService:
    """Service pour gérer les types d'infractions"""

    @staticmethod
    @transaction.atomic
    def importer_infractions_loi_2017():
        """
        Importe les 24 types d'infractions de la Loi n°2017-002.
        Utilise les données du fichier infractions_loi_articles_complet.md
        """
        infractions_data = [
            # DÉLITS ROUTIERS GRAVES (7 types)
            {
                "nom": "Conduite en état d'ivresse ou stupéfiants",
                "article_code": "L7.1-1",
                "categorie": "DELIT_GRAVE",
                "montant_min_ariary": Decimal("100000"),
                "montant_max_ariary": Decimal("400000"),
                "montant_variable": False,
                "sanctions_administratives": "Suspension/retrait permis, immobilisation véhicule",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Refus de vérification (alcoolémie)",
                "article_code": "L7.1-2",
                "categorie": "DELIT_GRAVE",
                "montant_min_ariary": Decimal("200000"),
                "montant_max_ariary": Decimal("800000"),
                "montant_variable": False,
                "sanctions_administratives": "Retrait/suspension permis, immobilisation",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Conduite sans permis en état d'ivresse",
                "article_code": "L7.1-3",
                "categorie": "DELIT_GRAVE",
                "montant_min_ariary": Decimal("200000"),
                "montant_max_ariary": Decimal("800000"),
                "montant_variable": False,
                "sanctions_administratives": "Emprisonnement 1-12 mois, interdiction permis",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "1-12 mois",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Délit de fuite (accident)",
                "article_code": "L7.1-5",
                "categorie": "DELIT_GRAVE",
                "montant_min_ariary": Decimal("500000"),
                "montant_max_ariary": Decimal("2000000"),
                "montant_variable": False,
                "sanctions_administratives": "Emprisonnement 2-12 mois, retrait permis",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "2-12 mois",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Refus d'obtempérer aux ordres",
                "article_code": "L7.1-7",
                "categorie": "DELIT_GRAVE",
                "montant_min_ariary": Decimal("200000"),
                "montant_max_ariary": Decimal("800000"),
                "montant_variable": False,
                "sanctions_administratives": "Retrait/suspension permis, immobilisation",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Non-respect distance de sécurité",
                "article_code": "L7.2-4",
                "categorie": "DELIT_GRAVE",
                "montant_min_ariary": Decimal("200000"),
                "montant_max_ariary": Decimal("800000"),
                "montant_variable": False,
                "sanctions_administratives": "Suspension permis si accident corporel",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": Decimal("200000"),
                "penalite_recidive_pct": Decimal("30.00"),
            },
            {
                "nom": "Excès de vitesse",
                "article_code": "L7.2-5",
                "categorie": "DELIT_GRAVE",
                "montant_min_ariary": Decimal("200000"),
                "montant_max_ariary": Decimal("800000"),
                "montant_variable": False,
                "sanctions_administratives": "Retrait/suspension permis",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": Decimal("200000"),
                "penalite_recidive_pct": Decimal("30.00"),
            },
            # INFRACTIONS DE CIRCULATION (7 types)
            {
                "nom": "Course/compétition non autorisée",
                "article_code": "L7.2-6",
                "categorie": "CIRCULATION",
                "montant_min_ariary": Decimal("400000"),
                "montant_max_ariary": Decimal("800000"),
                "montant_variable": False,
                "sanctions_administratives": "Emprisonnement 1-6 mois possible",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "1-6 mois",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Mise en danger d'autrui",
                "article_code": "L7.2-3",
                "categorie": "CIRCULATION",
                "montant_min_ariary": Decimal("200000"),
                "montant_max_ariary": Decimal("1500000"),
                "montant_variable": False,
                "sanctions_administratives": "Emprisonnement 1-6 mois possible",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "1-6 mois",
                "penalite_accident_ariary": Decimal("500000"),
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Obstacle sur voie publique",
                "article_code": "L7.2-3",
                "categorie": "CIRCULATION",
                "montant_min_ariary": Decimal("200000"),
                "montant_max_ariary": Decimal("1500000"),
                "montant_variable": False,
                "sanctions_administratives": "Emprisonnement 3-24 mois possible",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "3-24 mois",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("30.00"),
            },
            {
                "nom": "Violation feux rouges/signalisation",
                "article_code": "L7.1-1, L7.2-1",
                "categorie": "CIRCULATION",
                "montant_min_ariary": Decimal("50000"),
                "montant_max_ariary": Decimal("200000"),
                "montant_variable": True,
                "sanctions_administratives": "Mise en fourrière possible",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": Decimal("100000"),
                "penalite_recidive_pct": Decimal("30.00"),
            },
            {
                "nom": "Destruction patrimoine routier",
                "article_code": "L7.2-3",
                "categorie": "CIRCULATION",
                "montant_min_ariary": Decimal("200000"),
                "montant_max_ariary": Decimal("800000"),
                "montant_variable": False,
                "sanctions_administratives": "Application Code pénal art. 473-474",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("30.00"),
            },
            {
                "nom": "Chargement mal arrimé/débordant",
                "article_code": "L7.2-8",
                "categorie": "CIRCULATION",
                "montant_min_ariary": Decimal("50000"),
                "montant_max_ariary": Decimal("300000"),
                "montant_variable": True,
                "sanctions_administratives": "Avertissement/immobilisation",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": Decimal("100000"),
                "penalite_recidive_pct": Decimal("20.00"),
            },
            {
                "nom": "Stationnement interdit",
                "article_code": "L7.2-7",
                "categorie": "CIRCULATION",
                "montant_min_ariary": Decimal("12000"),
                "montant_max_ariary": Decimal("600000"),
                "montant_variable": True,
                "sanctions_administratives": "Immobilisation par taquets d'arrêt",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("20.00"),
            },
            # INFRACTIONS DOCUMENTAIRES (6 types)
            {
                "nom": "Défaut de carte grise",
                "article_code": "L7.4-1",
                "categorie": "DOCUMENTAIRE",
                "montant_min_ariary": Decimal("50000"),
                "montant_max_ariary": Decimal("200000"),
                "montant_variable": True,
                "sanctions_administratives": "Mise en fourrière 10 jours minimum",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("30.00"),
            },
            {
                "nom": "Défaut de permis de conduire",
                "article_code": "L7.5-1",
                "categorie": "DOCUMENTAIRE",
                "montant_min_ariary": Decimal("100000"),
                "montant_max_ariary": Decimal("300000"),
                "montant_variable": True,
                "sanctions_administratives": "Mise en fourrière + poursuites pénales",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Défaut d'assurance",
                "article_code": "L7.4-5",
                "categorie": "DOCUMENTAIRE",
                "montant_min_ariary": Decimal("100000"),
                "montant_max_ariary": Decimal("500000"),
                "montant_variable": False,
                "sanctions_administratives": "Mise en fourrière, retrait permis si accident",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": Decimal("500000"),
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Défaut de visite technique",
                "article_code": "L7.4-1",
                "categorie": "DOCUMENTAIRE",
                "montant_min_ariary": Decimal("50000"),
                "montant_max_ariary": Decimal("150000"),
                "montant_variable": True,
                "sanctions_administratives": "Mise en fourrière",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("30.00"),
            },
            {
                "nom": "Conduite sans permis valable",
                "article_code": "L7.5-1",
                "categorie": "DOCUMENTAIRE",
                "montant_min_ariary": Decimal("500000"),
                "montant_max_ariary": Decimal("1500000"),
                "montant_variable": False,
                "sanctions_administratives": "Emprisonnement 1-6 mois si récidive",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "1-6 mois (récidive)",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            {
                "nom": "Utilisation de faux papiers",
                "article_code": "L7.4-2",
                "categorie": "DOCUMENTAIRE",
                "montant_min_ariary": Decimal("500000"),
                "montant_max_ariary": Decimal("2000000"),
                "montant_variable": True,
                "sanctions_administratives": "Emprisonnement 6 mois - 2 ans possible",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "6 mois - 2 ans",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("50.00"),
            },
            # INFRACTIONS DE SÉCURITÉ (4 types)
            {
                "nom": "Non-port du casque (moto)",
                "article_code": "L7.6-1",
                "categorie": "SECURITE",
                "montant_min_ariary": Decimal("5000"),
                "montant_max_ariary": Decimal("6000"),
                "montant_variable": False,
                "sanctions_administratives": "Avertissement/immobilisation",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("20.00"),
            },
            {
                "nom": "Non-port ceinture de sécurité",
                "article_code": "L7.6-2",
                "categorie": "SECURITE",
                "montant_min_ariary": Decimal("10000"),
                "montant_max_ariary": Decimal("50000"),
                "montant_variable": True,
                "sanctions_administratives": "Avertissement",
                "fourriere_obligatoire": False,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("20.00"),
            },
            {
                "nom": "Modifications illégales du véhicule",
                "article_code": "L7.4-2",
                "categorie": "SECURITE",
                "montant_min_ariary": Decimal("50000"),
                "montant_max_ariary": Decimal("100000"),
                "montant_variable": False,
                "sanctions_administratives": "Immobilisation du véhicule",
                "fourriere_obligatoire": True,
                "emprisonnement_possible": "",
                "penalite_accident_ariary": None,
                "penalite_recidive_pct": Decimal("30.00"),
            },
        ]

        created_count = 0
        updated_count = 0

        for data in infractions_data:
            # Chercher si l'infraction existe déjà par article_code et nom
            infraction, created = TypeInfraction.objects.update_or_create(
                article_code=data["article_code"], nom=data["nom"], defaults=data
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        return {"success": True, "created": created_count, "updated": updated_count, "total": len(infractions_data)}

    @staticmethod
    def get_infractions_par_categorie():
        """Retourne les infractions groupées par catégorie"""
        infractions = TypeInfraction.objects.filter(est_actif=True).order_by("categorie", "nom")

        grouped = {
            "DELIT_GRAVE": [],
            "CIRCULATION": [],
            "DOCUMENTAIRE": [],
            "SECURITE": [],
        }

        for infraction in infractions:
            if infraction.categorie in grouped:
                grouped[infraction.categorie].append(infraction)

        return grouped

    @staticmethod
    def get_montant_pour_autorite(type_infraction, autorite):
        """
        Retourne le montant applicable selon l'autorité.
        Pour les montants variables, retourne le montant moyen par défaut.
        """
        if not isinstance(type_infraction, TypeInfraction):
            type_infraction = TypeInfraction.objects.get(pk=type_infraction)

        return type_infraction.get_montant_pour_autorite(autorite)
