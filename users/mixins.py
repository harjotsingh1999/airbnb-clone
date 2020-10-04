# Mixins will help us show a message to the users if he
# tries to mess with the urls and tries to update password
# when he is logged in with gmail or github
# in which case he should not be allowed to change password
# Or if he tries to update profile without being logged __init__(self, *args, **kwargs):
# which of course throws an error, but its better to just show a message


from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.contrib import messages

# only users who are logged out will be able to see the view whch extends this view
# used in SignUp and Login View
# meaning users who are logged in will get the error message described below
# if they try to change url to get into login/signup page
class LoggedOutOnlyView(UserPassesTestMixin):

    # if this function returns true only then user will see this view
    # in this case only unauthenticated users will see this view
    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        messages.info(self.request, "Can't go there")
        return redirect("core:home")

    # message to show to these users
    permission_denied_message = "Page not found"


# this class LoginRequiredMixin already has method to check if user is authtnticated
# we just have to add
class LoggedInOnlyView(LoginRequiredMixin):
    login_url = reverse_lazy("users:login")

    def handle_no_permission(self):
        messages.info(self.request, "You must be logged in")
        return redirect("users:login")


# only users who have logged in with email can change their passwords
# others will be shown an error
class EmailLoginOnlyView(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.login_method == "email"

    def handle_no_permission(self):
        messages.info(self.request, "Password cannot be changed")
        return redirect(self.request.user.get_absolute_url)