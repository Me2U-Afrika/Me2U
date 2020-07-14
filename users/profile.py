from .models import Profile
from .forms import AddressForm


def retrieve_profile(request):
    try:
        profile = request.user.profile
        print('profile:', profile)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        profile.save()

    return profile


def set_profile(request):
    profile = retrieve_profile(request)
    profile_form = AddressForm(request.POST, instance=profile)
    profile_form.save()
