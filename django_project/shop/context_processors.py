def user_roles(request):
    user = request.user
    return {
        'is_admin': user.groups.filter(name='Administrator').exists(),
        'is_seller': user.groups.filter(name='Seller').exists(),
    }