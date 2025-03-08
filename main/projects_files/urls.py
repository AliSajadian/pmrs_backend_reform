from rest_framework import routers
from django.urls import path, include

from .api import *
       
router = routers.DefaultRouter()
router.register('api/hseReportDox', HseReportDoxAPI, basename='hseReportDox')
router.register('api/projectDox', ProjectDoxAPI, basename='projectDox')
router.register('api/contractorDox', ContractorDoxAPI, basename='contractorDox')
router.register('api/projectMonthlyDox', ProjectMonthlyDoxAPI, basename='projectMonthlyDox')
router.register('api/approvedInvoiceDox', ApprovedInvoiceDoxAPI, basename='hseReportDox')
router.register('api/zones', ZoneAPI, basename='zones')

# router.register('api/reportVisit', ReportVisitAPI, basename='reportVisit')

urlpatterns = [
    path('api/reportdox/', ReportDoxAPI.as_view()),
    
    path('api/zones/contractZoneList/<int:contractid>/', ZoneAPI.as_view({"get": "contractZoneList"})),    

    path('api/zoneImages/', ZoneImagesAPI.as_view()),
    path('api/zoneImages/<int:pk>/', ZoneImagesAPI.as_view()),   
    path('api/getZoneImages/', getContractZoneImages), 
    path('api/updateZoneImage/<int:pk>/', updateZoneImage),    
    path('api/zoneImages/<int:contractid>/<int:dateid>/', ZoneImagesAPI.as_view()),    

    path('api/allContractsZonesImages/<int:dateid>/', getReportAllProjectZonesImages), 
    path('api/allContractsZonesImagesEx/<int:fromDateid>/<int:toDateid>/', getReportAllProjectZonesImagesEx), 
    path('api/selectedContractsAllZonesImages/<int:dateid>/', getReportSelectedProjectAllZonesImages), 
    path('api/selectedContractsAllZonesImagesEx/<int:fromDateid>/<int:toDateid>/', getReportSelectedProjectAllZonesImagesEx), 
    path('api/contractZoneImages/<int:zoneid>/', getReportProjectZoneImages), 

    path('api/hseReportDox/contractList/<int:contractid>/', HseReportDoxAPI.as_view({"get": "contractList"})),    
    path('api/hseReportDox/download/<int:id>/', HseReportDoxAPI.as_view({"get": "download"})),  
      
    path('api/projectDox/contractList/<int:userid>/<int:contractid>/<int:dateid>/<int:reportid>/', ProjectDoxAPI.as_view({"get": "contractList"})),    
    path('api/projectDox/download/<int:id>/', ProjectDoxAPI.as_view({"get": "download"})),    
    
    path('api/contractorDox/contractList/<int:contractid>/', ContractorDoxAPI.as_view({"get": "contractList"})),    
    path('api/contractorDox/download/<int:id>/', ContractorDoxAPI.as_view({"get": "download"})),    
    
    path('api/projectMonthlyDox/contractList/<int:userid>/<int:contractid>/<int:dateid>/<int:reportid>/', ProjectMonthlyDoxAPI.as_view({"get": "contractList"})),    
    path('api/projectMonthlyDox/download/<int:id>/', ProjectMonthlyDoxAPI.as_view({"get": "download"})), 
       
    path('api/approvedInvoiceDox/contractMonthList/<int:contractid>/<int:dateid>/', ApprovedInvoiceDoxAPI.as_view({"get": "contractMonthList"})),    
    path('api/approvedInvoiceDox/download/<int:id>/', ApprovedInvoiceDoxAPI.as_view({"get": "download"})),  
    
    path('api/reportVisit/<int:contractid>/<int:dateid>/', ReportVisitAPI.as_view()),    
    path('api/reportVisit/', ReportVisitAPI.as_view()),    
]

urlpatterns += router.urls

