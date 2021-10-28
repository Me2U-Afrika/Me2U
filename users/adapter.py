# I managed to get this working by changing the code for adapter a little bit.
#
# adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from users.models import User
from allauth.account.models import EmailAddress


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        print("we came to pre_social login on users/adapter.py ")
        user = sociallogin.user
        # print('user:', user)
        provider = sociallogin.account.provider
        # print('provider:', provider)
        if not user.first_name or user.profile.image_url:
            if provider.lower() == 'google':
                # print('account:', sociallogin.account.extra_data)
                if not user.first_name:
                    user.first_name = sociallogin.account.extra_data['given_name']
                    user.last_name = sociallogin.account.extra_data['family_name']
                if not user.profile.image_url:
                    user.profile.image_url = sociallogin.account.extra_data['picture']
                    user.profile.save()
                    user.save()
                try:
                    unverified_email = EmailAddress.objects.get(email__iexact=user.email, verified=False)
                    verified_email = sociallogin.account.extra_data['verified_email']
                    if verified_email:
                        unverified_email.verified = verified_email
                        unverified_email.save()
                except EmailAddress.DoesNotExist:
                    pass

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
