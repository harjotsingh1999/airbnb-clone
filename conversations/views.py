from django.core.checks import messages
from django.http import request
from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import Http404
from django.db.models import Q
from django.views.generic import View
from users import models as user_models
from . import models
from . import forms

# Create your views here.
def go_conversation(request, a_pk, b_pk):
    user1 = user_models.User.objects.get(pk=a_pk)
    user2 = user_models.User.objects.get(pk=b_pk)
    if user1 is not None and user2 is not None:
        # try to get a converation

        # for complex queres we use Q objects when filter is not enough
        # here we are getting a convo with both user 1 and user2
        try:
            conversation = models.Conversation.objects.get(
                Q(participants=user1) & Q(participants=user2)
            )
            print("convo exists", conversation)
        except models.Conversation.DoesNotExist:
            # if convo does not exist we have to create one
            print("convo does not exist")
            conversation = models.Conversation.objects.create()
            conversation.participants.add(user1, user2)
        return redirect(
            reverse(
                "conversations:detail",
                kwargs={"pk": conversation.pk},
            )
        )


class ConversationDetailView(View):
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()

        form = forms.AddMessageForm()
        return render(
            self.request,
            "conversations/conversation_detail.html",
            {
                "conversation": conversation,
                "form": form,
            },
        )

    def post(self, *args, **kwargs):
        form = forms.AddMessageForm(self.request.POST)
        pk = kwargs.get("pk")
        conversation = models.Conversation.objects.get_or_none(pk=pk)
        if not conversation:
            raise Http404()
        if form.is_valid():
            message = form.cleaned_data["message"]
            if message is not None:
                models.Message.objects.create(
                    message=message,
                    user=self.request.user,
                    conversation=conversation,
                )
        return redirect(reverse("conversations:detail", kwargs={"pk": pk}))
