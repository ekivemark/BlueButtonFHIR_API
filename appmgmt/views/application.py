# -*- coding: utf-8 -*-
"""
bofhirdev
FILE: application
Created: 11/5/15 10:50 PM


"""
from PIL import Image
from braces.views import MessageMixin

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy

from django.forms.models import model_to_dict

from django.http import HttpResponseRedirect
from django.shortcuts import (render,
                              render_to_response,
                              get_object_or_404)
from django.template import RequestContext
from django.views.generic import (DetailView,
                                  UpdateView,
                                  DeleteView)
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView

from oauth2_provider.generators import (generate_client_id,
                                        generate_client_secret)

from accounts.utils import User_From_Request

from appmgmt.forms.application import (ApplicationForm,
                                       Application_Secret_Form,
                                       Application_Secret,
                                       ApplicationDeleteForm)
from appmgmt.models import (BBApplication,
                            Organization,
                            Developer)


__author__ = 'Mark Scrimshire:@ekivemark'


@login_required
def My_Application_Update(request, pk):
    """
    Edit a BBApplication entry

    :param request:
    :return:
    """

    # Accounts.utils - get user model and key field and return user or None
    u = User_From_Request(request.user)
    app = BBApplication.objects.get(pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST or None,
                               request.FILES or None,
                               instance=app)
        if form.is_valid():
            # Preserve the key and secret

            app = form.save(commit=False)
            app.owner = u
            app.user = u
            app.organization = u.organization

            if settings.DEBUG:
                print("App:", app )
                print("logo:", app.logo)
                print("form logo:", form.cleaned_data['logo'])
            app.save()

            # Check
            return HttpResponseRedirect(reverse_lazy('appmgmt:manage_applications'))
    else:

        form = ApplicationForm(instance=app,
                               initial={'name': app.name,
                                        'logo': app.logo,
                                        'about': app.about,
                                        'privacy_url': app.privacy_url,
                                        'support_url': app.support_url,
                                        'client_type': app.client_type,
                                        'authorization_grant_type': app.authorization_grant_type,
                                        }
                            )

    return render(request, 'appmgmt/bbapplication_form.html',
                              {'form': form,
                               'application': app,
                               'owner': u,
                               'organization': u.organization,})


class MyApplicationListView(ListView):
    """
    View for Applications

    """
    model = BBApplication
    template_name = 'appmgmt/application_list.html'

    def get_queryset(self):
        if settings.DEBUG:
            print("Queryset User:", self.request.user)
        qs = super(MyApplicationListView, self).get_queryset()
        return qs.filter(organization=self.request.user.organization).values()


class MyApplicationDetailView(DetailView):
    """
    Display the Application Detail View for a single item in the
    application list
    """
    model = BBApplication
    fields = ['name', 'about', 'logo',
              'privacy_url', 'support_url',
              'redirect_uris', 'client_type',
              'authorization_grant_type',
              ]
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(MyApplicationDetailView, self).get_context_data(**kwargs)
        # add in a QuerySet of all Applications
        if settings.DEBUG:
            print("Context:", context)

        return context


class MyApplicationUpdateView(UpdateView):
    """
    Edit view for Application

    """
    model = BBApplication
    fields = ['name', 'about','logo',
              'privacy_url', 'support_url',
              'redirect_uris' ,
              'client_type', 'authorization_grant_type',
              ]

    context_object_name = "application"

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(MyApplicationUpdateView, self).get_context_data(**kwargs)
        # add in a QuerySet of all Applications
        if settings.DEBUG:
            print("Context:", context)

        return context


class MyApplicationCreate(CreateView):
    """
    Create Application
    """

    model = BBApplication
    form_class = ApplicationForm
    # fields = ['name', 'about',
    #           'logo', 'privacy_url', 'support_url',
    #           'redirect_uris', 'client_type',
    #           'authorization_grant_type',
    #           ]
    context_object_name = 'application'

    def get_context_data(self, **kwargs):
        context = super(MyApplicationCreate, self).get_context_data(**kwargs)
        context['organization'] = self.request.user.organization
        context['owner'] = self.request.user

        return context

    def get_object(self):
        return get_object_or_404(BBApplication, pk=self.kwargs.get("pk"))

    def get_initial(self):
        if self.request.user.is_authenticated():
            print("user is:", self.request.user)

        org = Organization.objects.filter(name=self.request.user.organization)
        if settings.DEBUG:
            print("org:",org )
        self.initial.update({ 'owner': self.request.user,
                              'organization': org,
                              'user': self.request.user
                             })

        return self.initial

    def post(self, request, *args, **kwargs):

        form = self.get_form()

        if self.request.user.is_authenticated():
            print("user is:", self.request.user)
            print("self:", self)
            print("form:", form)

        if form.is_valid():

            if settings.DEBUG:
                print("logo:", form.instance.logo)
            form.instance.user = self.request.user
            form.instance.owner = self.request.user
            form.instance.organization = self.request.user.organization
            form.save()
            form.organization = self.request.user.organization
            return super(MyApplicationCreate, self).form_valid(form)

            return super(MyApplicationCreate, self).form_valid(form)

        return HttpResponseRedirect(self.success_url)

    # def get(self, request, *args, **kwargs):
    #
    #     if self.request.user.is_authenticated():
    #         print("user is:", self.request.user)
    #     u = self.request.user
    #     org = Organization.objects.filter(name=u.organization)
    #     if settings.DEBUG:
    #         print("u:", u)
    #         print("org:", org)
    #     # self.object = self.get_object()
    #     success_url = reverse_lazy('appmgmt:application_view')
    #     if settings.DEBUG:
    #         print("object:", self.get_object().id)
    #         print("success goes to:",success_url)
    #
    #     return HttpResponseRedirect(success_url,
    #                                 kwargs={'pk': self.get_object().id})


def Application_Update_Secret(request, pk):
    """
    Replace client_id and client_secret

    :param request:
    :param pk:
    :return:
    """
    if request.method == 'POST':
        a=BBApplication.objects.get(pk=pk)
        form = Application_Secret(request.POST)

        if form.is_valid():
            if form.cleaned_data['confirm'] == '1':
                a.client_id = generate_client_id()
                a.client_secret = generate_client_secret()
                a.save()
                messages.success(request,"Client Id and Secret updated")

            if settings.DEBUG:
                print("Confirm:", form.cleaned_data['confirm'])
                print("Id:", a.client_id)
                print("Secret:", a.client_secret)

            return HttpResponseRedirect(reverse_lazy('appmgmt:manage_applications'))

        else:
            if settings.DEBUG:
                print("form has a problem")
    else:
        a=BBApplication.objects.get(pk=pk)
        if settings.DEBUG:
            print("BBApplication:", a)

        form = Application_Secret(initial={'confirm': '0'})
    return render_to_response('appmgmt/application_secret_form.html',
                              RequestContext(request,{'form': form, 'application': a,}))


class MyApplicationDeleteView(MessageMixin, DeleteView):
    """
    Delete an Application
    """

    model = BBApplication
    context_object_name = 'application'
    #form_class = ApplicationDeleteForm
    success_message = "Application Deleted Successfully"

    def get_context_data(self, **kwargs):
        context = super(MyApplicationDeleteView, self).get_context_data(**kwargs)
        context.update({'organization': self.request.user.organization,
                        'owner': self.request.user,
                        'key': self.object.id,
                        'verb': "delete",
#                        'application': BBApplication.objects.get(pk=self.object.id)
                        })
        if settings.DEBUG:
            print("Context:", context, "kwargs", kwargs, "self", self.object.id,
                  )
        return context

    def get_queryset(self):
        qs = super(MyApplicationDeleteView, self).get_queryset()
        return qs.filter(owner=self.request.user)


@login_required()
def Manage_Applications(request):
    # Manage Organization's Applications entry page

    account_model = get_user_model()
    access_field = settings.USERNAME_FIELD
    user = account_model.objects.get(**{access_field:request.user})

    org_name = user.organization

    if settings.DEBUG:
        print(settings.APPLICATION_TITLE,
              "in accounts.views.manage_account")
        print("with Organization Record:", org_name)

    if org_name == None:
        return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

    try:
        org = Organization.objects.get(name=org_name)
    except Organization.DoesNotExist:
        org = {}
        return HttpResponseRedirect(reverse_lazy("accounts:manage_account"))

    # get my Developer role
    try:
        my_dev = Developer.objects.get(member=user)
        my_role = my_dev.role
        if my_dev.role in ['1','2']:
            org_owner = True
        else:
            org_owner = False
    except Developer.DoesNotExist:
        my_dev = {}
        my_role = ""
        org_owner = False


    # Get the Applications for an Organization
    try:
        my_apps = BBApplication.objects.filter(organization=org_name).order_by('name')
    except BBApplication.DoesNotExist:
        my_apps = {}


    if settings.DEBUG:
        print("User:", user)
        print("Organization:", org, "[", org.name, "]")
        print("My_apps :", my_apps)
        print("Media is here:[ROOT]", settings.MEDIA_ROOT,
              "[URL]", settings.MEDIA_URL)

    context = {"user": user,
               "org": org,
               "org_owner": org_owner,
               "my_apps": my_apps,
               }

    # Using manage_applications template
    return render_to_response('appmgmt/manage_applications.html',
                              RequestContext(request, context, ))

