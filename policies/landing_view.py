from django.views.generic import TemplateView
from django.shortcuts import redirect

class LandingView(TemplateView):
    """Landing page view for non-authenticated users."""
    template_name = 'landing.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users to the policies home page
        if request.user.is_authenticated:
            return redirect('policies:home')
        return super().dispatch(request, *args, **kwargs)