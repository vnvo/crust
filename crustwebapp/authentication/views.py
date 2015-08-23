from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views
from django.contrib.auth import authenticate, login, logout
from django.db.models import Q
from authentication.models import Supervisor
from authentication.permissions import IsAdmin
from authentication.serializers import SupervisorSerializer
import json


class LogoutView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        logout(request)

        return Response({}, status=status.HTTP_204_NO_CONTENT)

class LoginView(views.APIView):
    def post(self, request, format=None):
        data = json.loads(request.body)

        username = data.get('username', None)
        password = data.get('password', None)

        account = authenticate(username=username, password=password)

        if account is not None:
            if account.is_active:
                login(request, account)

                serialized = SupervisorSerializer(account)

                return Response(serialized.data)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Username/password combination invalid.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class SupervisorViewSet(viewsets.ModelViewSet):

    #queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer

    def get_queryset(self):
        queryset = Supervisor.objects

        if self.request.user.is_admin:
            queryset = queryset.all()
        else:
            queryset = queryset.filter(username=self.request.user.username)

        hint = self.request.query_params.get('hint', None)
        search_filter = self.request.query_params.get('search_filter', None)
        if hint:
            queryset = queryset.filter(username__icontains=hint)
        if search_filter:
            queryset = queryset.filter(
                Q(username__icontains=search_filter)|
                Q(email__icontains=search_filter)
            )

        for key,val in self.request.query_params.iteritems():
            if key in ['page', 'page_size', 'ordering', 'hint', 'search_filter']:
                continue
            queryset = queryset.filter(**{key:val})

        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)

        return queryset

    def get_permissions(self):
        return (permissions.IsAuthenticated(), IsAdmin(),)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid(raise_exception=True):
            Supervisor.objects.create_user(**serializer.validated_data)

            return Response(
                serializer.validated_data,
                status=status.HTTP_201_CREATED
            )

        return Response({
            'status': 'Bad request',
            'message': 'Supervisor could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)
