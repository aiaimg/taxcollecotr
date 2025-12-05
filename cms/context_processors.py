from .views import get_cms_context


def cms_context(request):
    """
    Context processor to make CMS settings available to all templates.
    """
    return get_cms_context()
