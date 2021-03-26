# I managed to get this working by changing the code for adapter a little bit.
#
# adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from users.models import User


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):

        print("we came to pre_social login")
        user = sociallogin.user
        print('user:', user)
        if user.id:
            return
        if not user.email:
            return

        try:
            user = User.objects.get(
                email=user.email)  # if user exists, connect the account to the existing account and login
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass