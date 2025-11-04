"""
URLs for the projects application.
"""
from rest_framework import routers
from django.urls import path

from .api import *
       
router = routers.DefaultRouter()
router.register('api/reportConfirm', ReportConfirmAPI, basename='reportConfirm')
router.register('api/financialInfos', FinancialInfoAPI, basename='financialInfo')
router.register('api/hses', HseAPI, basename='hse')
router.register('api/progressStates', ProgressStateAPI, basename='progressState')
router.register('api/timeProgressStates', TimeProgressStateAPI, basename='timeProgressStates')
router.register('api/invoices', InvoiceAPI, basename='invoice')
router.register('api/financialInvoices', FinancialInvoiceAPI, basename='financialInvoice')
router.register('api/workVolumes', WorkVolumeAPI, basename='workVolume')
router.register('api/pmsProgresses', PmsprogressAPI, basename='pmsProgress')
router.register('api/budgetCosts', BudgetCostAPI, basename='budgetCost')
router.register('api/machineries', MachineryAPI, basename='machinery')
router.register('api/projectPersonals', ProjectPersonalAPI, basename='projectPersonal')
router.register('api/problems', ProblemAPI, basename='problem')
router.register('api/criticalActions', CriticalActionAPI, basename='criticalAction')

urlpatterns = [
    path('api/reportDates', ReportDateAPIEx.as_view()),
    # <int:contract_id>/<int:date_id>/<int:confirmed>/
    path('api/reportConfirm/projectManagerReportConfirm/', ReportConfirmAPI.as_view({"post": "projectManagerReportConfirm"})),    
    path('api/reportConfirm/coordinatorReportConfirm/', ReportConfirmAPI.as_view({"post": "coordinatorReportConfirm"})),    
    path('api/reportConfirm/isCoordinatorConfirmedReport/', ReportConfirmAPI.as_view({"post": "isCoordinatorConfirmedReport"})),    
    path('api/reportConfirm/confirmedReports/<int:contract_id>/<int:date_id>/', ReportConfirmAPI.as_view({"get": "getConfirmedReports"})),   

    path('api/financialInfos/updateFinancialInfo/<int:financialInfoId>/', FinancialInfoAPI.as_view({"post": "updateFinancialInfo"})),    

    path('api/financialInfos/contractMonthList/', FinancialInfoAPI.as_view({"post": "contractMonthList"})),    
    path('api/hses/contractMonthList/', HseAPI.as_view({"post": "contractMonthList"})),    
    path('api/progressStates/contractMonthList/', ProgressStateAPI.as_view({"post": "contractMonthList"})),
    path('api/timeProgressStates/contractMonthList/', TimeProgressStateAPI.as_view({"post": "contractMonthList"})),
    path('api/invoices/contractMonthList/', InvoiceAPI.as_view({"post": "contractMonthList"})),
    path('api/financialInvoices/contractMonthList/', FinancialInvoiceAPI.as_view({"post": "contractMonthList"})),
    path('api/pmsProgresses/contractMonthList/', PmsprogressAPI.as_view({"post": "contractMonthList"})),
    path('api/budgetCosts/contractMonthList/', BudgetCostAPI.as_view({"post": "contractMonthList"})),
    path('api/budgetCosts/setAdminDescription/', BudgetCostAPI.as_view({"put": "setAdminDescription"})),
    path('api/workVolumes/contractMonthList/', WorkVolumeAPI.as_view({"post": "contractMonthList"})),
    path('api/machineries/contractMonthList/', MachineryAPI.as_view({"post": "contractMonthList"})),
    path('api/projectPersonals/contractMonthList/', ProjectPersonalAPI.as_view({"post": "contractMonthList"})),
    path('api/problems/contractMonthList/', ProblemAPI.as_view({"post": "contractMonthList"})),
    path('api/criticalActions/contractMonthList/', CriticalActionAPI.as_view({"post": "contractMonthList"})),

    path('api/financialInfos/contractMonthReportList/<int:contractid>/<int:dateid>/', FinancialInfoAPI.as_view({"get": "contractMonthReportList"})),    
    path('api/hses/contractMonthReportList/<int:contractid>/<int:dateid>/', HseAPI.as_view({"get": "contractMonthReportList"})),
    path('api/progressStates/contractMonthReportList/<int:contractid>/<int:dateid>/', ProgressStateAPI.as_view({"get": "contractMonthReportList"})),
    path('api/invoices/contractMonthReportList1/<int:contractid>/<int:dateid>/', InvoiceAPI.as_view({"get": "contractMonthReportList1"})),
    path('api/invoices/contractMonthReportList2/<int:contractid>/<int:dateid>/', InvoiceAPI.as_view({"get": "contractMonthReportList2"})),
    path('api/financialInvoices/contractMonthReportList/<int:contractid>/<int:dateid>/', FinancialInvoiceAPI.as_view({"get": "contractMonthReportList"})),
    path('api/pmsProgresses/contractMonthReportList/<int:contractid>/<int:dateid>/', PmsprogressAPI.as_view({"get": "contractMonthReportList"})),
    path('api/budgetCosts/contractMonthReportList/<int:contractid>/<int:dateid>/', BudgetCostAPI.as_view({"get": "contractMonthReportList"})),
    path('api/workVolumes/contractMonthReportList/<int:contractid>/<int:dateid>/', WorkVolumeAPI.as_view({"get": "contractMonthReportList"})),
    path('api/machineries/contractMonthReportList/<int:contractid>/<int:dateid>/', MachineryAPI.as_view({"get": "contractMonthReportList"})),
    path('api/projectPersonals/contractMonthReportList/<int:contractid>/<int:dateid>/', ProjectPersonalAPI.as_view({"get": "contractMonthReportList"})),
    path('api/problems/contractMonthReportList/<int:contractid>/<int:dateid>/', ProblemAPI.as_view({"get": "contractMonthReportList"})),
    path('api/criticalActions/contractMonthReportList/<int:contractid>/<int:dateid>/', CriticalActionAPI.as_view({"get": "contractMonthReportList"})),
]

urlpatterns += router.urls

