from .models import Profile
from .forms import AddressForm, PersonalInfoForm, ProfilePicForm


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


def set_personal(request):
    profile = retrieve_profile(request)
    profile_form = PersonalInfoForm(request.POST, instance=profile)
    profile_form.save()


def set_pic(request):
    profile = retrieve_profile(request)
    profile_form = ProfilePicForm(request.POST, request.FILES, instance=profile)
    profile_form.save()
