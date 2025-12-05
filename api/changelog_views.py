from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from api.models import APIVersion


class APIChangelogView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        versions = APIVersion.objects.all().values(
            "version", "released_at", "summary", "changes", "deprecated_endpoints"
        )
        return Response({"versions": list(versions)})

