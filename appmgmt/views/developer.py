# -*- coding: utf-8 -*-
"""
appmgmt.BlueButtonDev
FILE: developer
Created: 11/30/15 12:52 PM


"""
__author__ = 'Mark Scrimshire:@ekivemark'

from ..models import (Developer,
                      Organization,
                      DEVELOPER_ROLE_CHOICES)
from ..utils import Choice_Display

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import (ListView,
                                  DetailView,
                                  CreateView)

from accounts.models import User
from appmgmt.forms.developer import DeveloperForm

class DeveloperList(ListView):
    model = Developer


class DeveloperCreate(CreateView):

    model = Developer

    fields = ['member', 'organization', 'role']


class UserDomainList(ListView):
    model = settings.AUTH_USER_MODEL
    template_name = 'appmgmt/domainuser_list.html'

    fields = ['username', 'email', 'first_name', 'last_name', 'get_email_domain']

    def get_queryset(self):

        User = get_user_model()
        access_field = settings.USERNAME_FIELD
        if settings.DEBUG:

            print("User", User, access_field)

        u = User.objects.get(**{access_field:self.request.user})

        qs = User.objects.filter(email__icontains=u.get_email_domain)
        # qs = super(UserDomainList, self).get_queryset()

        if settings.DEBUG:
            result = qs.filter(email__icontains=u.get_email_domain()).values()
            print("qs filter:", result)

        return qs.filter(email__icontains=u.get_email_domain()).values()
    # def get_context_data(self, **kwargs):
    #     context = super(MyOrganizationListView, self).get_context_data(**kwargs)


    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super(UserDomainList, self).get_context_data(**kwargs)
        # add in a QuerySet of all Applications

        # print("context - Developers:", context, self.request.user )
        org = Organization.objects.get(owner_id=self.request.user)
        # print("Org:", org )
        context['extra_content'] = {"developer_list":Developer.objects.filter(organization=org.id)
                                   }
        if settings.DEBUG:
            print("Context:", context['extra_content'])
            print("Developers:", context['extra_content']['developer_list'])

        return context


def DevTeam_Add(request, pk):
    """
    Add a Candidate to the Developer Database as a Team Member
    :param request:
    :param pk:
    :return:
    """

    User = get_user_model()
    access_key = settings.USERNAME_FIELD
    try:
        candidate = User.objects.get(pk=pk)
    except User.DoesNotExist:
        messages.error(request,"Candidate Not Found [%s]" % pk)
        return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

    # We have a Candidate
    # So we 1. create a Developer record
    # 2. Update User record with Organization

    if settings.DEBUG:
        print("Request User Org:", request.user.organization)

    # default role to '9' = default in model
    # member = candidate.username
    dev = Developer(member=candidate, organization=request.user.organization)
    dev.save()
    candidate.organization = request.user.organization
    candidate.save()

    return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))


def DevTeam_Delete(request, pk):
    """
    Remove a Developer from the Developer Database
    Also set user.organization to None
    :param request:
    :param pk:
    :return:
    """

    User = get_user_model()
    access_key = settings.USERNAME_FIELD
    try:
        developer = Developer.objects.get(pk=pk)
    except Developer.DoesNotExist:
        messages.error(request,"Developer Not Found [%s]" % pk)
        return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

    # We have a Developer
    # So we 1. Delete Developer record
    # 2. Update User record to set Organization to None

    # We need to do some tests.

    # Get a count of Developers.
    try:
        dev_team = Developer.objects.filter(organization=request.user.organization)
    except Developer.DoesNotExist:
        messages.error(request,"Dev Team Records Not Found [%s]" % pk)
        return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

    # We can get the team size.
    team_size = dev_team.count()

    # If team size = 1 we need to delete application keys and Organization
    # So throw an error and force a "Close Account" Action
    if team_size <= 1:
        messages.error(request, "This is the last team member. "
                                "Add a new member to the team first, or "
                                "choose 'Close Account' option to remove "
                                "application keys and organization record.")
        return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

    # There is more than one member of the team.
    # Check the validity of the removal before taking action

    # Set Proposed Role to '-' to test status change
    if valid_role_change(request,
                         developer.role,
                         '-'):
        u = User.objects.get(**{access_key:developer.member})
        if settings.DEBUG:
            print("User:", u)
        u.organization = None
        u.save()
        developer.delete()
        messages.info(request,"%s removed from Developer Team" % u.username)

    return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))



def DevTeam_Role_Change(request, pk):
    """
    Receive the id key for Developer table.
    Get count of Developers for the Organization

    Present form to change role

    Evaluate role change

    Update Developer Record

    :param request:
    :param pk:
    :return:
    """

    # Get the record
    try:
        target = Developer.objects.get(pk=pk)
    except Developer.DoesNotExist:
        messages.error(request,"Developer Record Not Found [%s]" % pk)
        return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

    current_role = target.role

    try:
        dev_team = Developer.objects.filter(organization=target.organization)
    except Developer.DoesNotExist:
        messages.error(request,"Dev Team Records Not Found [%s]" % pk)
        return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

    team_size = dev_team.count()

    if request.method == "POST":
        form = DeveloperForm(request.POST)
        if form.is_valid():
            # Now we do the role comparison tests
            if valid_role_change(request,
                                 current_role,
                                 form.cleaned_data['role']):

                # If developer dropped from team. Remove him
                if form.cleaned_data['role'] == '-':
                    # remove organization from User record
                    # delete Developer record
                    User = get_user_model()
                    access_key = settings.USERNAME_FIELD
                    try:
                        u = User.objects.get(**{access_key:target.member})
                        u.organization = None
                        u.save()
                        target.delete()
                        target.role = form.cleaned_data['role']
                        target.save()
                        return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

                    except User.DoesNotExist:
                        target.role = form.cleaned_data['role']
                        target.save()

                # Check for Account Owner Change
                elif form.cleaned_data['role'] == '1':
                    # New Account Owner
                    target.role  = form.cleaned_data['role']
                    target.save()
                    try:
                        org = Organization.objects.get(name=request.user.organization)
                        org.owner = target.member
                        org.save()
                    except Organization.DoesNotExist:
                        org = {}
                else:
                    # All other options
                    target.role = form.cleaned_data['role']
                    target.save()

            return HttpResponseRedirect(reverse_lazy('accounts:manage_account'))

    else:

        form = DeveloperForm(initial={'role': current_role})

    return render(request,
                  'appmgmt/developer_role_form.html',
                  {'form': form,
                   'developer': target.member})

def valid_role_change(request, current, proposed):
    """
    Check for a valid change in role

    :param request:
    :param current:
    :param proposed:
    :return:  True or False
    """

    me = Developer.objects.get(member=request.user)
    if settings.DEBUG:
        print("Me;", me)

    result =  False
    msg = ""

    if settings.DEBUG:
        print("Checking validity of Role Change")
        print("Current:", current, "Proposed:", proposed)

    if (current == '2' and proposed in ['9', '-']):
        # Backup can be demoted
        result = True
    elif (proposed == '1' and current == '2' and me.role == '1'):
        # special handling to swap account ownership
        result = True
    elif (proposed == '1' and me.role == '2'):
        # Special check for promotion to Account Owner ['1']
        # Check if Account Owner in Dev_Team
        try:
            dev_owner = Developer.objects.filter(organization=request.user.organization,
                                                 role='1')
        except Developer.DoesNotExist:
            dev_owner = {}
        if len(dev_owner) == 0:
            # No Account Owner for Organization.
            msg = "No Account Owner. Promotion to Account Owner is allowed. "
            result = True


    elif (proposed == '2' and me.role == '1' ):
        # Only Account Owner can create a backup
        if current == '1':
            # WE need to check the demotion of Account Owner carefully
            try:
                dev_team_size = Developer.objects.filter(organization=request.user.organization).count()
            except Developer.DoesNotExist:
                dev_team_size = 0
            if dev_team_size <= 1:
                # If there is only one team member we shouldn't allow a
                result = False
            else:
                result = True
        else:
            # Team member is being promoted by Account Owner to Backup
            result = True

    elif (proposed == '2' and me.role != '1'):
        # Only the Account Owner can create a backup
        msg = "This action can only be performed by the Account Owner. "
        result = False
    elif (proposed in ['9','-'] and current == '1'):
        # Demote Account Owner to backup first
        result = False
    elif (current in ['9', '-'] and proposed in ['-'] and me.role in ['1','2']):
        # Removing Team member by Owner or Backup
        result = True


    if not result:
        msg = msg + "Role not "
    else:
        msg = msg + "Role "

    msg = msg + "changed from %s to %s" % (Choice_Display(current),
                                           Choice_Display(proposed))

    messages.info(request, msg)
    return result
#   Change Role
##  Check if last Developer entry for Organization if Role becomes None
### Check if active applications exist
### Promote to Account Owner[1]
#### Must be Primary or Backup Owner to Promote
#### Demotes Account Owner[1] to Backup[2]

### Promote to Backup Owner[2]
#### Must be Account Owner[1] to promote

### Demote to Team Member[9]
#### Primary or Backup can demote.
#### Only demote from Backup[2] to Team Member

##  Remove from Team [-]
### Remove - Via Remove function

# remove entry from Developer
## Remove organization from User.entry


