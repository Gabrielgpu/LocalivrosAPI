from .models import BlingCredential

def bling_credentials(request):
    credential = None
    if request.user.is_authenticated:
        credential = BlingCredential.objects.filter(user=request.user).first()
    return {
        'bling_credential': credential,
        'has_credential': credential is not None
    }
