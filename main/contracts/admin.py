"""
Admin for the contracts application.

This module contains the admin for the contracts application.
"""
from django.contrib import admin
from .models import *
from django import forms
from django.contrib.auth import get_user_model


PmrsUser = get_user_model()


class CompanyInline(admin.StackedInline):
    """
    Inline for the Company model.
    """
    model = Company
    exclude = ["fax", "address"]


class CompanyTypeAdmin(admin.ModelAdmin):
    """
    Admin for the CompanyType model.
    """
    inlines = [
        CompanyInline,
    ]
    ordering = ['companytype']
    search_fields = ['companytype']

    def get_actions(self, request):
        """
        Get the actions for the CompanyType admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """
    Admin for the Company model.
    """
    list_display = ('company', 'get_company_type')
    ordering = ['-companytypeid']
    search_fields = ['company']

    def get_actions(self, request):
        """
        Get the actions for the Country admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)

    @admin.display(ordering='Company__CompanyType', description='company type')
    def get_company_type(self, obj):
        """
        Get the type of the Company.
        """
        return obj.companytypeid.companytype


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """
    Admin for the Country model.
    """
    list_display = ['country']

    def get_actions(self, request):
        """
        Get the actions for the Country admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """
    Admin for the Currency model.
    """
    list_display = ('get_country', 'currency')

    def get_actions(self, request):
        """
        Get the actions for the Currency admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)

    @admin.display(ordering='Currency__Country', description='country')
    def get_country(self, obj):
        """
        Get the country for the Currency.
        """
        return obj.countryid.country


# @admin.register(Currency)
# class CurrencyAdmin(admin.ModelAdmin):
#     list_display = ('country', 'currency')

#     def get_actions(self, request):
#         actions = super().get_actions(request)
#         if 'delete_selected' in actions:
#             del actions['delete_selected']
#         return actions

#     # def has_add_permission(self, request):
#     #     return ("add" in request.path or "change" in request.path)

#     @admin.display(ordering='Currency__Country', description='country')
#     def get_country(self, obj):
#         return obj.countryid.country

# class PersonelInline(admin.TabularInline):
#     model = Personel
#     exclude = ["tel", "activity"]

# class PersoneltypeAdmin(admin.ModelAdmin):
#     inlines = [
#         PersonelInline,
#     ]

# admin.site.register(Personeltype, PersoneltypeAdmin)

# @admin.register(Personeltype)
# class PersoneltypeAdmin(admin.ModelAdmin):
#     list_display = ('personeltypeid', 'personeltype')

# @admin.register(Personel)
# class PersonelAdmin(admin.ModelAdmin):
#     list_display = ('name', 'family', 'get_personelType')
#     list_filter = ['personeltypeid']
#     search_fields = ['family']

#     def get_actions(self, request):
#         actions = super().get_actions(request)
#         if 'delete_selected' in actions:
#             del actions['delete_selected']
#         return actions

    # @admin.display(ordering='Personel__Personeltype', description='personal type')
    # def get_personelType(self, obj):
    #     return obj.personeltypeid.personeltype

@admin.register(ContractType)
class ContractTypeAdmin(admin.ModelAdmin):
    """
    Admin for the ContractType model.
    """
    list_display = ['contracttype']
    search_fields = ['contracttype']
    ordering = ['contracttype']

    def get_actions(self, request):
        """
        Get the actions for the ContractType admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)


class ContractForm(forms.ModelForm):
    """
    Form for the Contract model.
    """
    class Meta:
        model = Contract
        fields = ('contractno', 'contract', 'contracttypeid', 'customerid', 'coordinatorid',
              'startoperationdate', 'finishdate',  'notificationdate', 'validationdate', 
              'planstartdate', 'startdate', 'duration', 'contractamount_r', 'contractamount_fc', 
              'currencyid', 'prepaymentpercent',  'insurancepercent', 'perforcebondpercent',  
              'withholdingtaxpercent', 'commitpercent', 'latitude', 'longitude', 'iscompleted'
        )
        widgets = {'contractno': forms.TextInput(attrs={'dir': 'rtl', 'class': 'vTextField'})}


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """
    Admin for the Contract model.
    """
    form = ContractForm
    list_display = ('contractno', 'contract', 'get_contract_type', 'duration')
    fields = ('contractno', 'contract', 'contracttypeid', 'projectmanagerid', 'customerid',
              'coordinatorid', 'startoperationdate', 'finishdate', 'notificationdate',  
              'validationdate', 'planstartdate', 'startdate', 'duration', 'contractamount_r', 
              'contractamount_fc', 'currencyid', 'prepaymentpercent', 'insurancepercent',  
              'perforcebondpercent', 'withholdingtaxpercent', 'commitpercent', 'latitude', 
              'longitude', 'iscompleted'
    )
    list_filter = ['contracttypeid']
    search_fields = ['contractno']
    ordering = ['contractno']

    def get_actions(self, request):
        """
        Get the actions for the Contract admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)

    @admin.display(ordering='Contract__ContractType', description='contract type')
    def get_contract_type(self, obj):
        """
        Get the contract type for the Contract.
        """
        return obj.contracttypeid.contracttype

    # , 'get_projectManager'
    # @admin.display(ordering='Contract__User', description='project manager')
    # def get_projectManager(self, obj):
    #     return '%s %s' % (obj.projectmanagerid.first_name, obj.projectmanagerid.last_name)
    # if obj.projectmanagerid is not None else ''


# @admin.register(ContractUser)
# class ContractUserAdmin(admin.ModelAdmin):
#     list_display = ('contractuserid', 'get_user', 'get_contract')
#     list_filter = ['userid']
#     search_fields = ['contractid__contract']

#     @admin.display(ordering='ContractUser__Tblcontract', description='contract')
#     def get_contract(self, obj):
#         return obj.contractid.contract

#     @admin.display(ordering='ContractUser__PmrsUser', description='user')
#     def get_user(self, obj):
#         return obj.userid.username

@admin.register(EpcCorporation)
class EpcCorporationAdmin(admin.ModelAdmin):
    """
    Admin for the EpcCorporation model.
    """
    list_display = ('get_contract', 'get_company', 'e_percent', 'p_percent', 'c_percent')
    search_fields = ['contractid__contract']
    ordering = ['contractid__contract']

    def get_actions(self, request):
        """
        Get the actions for the EpcCorporation admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)

    @admin.display(ordering='EpcCorporation__Contract', description='contract')
    def get_contract(self, obj):
        """
        Get the contract for the EpcCorporation.
        """
        return obj.contractid.contract

    @admin.display(ordering='EpcCorporation__Company', description='company')
    def get_company(self, obj):
        """
        Get the company for the EpcCorporation.
        """
        return obj.companyid.company


@admin.register(ContractConsultant)
class ContractConsultantAdmin(admin.ModelAdmin):
    """
    Admin for the ContractConsultant model.
    """
    list_display = ('get_contract', 'get_consultant')
    # list_filter = ['contractid', 'consultantid']
    search_fields = ['consultantid__company']
    ordering = ['contractid__contract']

    def get_actions(self, request):
        """
        Get the actions for the ContractConsultant admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)

    @admin.display(ordering='ContractConsultant__Contract', description='contract')
    def get_contract(self, obj):
        """
        Get the contract for the ContractConsultant.
        """
        return obj.contractid.contract

    @admin.display(ordering='ContractConsultant__Company', description='consultant')
    def get_consultant(self, obj):
        """
        Get the consultant for the ContractConsultant.
        """
        return obj.consultantid.company


# @admin.register(ContractCurrencies)
# class ContractCurrenciesAdmin(admin.ModelAdmin):
#     list_display = ('contractcurrencyid', 'get_contract', 'get_currency', 'price', 'date')

#     @admin.display(ordering='ContractCurrencies__Contract', description='contract')
#     def get_contract(self, obj):
#         return obj.contractid.contract

#     @admin.display(ordering='ContractCurrencies__Currency', description='currency')
#     def get_currency(self, obj):
#         curr = Currency.objects.get(pk=obj.currencyid)
#         return curr.currency


@admin.register(Addendum)
class AddendumAdmin(admin.ModelAdmin):
    """
    Admin for the Addendum model.
    """
    list_display = ('get_contract', 'addendumamount_r',
            'addendumamount_fc', 'addendumamountdate', 'afteraddendumdate') 
    ordering = ['contractid__contract']

    def get_actions(self, request):
        """
        Get the actions for the Addendum admin.
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # def has_add_permission(self, request):
    #     return ("add" in request.path or "change" in request.path)

    @admin.display(ordering='Addendum__Contract', description='contract')
    def get_contract(self, obj):
        """
        Get the contract for the Addendum.
        """
        return obj.contractid.contract
