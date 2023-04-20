from functools import wraps

def confirm_password(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
            from .views import ConfirmPasswordView
            return ConfirmPasswordView.as_view()(request, *args, **kwargs)
            return view_func(request, *args, **kwargs)
    return _wrapped_view

