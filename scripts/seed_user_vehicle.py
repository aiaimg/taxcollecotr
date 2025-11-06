import os
import sys
from pathlib import Path

# Ensure project root on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taxcollector_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from core.models import UserProfile
from vehicles.models import Vehicule, VehicleType
from vehicles.utils import get_puissance_fiscale_from_cylindree

USERNAME = 'testuser1'
PASSWORD = 'TestPass123!'
EMAIL = 'testuser1@example.com'
PLAQUE = '1234 TAA'

# Create or get user
user, created = User.objects.get_or_create(username=USERNAME, defaults={'email': EMAIL})
if created:
    user.set_password(PASSWORD)
    user.first_name = 'Test'
    user.last_name = 'User'
    user.is_active = True
    user.save()
print('USER_CREATED', created)

# Ensure profile
profile, p_created = UserProfile.objects.get_or_create(user=user, defaults={
    'user_type': 'individual',
    'langue_preferee': 'fr',
})
if not p_created:
    profile.user_type = 'individual'
    profile.langue_preferee = 'fr'
    profile.save()
print('PROFILE_CREATED', p_created)

# Pick a vehicle type
vtype = VehicleType.objects.filter(est_actif=True).order_by('ordre_affichage', 'nom').first()
if vtype is None:
    vtype = VehicleType.objects.create(nom='Voiture', description='Type par défaut (créé pour test)', est_actif=True, ordre_affichage=1)
print('VTYPE', vtype.nom)

# Compute coherent puissance fiscale from cylindrée
cyl = 1600
pf = get_puissance_fiscale_from_cylindree(cyl)

# Create or update vehicle
veh_defaults = {
    'proprietaire': user,
    'puissance_fiscale_cv': pf,
    'cylindree_cm3': cyl,
    'source_energie': 'Essence',
    'date_premiere_circulation': timezone.now().date().replace(year=2018),
    'categorie_vehicule': 'Personnel',
    'type_vehicule': vtype,
    'est_actif': True,
}
veh, v_created = Vehicule.objects.get_or_create(plaque_immatriculation=PLAQUE, defaults=veh_defaults)
if not v_created:
    for k, v in veh_defaults.items():
        setattr(veh, k, v)
    veh.save()
print('VEHICLE_CREATED', v_created)

print('USER_READY', user.username)
print('VEHICLE_READY', veh.plaque_immatriculation, veh.type_vehicule.nom)