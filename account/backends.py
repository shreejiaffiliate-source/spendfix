from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 🔥 YAHAN MAGIC HAI: Ab Django Username, Email, YA Phone teeno check karega!
            user = UserModel.objects.get(
                Q(username__iexact=username) | 
                Q(email__iexact=username) | 
                Q(phone__iexact=username)
            )
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None