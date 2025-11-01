from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .utils import get_conversion_info


@method_decorator(csrf_exempt, name='dispatch')
class ConvertCylindreeView(View):
    """
    API endpoint pour convertir la cylindrée en puissance fiscale
    """
    
    def get(self, request):
        """
        Convertit une cylindrée en puissance fiscale
        
        Paramètres:
        - cylindree: cylindrée en cm³ (obligatoire)
        
        Retourne:
        - JSON avec les informations de conversion
        """
        try:
            cylindree_str = request.GET.get('cylindree')
            if not cylindree_str:
                return JsonResponse({
                    'success': False,
                    'error': 'Paramètre cylindree manquant'
                }, status=400)
            
            try:
                cylindree = int(cylindree_str)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'La cylindrée doit être un nombre entier'
                }, status=400)
            
            # Obtenir les informations de conversion
            conversion_info = get_conversion_info(cylindree)
            
            if conversion_info['valid']:
                return JsonResponse({
                    'success': True,
                    'data': conversion_info
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': conversion_info['message']
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }, status=500)
    
    def post(self, request):
        """
        Version POST pour la conversion (même logique que GET)
        """
        try:
            data = json.loads(request.body)
            cylindree = data.get('cylindree')
            
            if cylindree is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Paramètre cylindree manquant'
                }, status=400)
            
            try:
                cylindree = int(cylindree)
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'error': 'La cylindrée doit être un nombre entier'
                }, status=400)
            
            # Obtenir les informations de conversion
            conversion_info = get_conversion_info(cylindree)
            
            if conversion_info['valid']:
                return JsonResponse({
                    'success': True,
                    'data': conversion_info
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': conversion_info['message']
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON invalide'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Erreur interne: {str(e)}'
            }, status=500)


@require_http_methods(["GET"])
def convert_cylindree_simple(request):
    """
    Version simplifiée de l'API de conversion (fonction view)
    """
    cylindree_str = request.GET.get('cylindree')
    
    if not cylindree_str:
        return JsonResponse({
            'success': False,
            'error': 'Paramètre cylindree manquant'
        }, status=400)
    
    try:
        cylindree = int(cylindree_str)
        conversion_info = get_conversion_info(cylindree)
        
        if conversion_info['valid']:
            return JsonResponse({
                'success': True,
                'data': conversion_info
            })
        else:
            return JsonResponse({
                'success': False,
                'error': conversion_info['message']
            }, status=400)
            
    except ValueError:
        return JsonResponse({
            'success': False,
            'error': 'La cylindrée doit être un nombre entier'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erreur interne: {str(e)}'
        }, status=500)