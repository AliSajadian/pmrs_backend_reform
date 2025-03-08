from rest_framework import routers
from django.urls import path, include

from .api import *
       
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
    path('api/contractInfo/<int:contractId>/<int:dateId>/', get_ContractBaseInfo, name='contractInfo'),
    path('api/contract/updateStartOperationDate/<int:contractId>/<str:date>/', put_startOperationDate, name='startOperationDate'),
    path('api/contract/updateNotificationDate/<int:contractId>/<str:date>/', put_notificationDate, name='put_notificationDate'),
    path('api/contract/updatePlanStartDate/<int:contractId>/<str:date>/', put_planStartDate, name='planStartDate'),
    path('api/contract/updateFinishDate/<int:contractId>/<str:date>/', put_finishDate, name='finishDate'),
    path('api/contractUpdate/<int:id>/', ContractInfo.put_ContractBaseInfo, name='contractUpdate'),
    path('api/contractConsultants/<int:id>/', ContractInfo.get_ContractConsultant, name='contractConsultants'),
    path('api/contractCorporations/<int:id>/', ContractInfo.get_EpcCorporation, name='contractCorporations'),
    path('api/contractAddendums/contractAddendumList/<int:contract_id>/', ContractAddendumAPI.as_view({"get": "contractAddendumList"})),    
]

urlpatterns += router.urls

