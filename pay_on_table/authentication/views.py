from .serializers import ChangePasswordSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.validators import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_password(request):
    user: User = request.user
    data = request.data
    serializer = ChangePasswordSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    if user.check_password(serializer.validated_data["old_password"])  is True:
        user.set_password(serializer.validated_data["new_password"])
        user.save()
    else:
        raise ValidationError(detail="Old Password is not correct.")
    return Response()
