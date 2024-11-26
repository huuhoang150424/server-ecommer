from rest_framework_simplejwt.tokens import RefreshToken

def generaToken(user):
    refresh = RefreshToken.for_user(user)
    refresh['isAdmin'] = user.isAdmin 
    refresh['user_id'] = str(user.id)
    return {
        'refreshToken': str(refresh),
        'accessToken': str(refresh.access_token)
    }