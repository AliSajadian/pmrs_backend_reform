"""
URLs for the contracts application.
"""
from rest_framework import routers
from django.urls import path

from .api import ContractTypeAPI, CurrencyAPI, CountryAPI, ContractAddendumAPI, PersonelTypeAPI, \
    PersonelAPI, ContractAPIEx, ContractInfoAPI, get_contract_base_info, put_start_operation_date, \
        put_notification_date, put_plan_start_date, put_finish_date

router = routers.DefaultRouter()
router.register('api/contractTypes', ContractTypeAPI, 'contractTypes')
router.register('api/currencies', CurrencyAPI, 'currencies')
router.register('api/countries', CountryAPI, 'countries')
router.register('api/contractAddendums', ContractAddendumAPI, 'contractAddendums')
router.register('api/personalTypes', PersonelTypeAPI, 'personalTypes')
router.register('api/personals', PersonelAPI, 'personals')

urlpatterns = [
    # path('api/auth/login', LoginAPI.as_view()),  put_ContractBaseInfo  put_startOperationDate
    path('api/contracts/<int:userid>/', ContractAPIEx.as_view(), name='contracts'),
    path('api/contractInfo/<int:contractId>/<int:date_id>/',
        get_contract_base_info, name='contractInfo'),
    path('api/contract/updateStartOperationDate/<int:contract_id>/<str:date>/',
        put_start_operation_date, name='startOperationDate'),
    path('api/contract/updateNotificationDate/<int:contract_id>/<str:date>/',
        put_notification_date, name='put_notificationDate'),
    path('api/contract/updatePlanStartDate/<int:contract_id>/<str:date>/',
        put_plan_start_date, name='planStartDate'),
    path('api/contract/updateFinishDate/<int:contract_id>/<str:date>/',
        put_finish_date, name='finishDate'),
    path('contract-info/', ContractInfoAPI.as_view(), name='contract-info'),
    # path('api/contractUpdate/<int:pk>/',
    #     ContractInfo.put_contract_base_info, name='contractUpdate'),
    # path('api/contractConsultants/<int:pk>/',
    #     ContractInfo.get_contract_consultant, name='contractConsultants'),
    # path('api/contractCorporations/<int:pk>/',
    #     ContractInfo.get_epc_corporation, name='contractCorporations'),
    path('api/contractAddendums/contractAddendumList/<int:contract_id>/',
        ContractAddendumAPI.contract_addendum_list, name='contractAddendumList'),
]

urlpatterns += router.urls
