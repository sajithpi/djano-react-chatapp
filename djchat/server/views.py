from django.db.models import Count
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.response import Response

from .models import Server
from .serializer import ServerSerializer

# Create your views here.


class ServerListViewSet(viewsets.ViewSet):
    queryset = Server.objects.all()

    def list(self, request):
        # Retrieve query parameters from the request
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == True
        by_server_id = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == True

        # Check if authentication is required for certain queries
        if by_user or by_server_id and not request.user.is_authenticated:
            raise AuthenticationFailed()

        # Filter queryset based on the 'category' parameter
        if category:
            self.queryset = self.queryset.filter(category__name=category)

        # Filter queryset based on the authenticated user
        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(member=user_id)

        # Annotate the queryset with the number of members if requested
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        # Limit the queryset to a specified quantity if 'qty' parameter is provided
        if qty:
            self.queryset = self.queryset[: int(qty)]

        # Filter queryset based on the 'by_server_id' parameter if provided
        if by_server_id:
            try:
                self.queryset = self.queryset.filter(id=by_server_id)
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_server_id} not found")
            except ValueError:
                raise ValidationError(detail=f"Server value error")

        # Serialize the queryset using ServerSerializer, considering 'num_members' if requested
        serializer = ServerSerializer(self.queryset, many=True, context={"num_members": with_num_members})

        # Return the serialized data in the response
        return Response(serializer.data)
