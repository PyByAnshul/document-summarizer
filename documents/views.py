from rest_framework import status, viewsets
from rest_framework.response import Response

from .models import Document
from .serializers import (
    DocumentCreateSerializer,
    DocumentDetailSerializer,
    DocumentListSerializer,
)
from .tasks import process_document


class DocumentsViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    http_method_names = ["get", "post", "delete"]

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentCreateSerializer
        if self.action == "list":
            return DocumentListSerializer
        return DocumentDetailSerializer

    def perform_create(self, serializer):
        document = serializer.save()
        process_document.delay(document.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "id": serializer.instance.id,
                "filename": serializer.instance.original_filename,
                "status": serializer.instance.status,
            },
            status=status.HTTP_202_ACCEPTED,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            {"message": "Document deleted."},
            status=status.HTTP_202_ACCEPTED,
        )
