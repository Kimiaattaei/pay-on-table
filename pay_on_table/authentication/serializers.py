from rest_framework import serializers


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=30, min_length=4)
    new_password = serializers.CharField(min_length=4, max_length=30)
