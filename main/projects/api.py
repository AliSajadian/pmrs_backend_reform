"""
API for the projects application.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Max, Q
from datetime import datetime

from django.contrib.auth import get_user_model
from contracts.models import *
from contracts.services import GregorianToShamsi
from projects_files.services import SetReportVisit
from projects.models import ReportDate, ReportConfirm, FinancialInfo, Hse, ProgressState, \
    TimeprogressState, Invoice, FinancialInvoice, WorkVolume, PmsProgress, Budgetcost, Problem, \
        CriticalAction, ContractReportDate, Machinary, ProjectPersonnel 
from .serializers import ReportDateSerializerEx, ReportConfirmSerializer, ReportsConfirmedSerializer, \
    ProjectManagerReportConfirmSerializer, CoordinatorReportConfirmSerializer, FinancialInfoSerializer, \
        FinancialInfoReportSerializer, HseSerializer, ProgressStateSerializer, TimeProgressStateSerializer, \
            InvoiceSerializer, FinancialInvoiceSerializer, WorkvolumeSerializer, PmsprogressSerializer, \
                BudgetCostSerializer, MachinerySerializer, ProjectPersonalSerializer, ProblemSerializer, \
                    CriticalActionSerializer, HseReportSerializer, ProgressStateReportSerializer, \
                        InvoiceReport1Serializer, InvoiceReport2Serializer, FinancialInvoiceReportSerializer, \
                            BudgetCostReportSerializer, ProjectPersonalReportSerializer


class ReportDateAPIEx(APIView):
    """
    API for the ReportDate model.
    """
    permission_classes = [
        permissions.IsAuthenticated
    ]

    '''
        READ Report Date:
        
        every time read Report date model if encounter to begin of new persian month it 
        create new record for last month in ReportDate model this way always the ReportDate 
        contain all persian months until last month
        
        if user read ReportDate model after a few months then system create a record for 
        each of those months to reach to last month
    '''
    def get(self, *args, **kwargs):
        """
        Get the report dates.
        """
        max_date_id = ReportDate.objects.aggregate(Max('dateid'))['dateid__max']
        date = ReportDate.objects.get(pk=max_date_id)
        y1 = int(date.year)
        m1 = int(date.month)

        now = GregorianToShamsi(datetime.now())
        y2 = int(now[0:4])
        m2 = int(now[5:now.find('-', 5)])
        if(m2 > 1):
            m2 = m2 - 1
        else:
            m2 = 12
            y2 = y2 - 1
        
        loop = 0
        if((y2 - y1) > 1 or ((y2 - y1) == 0 and (m2 - m1) > 0) or ((y2 -y1) == 1 and (12 - m1 + m2 > 0))):
            loop = 1
        
        while(loop == 1):
            if(y2 == y1):
                m1 = m1 + 1
                date = ReportDate.objects.create(year=str(y1), month=str(m1))
                
                flag = 0
                contracts = Contract.objects.exclude(contract__exact='test').filter(iscompleted__exact=False)
                for contract in contracts:
                    flag = ContractReportDate.objects.filter(contractid__exact=contract.contractid, 
                                                          dateid__year__exact=y2,
                                                          dateid__month__exact=m2).count()
                    if flag == 0:
                        ContractReportDate.objects.create(contractid=contract, dateid=date)
                        
                if(m2 == m1):
                    loop = 0
                    
            elif(y2 - y1 > 0):
                m1 = m1 + 1
                if(m1 > 12):
                    m1 = 1
                    y1 = y1 + 1
                
                date = ReportDate.objects.create(year=str(y1), month=str(m1))

                flag = 0
                contracts = Contract.objects.exclude(contract__exact='test').filter(iscompleted__exact=False)
                for contract in contracts:
                    flag = ContractReportDate.objects.filter(contractid__exact=contract.contractid, 
                                                          dateid__year__exact=y2,
                                                          dateid__month__exact=m2).count()
                    if flag == 0:
                        ContractReportDate.objects.create(contractid=contract, dateid=date)
                
                if(y2 == y1 and m2 == m1):
                    loop = 0
                            
        reportDates = ReportDate.objects.all().order_by('-dateid')
        serializer = ReportDateSerializerEx(reportDates, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    
    
class ReportConfirmAPI(viewsets.ModelViewSet):
    """
    API for the ReportConfirm model.
    """
    queryset = ReportConfirm.objects.all()
    serializer_class = ReportConfirmSerializer
    # permission_classes = [
    #     permissions.IsAuthenticated
    # ]


    @action(detail=False, methods=['get'])   
    def getConfirmedReports(self, *args, **kwargs):
        """
        Get the confirmed reports.
        """
        try:
            contractId = int(kwargs["contract_id"])
            dateId = int(kwargs["date_id"])
            
            objects = ReportConfirm.objects.filter(
                Q(contractid__exact=contractId, dateid__exact=dateId, user_c__gt=0) | 
                Q(contractid__exact=contractId, dateid__exact=dateId, pm_c__gt=0))
            serializer = ReportsConfirmedSerializer(instance=objects, many=True) 
                
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])   
    def isProjectManagerConfirmedReport(self, request, *args, **kwargs):
        """
        Check if the project manager has confirmed the report.
        """
        try:
            data = request.data
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            type = int(data["type"])
            
            object = ReportConfirm.objects.filter(contractid__exact=contractId, dateid__exact=dateId, pm_c__gt=0)[0]
            
            serializer = ProjectManagerReportConfirmSerializer(instance=object, many=False) \
                if object is not None else {"pm_c":"0", "pmconfirmdate":""}
                
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['post'])   
    def projectManagerReportConfirm(self, request, *args, **kwargs):
        """
        Confirm the project manager report.
        """
        try:
            data = request.data
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            confirmed = int(data["confirmed"])
            # userId = int(data["userid"])

            objects = ReportConfirm.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            if(objects is not None and len(objects) == 15):
                for obj in objects:
                    obj.pm_c = confirmed
                    obj.pmconfirmdate = datetime.now()
                    obj.save()
                # return Response({"status": "success"}, status=status.HTTP_200_OK)
                objects = ReportConfirm.objects.filter(
                    Q(contractid__exact=contractId, dateid__exact=dateId, user_c__gt=0) | 
                    Q(contractid__exact=contractId, dateid__exact=dateId, pm_c__gt=0))
                serializer = ReportsConfirmedSerializer(instance=objects, many=True) 
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            else: 
                # contract = Contract.objects.get(pk=contractId)
                # date = ReportDate.objects.get(pk=dateId)
                # user = get_user_model().objects.get(pk=userId)
                # ReportConfirm.objects.create(contractid=contract, 
                #                              dateid=date, 
                #                              pm_c=confirmed, 
                #                              pmconfirmdate = datetime.now(), 
                #                              userId = user)
                return Response({"status": "error", "data": "Err:01"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])   
    def isCoordinatorConfirmedReport(self, request, *args, **kwargs):
        """
        Check if the coordinator has confirmed the report.
        """
        try:
            data = request.data
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            type = int(data["type"])
            
            objects = ReportConfirm.objects.filter(contractid__exact=contractId, dateid__exact=dateId, type__exact=type)
            object = objects[0] if (objects is not None and len(objects) > 0) else {"userconfirmer":"", "user_c":"0", "userconfirmdate":""}
            serializer = CoordinatorReportConfirmSerializer(instance=object, many=False) 
                
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # =======
    @action(detail=False, methods=['post'])   
    def coordinatorReportConfirm(self, request, *args, **kwargs):
        """
        Confirm the coordinator report.
        """
        try:
            data = request.data
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            userId = int(data["userid"])
            confirmed = int(data["confirmed"])
            type = int(data["type"])
            
            objects = ReportConfirm.objects.filter(contractid__exact=contractId, dateid__exact=dateId, type__exact=type)
            object = objects[0] if (objects is not None and len(objects) > 0) else None

            if(object is not None):
                object.user_c = confirmed
                object.userid = userId
                object.userconfirmdate = datetime.now()
                object.save()
            else: 
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                user = get_user_model().objects.get(pk=userId)
                ReportConfirm.objects.create(contractid=contract, dateid=date, userid=user, 
                                             type=type, user_c=confirmed, userconfirmdate = datetime.now())
            
            # object = ReportConfirm.objects.filter(contractid__exact=contractId, dateid__exact=dateId, type__exact=type)[0]
            # serializer = CoordinatorReportConfirmSerializer(instance=object, many=False) \
            #     if object is not None else {"userconfirmer":"", "user_c":"0", "userconfirmdate":""}
            objects = ReportConfirm.objects.filter(
                Q(contractid__exact=contractId, dateid__exact=dateId, user_c__gt=0) | 
                Q(contractid__exact=contractId, dateid__exact=dateId, pm_c__gt=0))
            serializer = ReportsConfirmedSerializer(instance=objects, many=True) 

            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
class FinancialInfoAPI(viewsets.ModelViewSet):
    """
    API for the FinancialInfo model.
    """
    queryset = FinancialInfo.objects.all()
    serializer_class = FinancialInfoSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=False, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the financial info for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            flg = 1	if FinancialInfo.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count() > 0 else 0

            if flg == 0:
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                FinancialInfo.objects.update_or_create(contractid=contract ,dateid=date)  
                          
            financialinfos = FinancialInfo.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = FinancialInfoSerializer(instance=financialinfos[0] if len(financialinfos) > 0 else None, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the financial info for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
                                    
            financialInfos = FinancialInfo.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = FinancialInfoReportSerializer(instance=financialInfos[0] if len(financialInfos) > 0 else None, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods='post')
    def updateFinancialInfo(self, request, *args, **kwargs):
        """
        Update the financial info.
        """
        try:
            financialInfoId = int(kwargs["financialInfoId"])
            
            data = request.data
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            lastclaimedinvoice_r = int(data["lastclaimedinvoice_r"])
            lastclaimedinvoice_fc = int(data["lastclaimedinvoice_fc"])
            lci_no = int(data["lci_no"])
            lastverifiedinvoice_r = int(data["lastverifiedinvoice_r"])
            lastverifiedinvoice_fc = int(data["lastverifiedinvoice_fc"])
            lvi_no = int(data["lvi_no"])
            lastclaimedadjustmentinvoice_r = int(data["lastclaimedadjustmentinvoice_r"])
            lastclaimedadjustmentinvoice_fc = int(data["lastclaimedadjustmentinvoice_fc"])
            lcai_no = int(data["lcai_no"])
            lastverifiedadjustmentinvoice_r = int(data["lastverifiedadjustmentinvoice_r"])
            lastverifiedadjustmentinvoice_fc = int(data["lastverifiedadjustmentinvoice_fc"])
            lvai_no = int(data["lvai_no"])
            lastclaimedextraworkinvoice_r = int(data["lastclaimedextraworkinvoice_r"])
            lastclaimedextraworkinvoice_fc = int(data["lastclaimedextraworkinvoice_fc"])
            lcewi_no = int(data["lcewi_no"])
            lastverifiedextraworkinvoice_r = int(data["lastverifiedextraworkinvoice_r"])
            lastverifiedextraworkinvoice_fc = int(data["lastverifiedextraworkinvoice_fc"])
            lvewi_no = int(data["lvewi_no"])
            lastclaimbill_r = int(data["lastclaimbill_r"])
            lastclaimbill_fc = int(data["lastclaimbill_fc"])
            lcb_no = int(data["lcb_no"])
            lastclaimbillverified_r = int(data["lastclaimbillverified_r"])
            lastclaimbillverified_fc = int(data["lastclaimbillverified_fc"])
            lcbv_no = int(data["lcbv_no"])
            lastclaimbillrecievedamount_r = int(data["lastclaimbillrecievedamount_r"])
            lastclaimbillrecievedamount_fc = int(data["lastclaimbillrecievedamount_fc"])
            cumulativeclientpayment_r = int(data["cumulativeclientpayment_r"])
            cumulativeclientpayment_fc = int(data["cumulativeclientpayment_fc"])
            clientprepaymentdeferment_r = int(data["clientprepaymentdeferment_r"])
            clientprepaymentdeferment_fc = int(data["clientprepaymentdeferment_fc"])
            estcost_r = int(data["estcost_r"])
            estcost_fc = int(data["estcost_fc"])
            estclientpayment_r = int(data["estclientpayment_r"])
            estclientpayment_fc = int(data["estclientpayment_fc"])
            estdebitcredit_r = int(data["estdebitcredit_r"])
            estdebitcredit_fc = int(data["estdebitcredit_fc"])
            
            financialInfo = FinancialInfo.objects.get(financialinfoid__exact=financialInfoId)
            financialInfo.lastclaimedinvoice_r=lastclaimedinvoice_r
            financialInfo.lastclaimedinvoice_fc=lastclaimedinvoice_fc
            financialInfo.lci_no=lci_no
            financialInfo.lastverifiedinvoice_r=lastverifiedinvoice_r
            financialInfo.lastverifiedinvoice_fc=lastverifiedinvoice_fc
            financialInfo.lvi_no=lvi_no
            financialInfo.lastclaimedadjustmentinvoice_r=lastclaimedadjustmentinvoice_r
            financialInfo.lastclaimedadjustmentinvoice_fc=lastclaimedadjustmentinvoice_fc
            financialInfo.lcai_no=lcai_no
            financialInfo.lastverifiedadjustmentinvoice_r=lastverifiedadjustmentinvoice_r
            financialInfo.lastverifiedadjustmentinvoice_fc=lastverifiedadjustmentinvoice_fc
            financialInfo.lvai_no=lvai_no
            financialInfo.lastclaimedextraworkinvoice_r=lastclaimedextraworkinvoice_r
            financialInfo.lastclaimedextraworkinvoice_fc=lastclaimedextraworkinvoice_fc
            financialInfo.lcewi_no=lcewi_no
            financialInfo.lastverifiedextraworkinvoice_r=lastverifiedextraworkinvoice_r
            financialInfo.lastverifiedextraworkinvoice_fc=lastverifiedextraworkinvoice_fc
            financialInfo.lvewi_no=lvewi_no
            financialInfo.lastclaimbill_r=lastclaimbill_r
            financialInfo.lastclaimbill_fc=lastclaimbill_fc
            financialInfo.lcb_no=lcb_no
            financialInfo.lastclaimbillverified_r=lastclaimbillverified_r
            financialInfo.lastclaimbillverified_fc=lastclaimbillverified_fc
            financialInfo.lcbv_no=lcbv_no
            financialInfo.lastclaimbillrecievedamount_r=lastclaimbillrecievedamount_r
            financialInfo.lastclaimbillrecievedamount_fc=lastclaimbillrecievedamount_fc
            financialInfo.cumulativeclientpayment_r=cumulativeclientpayment_r
            financialInfo.cumulativeclientpayment_fc=cumulativeclientpayment_fc
            financialInfo.clientprepaymentdeferment_r=clientprepaymentdeferment_r
            financialInfo.clientprepaymentdeferment_fc=clientprepaymentdeferment_fc
            financialInfo.estcost_r=estcost_r
            financialInfo.estcost_fc=estcost_fc
            financialInfo.estclientpayment_r=estclientpayment_r
            financialInfo.estclientpayment_fc=estclientpayment_fc
            financialInfo.estdebitcredit_r=estdebitcredit_r
            financialInfo.estdebitcredit_fc=estdebitcredit_fc
            financialInfo.save()
            
            invoice_r = Invoice.objects.filter(contractid__exact=contractId, dateid__exact=dateId, r__exact=True).first()
            if invoice_r:
                invoice_r.aci_n_r=lastverifiedinvoice_r
                invoice_r.aca_n_r=lastverifiedadjustmentinvoice_r
                invoice_r.ew_n_r=lastverifiedextraworkinvoice_r
                invoice_r.icc_n_r=lastclaimedinvoice_r
                invoice_r.acc_n_r=lastclaimedadjustmentinvoice_r
                invoice_r.ewcc_n_r=lastclaimedextraworkinvoice_r
                invoice_r.save()
            
            invoice_fc = Invoice.objects.filter(contractid__exact=contractId, dateid__exact=dateId, r__exact=False).first()
            if invoice_fc:
                invoice_fc.aci_n_fc=lastverifiedinvoice_fc
                invoice_fc.aca_n_fc=lastverifiedadjustmentinvoice_fc
                invoice_fc.ew_n_fc=lastverifiedextraworkinvoice_fc
                invoice_fc.icc_n_fc=lastclaimedinvoice_fc
                invoice_fc.acc_n_fc=lastclaimedadjustmentinvoice_fc
                invoice_fc.ewcc_n_fc=lastclaimedextraworkinvoice_fc
                invoice_fc.save()

            financialinfos = FinancialInfo.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = FinancialInfoSerializer(instance=financialinfos[0] if len(financialinfos) > 0 else None, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HseAPI(viewsets.ModelViewSet):
    """
    API for the Hse model.
    """
    queryset = Hse.objects.all()
    serializer_class = HseSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    
    @action(detail=False, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the HSE for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            flg = 1	if Hse.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count() > 0 else 0

            if flg == 0:
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                Hse.objects.update_or_create(contractid=contract ,dateid=date, totaloperationdays=0,   
                                       withouteventdays=0, deathno=0, woundno=0, disadvantageeventno=0)
                            
            hses = Hse.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = HseSerializer(instance=hses[0] if len(hses) > 0 else None, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the HSE for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
                                    
            hses = Hse.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = HseReportSerializer(instance=hses[0] if len(hses) > 0 else None, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProgressStateAPI(viewsets.ModelViewSet):
    """
    API for the ProgressState model.
    """
    queryset = ProgressState.objects.all()
    serializer_class = ProgressStateSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):      
        """
        Get the progress state for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            flg = 1	if ProgressState.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count() > 0 else 0

            if flg == 0:
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                ProgressState.objects.update_or_create(contractid=contract ,dateid=date, 
                                                       defaults={
                                                       'plan_replan':'00', 'pp_e':0, 'ap_e':0, 'pp_p':0, 'ap_p':0,  
                                                       'pp_c':0, 'ap_c':0, 'pp_t':0, 'ap_t':0, 'pr_t':0, 'pfc_t':0})
            
            progressStates = ProgressState.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('dateid')
            serializer = ProgressStateSerializer(instance=progressStates, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the progress state for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            progressStates = ProgressState.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('-dateid')[:6:-1]
            serializer = ProgressStateReportSerializer(instance=progressStates, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
 
class TimeProgressStateAPI(viewsets.ModelViewSet):
    """
    API for the TimeProgressState model.
    """
    queryset = TimeprogressState.objects.all()
    serializer_class = TimeProgressStateSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the time progress state for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
                       
            flg = 1	if TimeprogressState.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count() > 0 else 0

            if flg == 0:
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                # TimeprogressState.objects.update_or_create(contractid=contract ,dateid=date, 
                #                                            defaults={'plan_replan':'00', 'eep_date':datetime.now(), 'eee_date':datetime.now(), 
                #                                            'epp_date':datetime.now(), 'epe_date':datetime.now(), 'ecp_date':datetime.now(), 
                #                                            'ece_date':datetime.now(), 'epjp_date':datetime.now(), 'epje_date':datetime.now()})

                TimeprogressState.objects.update_or_create(contractid=contract ,dateid=date, 
                                                           defaults={'plan_replan':'00'})
            
            timeProgressStates = TimeprogressState.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('dateid')
            serializer = TimeProgressStateSerializer(instance=timeProgressStates, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvoiceAPI(viewsets.ModelViewSet):
    """
    API for the Invoice model.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the invoice for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            flg = 1	if Invoice.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count() > 0 else 0

            if flg == 0:
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                financialInfos = FinancialInfo.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
                
                Invoice.objects.update_or_create(contractid=contract ,dateid=date, r=True, defaults={ 'senddate': datetime.now(),
                                        'aci_g_r':0, 'aci_n_r':financialInfos[0].lastverifiedinvoice_r if financialInfos and len(financialInfos) > 0 else 0, 
                                        'aci_g_fc':None, 'aci_n_fc':None,
                                        'aca_g_r':0, 'aca_n_r':financialInfos[0].lastverifiedadjustmentinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'aca_g_fc':None, 'aca_n_fc':None,
                                        'ew_g_r':0, 'ew_n_r':financialInfos[0].lastverifiedextraworkinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'ew_g_fc':None, 'ew_n_fc':None,
                                        'icc_g_r':0, 'icc_n_r':financialInfos[0].lastclaimedinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'icc_g_fc':None, 'icc_n_fc':None,
                                        'acc_g_r':0, 'acc_n_r':financialInfos[0].lastclaimedadjustmentinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'acc_g_fc':None, 'acc_n_fc':None,
                                        'ewcc_g_r':0, 'ewcc_n_r':financialInfos[0].lastclaimedextraworkinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'ewcc_g_fc':None, 'ewcc_n_fc':None,
                                        'cvat_r':0, 'cvat_fc':None, 'cpi_r':0, 'cpi_fc':None, 'ccpi_a_r':0, 'ccpi_a_fc':None,
                                        'ccpi_a_vat_r':0, 'ccpi_a_vat_fc':None, 'ccpi_a_vat_ew_r':0, 'ccpi_a_vat_ew_fc':None, 
                                        'cp_pp_r':0, 'cp_pp_fc':None, 'pp_pp_r':0, 'pp_pp_fc':None, 'm':False, 'description':None})

                Invoice.objects.update_or_create(contractid=contract ,dateid=date, r=False, defaults={ 'senddate': datetime.now(),
                                        'aci_g_fc':0, 'aci_n_fc':financialInfos[0].lastverifiedinvoice_fc if financialInfos and len(financialInfos) > 0 else 0, 
                                        'aci_g_r':None, 'aci_n_r':None,
                                        'aca_g_fc':0, 'aca_n_fc':financialInfos[0].lastverifiedadjustmentinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'aca_g_r':None, 'aca_n_r':None,
                                        'ew_g_fc':0, 'ew_n_fc':financialInfos[0].lastverifiedextraworkinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'ew_g_r':None, 'ew_n_r':None,
                                        'icc_g_fc':0, 'icc_n_fc':financialInfos[0].lastclaimedinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'icc_g_r':None, 'icc_n_r':None,
                                        'acc_g_fc':0, 'acc_n_fc':financialInfos[0].lastclaimedadjustmentinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'acc_g_r':None, 'acc_n_r':None,
                                        'ewcc_g_fc':0, 'ewcc_n_fc':financialInfos[0].lastclaimedextraworkinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'ewcc_g_r':None, 'ewcc_n_r':None,
                                        'cvat_fc':0, 'cvat_r':None, 'cpi_fc':0, 'cpi_r':None, 'ccpi_a_fc':0, 'ccpi_a_r':None,
                                        'ccpi_a_vat_fc':0, 'ccpi_a_vat_r':None, 'ccpi_a_vat_ew_fc':0, 'ccpi_a_vat_ew_r':None, 
                                        'cp_pp_fc':0, 'cp_pp_r':None, 'pp_pp_fc':0, 'pp_pp_r':None, 'm':False, 'description':None})
            
                        
            invoices = Invoice.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('dateid')
            serializer = InvoiceSerializer(data=invoices, many=True)
            serializer.is_valid()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def contractMonthReportList1(self, request, *args, **kwargs):
        """
        Get the invoice for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            invoice = Invoice.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = InvoiceReport1Serializer(instance=invoice[0] if len(invoice) > 0 else None, many=False)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def contractMonthReportList2(self, request, *args, **kwargs):
        """
        Get the invoice for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            invoices = Invoice.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('-dateid')[:9:-1]
            serializer = InvoiceReport2Serializer(instance=invoices, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FinancialInvoiceAPI(viewsets.ModelViewSet):
    """
    API for the FinancialInvoice model.
    """
    queryset = FinancialInvoice.objects.all()
    serializer_class = FinancialInvoiceSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the financial invoice for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            flg = 1	if FinancialInvoice.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count() > 0 else 0

            if flg == 0:
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                financialInfos = FinancialInfo.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
                # FinancialInvoice.objects.update_or_create(contractid=contract ,dateid=date, defaults={'senddate':None, 'invoicetype':'', 'alino':None,
                #                              'almino':None, 'aci_g_r':None, 'aci_g_fc':None, 'aca_g_r':None, 'aca_g_fc':None, 
                #                              'ew_g_r':None, 'ew_g_fc':None, 'icc_g_r':None, 'icc_g_fc':None, 'acc_g_r':None, 
                #                              'acc_g_fc':None, 'ewcc_g_r':None, 'ewcc_g_fc':None, 'aci_n_r':None, 'aci_n_fc':None,
                #                              'aca_n_r':None, 'aca_n_fc':None, 'ew_n_r':None, 'ew_n_fc':None, 'icc_n_r':None, 
                #                              'icc_n_fc':None, 'acc_n_r':None, 'acc_n_fc':None, 'ewcc_n_r':None, 'ewcc_n_fc':None, 
                #                              'cvat_r':None, 'cvat_fc':None, 'cpi_r':None, 'cpi_fc':None, 'ccpi_a_r':None, 
                #                              'ccpi_a_fc':None, 'ccpi_a_vat_r':None, 'ccpi_a_vat_fc':None, 'ccpi_a_vat_ew_r':None, 
                #                              'ccpi_a_vat_ew_fc':None, 'cp_pp_r':None, 'cp_pp_fc':None, 'pp_pp_r':None, 
                #                              'pp_pp_fc':None, 'r':None, 'm':None, 'typevalue':None})
                FinancialInvoice.objects.update_or_create(contractid=contract ,dateid=date, r=True, defaults={ 'senddate': datetime.now(), 'invoicetype':'T', 'alino':None, 'almino':None, 
                                        'aci_g_r':0, 'aci_n_r':financialInfos[0].lastverifiedinvoice_r if financialInfos and len(financialInfos) > 0 else 0, 
                                        'aci_g_fc':None, 'aci_n_fc':None,
                                        'aca_g_r':0, 'aca_n_r':financialInfos[0].lastverifiedadjustmentinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'aca_g_fc':None, 'aca_n_fc':None,
                                        'ew_g_r':0, 'ew_n_r':financialInfos[0].lastverifiedextraworkinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'ew_g_fc':None, 'ew_n_fc':None,
                                        'icc_g_r':0, 'icc_n_r':financialInfos[0].lastclaimedinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'icc_g_fc':None, 'icc_n_fc':None,
                                        'acc_g_r':0, 'acc_n_r':financialInfos[0].lastclaimedadjustmentinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'acc_g_fc':None, 'acc_n_fc':None,
                                        'ewcc_g_r':0, 'ewcc_n_r':financialInfos[0].lastclaimedextraworkinvoice_r if financialInfos and len(financialInfos) > 0 else 0,
                                        'ewcc_g_fc':None, 'ewcc_n_fc':None,
                                        'cvat_r':0, 'cvat_fc':None, 'cpi_r':0, 'cpi_fc':None, 'ccpi_a_r':0, 'ccpi_a_fc':None,
                                        'ccpi_a_vat_r':0, 'ccpi_a_vat_fc':None, 'ccpi_a_vat_ew_r':0, 'ccpi_a_vat_ew_fc':None, 
                                        'cp_pp_r':0, 'cp_pp_fc':None, 'pp_pp_r':0, 'pp_pp_fc':None, 'm':True, 'typevalue':None})

                FinancialInvoice.objects.update_or_create(contractid=contract ,dateid=date, r=False, defaults={ 'senddate': datetime.now(), 'invoicetype':'T', 'alino':None, 'almino':None, 
                                        'aci_g_fc':0, 'aci_n_fc':financialInfos[0].lastverifiedinvoice_fc if financialInfos and len(financialInfos) > 0 else 0, 
                                        'aci_g_r':None, 'aci_n_r':None,
                                        'aca_g_fc':0, 'aca_n_fc':financialInfos[0].lastverifiedadjustmentinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'aca_g_r':None, 'aca_n_r':None,
                                        'ew_g_fc':0, 'ew_n_fc':financialInfos[0].lastverifiedextraworkinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'ew_g_r':None, 'ew_n_r':None,
                                        'icc_g_fc':0, 'icc_n_fc':financialInfos[0].lastclaimedinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'icc_g_r':None, 'icc_n_r':None,
                                        'acc_g_fc':0, 'acc_n_fc':financialInfos[0].lastclaimedadjustmentinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'acc_g_r':None, 'acc_n_r':None,
                                        'ewcc_g_fc':0, 'ewcc_n_fc':financialInfos[0].lastclaimedextraworkinvoice_fc if financialInfos and len(financialInfos) > 0 else 0,
                                        'ewcc_g_r':None, 'ewcc_n_r':None,
                                        'cvat_fc':0, 'cvat_r':None, 'cpi_fc':0, 'cpi_r':None, 'ccpi_a_fc':0, 'ccpi_a_r':None,
                                        'ccpi_a_vat_fc':0, 'ccpi_a_vat_r':None, 'ccpi_a_vat_ew_fc':0, 'ccpi_a_vat_ew_r':None, 
                                        'cp_pp_fc':0, 'cp_pp_r':None, 'pp_pp_fc':0, 'pp_pp_r':None, 'm':True, 'typevalue':None})
            
            financialInvoices = FinancialInvoice.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('dateid')
            serializer = FinancialInvoiceSerializer(data=financialInvoices, many=True)
            serializer.is_valid()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the work volume for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            invoices = FinancialInvoice.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('-dateid')[:9:-1]
            serializer = FinancialInvoiceReportSerializer(instance=invoices, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WorkVolumeAPI(viewsets.ModelViewSet):
    """
    API for the WorkVolume model.
    """
    queryset = WorkVolume.objects.all()
    serializer_class = WorkvolumeSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the work volume for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            contract = Contract.objects.get(pk=contractId)
            date = ReportDate.objects.get(pk=dateId)

            flg = 0
            record_count = WorkVolume.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count()
            last_date_id = ReportDate.objects.filter(dateid__lt=dateId).aggregate(Max('dateid'))['dateid__max']

            if WorkVolume.objects.filter(contractid__exact=contractId, dateid__exact=last_date_id).count() > 1:
                flg = 1	
                
            if record_count == 0:
                if flg == 0:
                    WorkVolume.objects.bulk_create([
                        WorkVolume(contractid=contract, dateid=date, work="خاکبرداری(متر مکعب)"),
                        WorkVolume(contractid=contract, dateid=date, work="خاکریزی(متر مکعب)"),
                        WorkVolume(contractid=contract, dateid=date, work="بتن ریزی(متر مکعب)"),
                        WorkVolume(contractid=contract, dateid=date, work="نصب اسکلت فلزی(تن)"),
                        WorkVolume(contractid=contract, dateid=date, work="نصب تجهبزات داخلی(تن)"),
                        WorkVolume(contractid=contract, dateid=date, work="نصب تجهیزات خارجی(تن)"),
                    ])
                else: 
                    workVolumes = WorkVolume.objects.filter(contractid__exact=contractId, dateid__exact=last_date_id)
                    for workvolume in workVolumes:
                        WorkVolume.objects.create(contractid=contract,  
                                                     dateid=date, 
                                                     work=workvolume.work, 
                                                     planestimate=workvolume.planestimate, 
                                                     totalestimate=workvolume.totalestimate,
                                                     executedsofar=workvolume.executedsofar)
                                    
            workVolumes = WorkVolume.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = WorkvolumeSerializer(instance=workVolumes, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, request, *args, **kwargs):
        """
        Get the work volume for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            workVolumes = WorkVolume.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = WorkvolumeSerializer(instance=workVolumes, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PmsprogressAPI(viewsets.ModelViewSet):
    """
    API for the PmsProgress model.
    """
    queryset = PmsProgress.objects.all()
    serializer_class = PmsprogressSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the PMS progress for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            contract = Contract.objects.get(pk=contractId)
            date = ReportDate.objects.get(pk=dateId)

            flg = 0
            record_count = PmsProgress.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count()
            last_date_id = ReportDate.objects.filter(dateid__lt=dateId).aggregate(Max('dateid'))['dateid__max']

            if PmsProgress.objects.filter(contractid__exact=contractId, dateid__exact=last_date_id).count() > 1:
                flg = 1	
                
            if record_count == 0:
                if flg == 0:
                    PmsProgress.objects.bulk_create([
                        PmsProgress(contractid=contract, dateid=date, item="کل کارهای سیویل"),
                        PmsProgress(contractid=contract, dateid=date, item="کل کارهای نصب"),
                        PmsProgress(contractid=contract, dateid=date, item="نصب اسکلت فلزی"),
                        PmsProgress(contractid=contract, dateid=date, item="بیل مکانیکی"),
                        PmsProgress(contractid=contract, dateid=date, item="نصب تجهیزات مکانیکال"),
                        PmsProgress(contractid=contract, dateid=date, item="نصب تجهیزات برق و ابزار دقیق"),
                        PmsProgress(contractid=contract, dateid=date, item="کل نصب تجهیزات داخلی (بدون در نظرگیری اسکلت فلزی)"),
                        PmsProgress(contractid=contract, dateid=date, item="کل نصب تجهیزات خارجی"),
                    ])
                else: 
                    pmsprogresses = PmsProgress.objects.filter(contractid__exact=contractId, dateid__exact=last_date_id)
                    for pmsprogress in pmsprogresses:
                        PmsProgress.objects.create(contractid=contract,  
                                                     dateid=date, item=pmsprogress.item, 
                                                     lastplanprogress=pmsprogress.lastplanprogress, 
                                                     lastplanvirtualprogress=pmsprogress.lastplanvirtualprogress)
                                    
            Pmsprogresses = PmsProgress.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = PmsprogressSerializer(instance=Pmsprogresses, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the PMS progress for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
                   
            Pmsprogresses = PmsProgress.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = PmsprogressSerializer(instance=Pmsprogresses, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

class BudgetCostAPI(viewsets.ModelViewSet):
    """
    API for the BudgetCost model.
    """
    queryset = Budgetcost.objects.all()
    serializer_class = BudgetCostSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the budget cost for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            flg = 1	if Budgetcost.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count() > 0 else 0

            if flg == 0:
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                Budgetcost.objects.update_or_create(contractid=contract ,dateid=date, 
                                                    defaults={'bac_r':0, 'bac_fc':0, 'eac_r':0, 'eac_fc':0, 
                                                    'ev_r':0, 'ev_fc':0, 'ac_r':0, 'ac_fc':0, 'description':''})

            budgetCosts = Budgetcost.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('dateid')
            serializer = BudgetCostSerializer(instance=budgetCosts, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['put'])
    def setAdminDescription(self, request, *args, **kwargs):
        """
        Set the admin description for the budget cost.
        """
        try:
            data = request.data
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            description = str(data["description"])
            
            budget = Budgetcost.objects.get(contractid__exact=contractId, dateid__exact=dateId)
            budget.description = description
            budget.save()
            
            return Response({"status": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the budget cost for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
                   
            budgetcosts = Budgetcost.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('-dateid')[:6:-1]
            serializer = BudgetCostReportSerializer(instance=budgetcosts, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

class MachineryAPI(viewsets.ModelViewSet):
    """
    API for the Machinery model.
    """
    queryset = Machinary.objects.all()
    serializer_class = MachinerySerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the machinery for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            contract = Contract.objects.get(pk=contractId)
            date = ReportDate.objects.get(pk=dateId)
            
            record_count = Machinary.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count()
            last_date_id = ReportDate.objects.filter(dateid__lt=dateId).aggregate(Max('dateid'))['dateid__max']

            flg = 1	if Machinary.objects.filter(contractid__exact=contractId, dateid__exact=last_date_id).count() > 0 else 0
            total_field_exist = False
            
            if record_count == 0:
                if flg == 0:
                    Machinary.objects.bulk_create([
                        Machinary(contractid=contract, dateid=date, machine="تاور کرین"),
                        Machinary(contractid=contract, dateid=date, machine="بولدوزر"),
                        Machinary(contractid=contract, dateid=date, machine="لودر"),
                        Machinary(contractid=contract, dateid=date, machine="بیل مکانیکی"),
                        Machinary(contractid=contract, dateid=date, machine="غلطک"),
                        Machinary(contractid=contract, dateid=date, machine="گریدر"),
                        Machinary(contractid=contract, dateid=date, machine="کمپرسی دو محور"),
                        Machinary(contractid=contract, dateid=date, machine="جرثقیل"),
                        Machinary(contractid=contract, dateid=date, machine="تراک میکسر"),
                        Machinary(contractid=contract, dateid=date, machine="تانکر آبپاش"),
                        Machinary(contractid=contract, dateid=date, machine="تراکتور"),
                        Machinary(contractid=contract, dateid=date, machine="پمپ بتن"),
                        Machinary(contractid=contract, dateid=date, machine="آمبولانس"),
                        Machinary(contractid=contract, dateid=date, machine="ماشین آتشنشانی"),
                        Machinary(contractid=contract, dateid=date, machine="لودر""مینی بوس و اتوبوس"),                        
                        Machinary(contractid=contract, dateid=date, machine="انواع سواری"),
                        Machinary(contractid=contract, dateid=date, machine="دستگاه بچینگ"),
                        Machinary(contractid=contract, dateid=date, machine="دستگاه بلوک زنی"),
                        Machinary(contractid=contract, dateid=date, machine="دستگاه جدول زنی"),
                        Machinary(contractid=contract, dateid=date, machine="تانکر سوخت آب"),
                        Machinary(contractid=contract, dateid=date, machine="چکش مکانیکی"),
                        Machinary(contractid=contract, dateid=date, machine="جمع کل", priority=1),
                    ])
                else: 
                    machineries = Machinary.objects.filter(contractid__exact=contractId, dateid__exact=last_date_id)
                    for machinery in machineries:
                        if(machinery.machine == "جمع کل"):
                            total_field_exist = True                            
                        Machinary.objects.create(contractid=contract, dateid=date, 
                                    machine=machinery.machine, activeno=machinery.activeno or 0, 
                                    inactiveno=machinery.inactiveno or 0, priority=1 if(machinery.machine == "جمع کل") else 0, 
                                    description=machinery.description or '')
                    
                    if(not total_field_exist):
                        total_field_exist = True    
                        Machinary.objects.create(contractid=contract, dateid=date, 
                                    machine="جمع کل", activeno=machinery.activeno or 0, 
                                    inactiveno=machinery.inactiveno or 0, priority=1,
                                    description=machinery.description or '')
            
            machineries = Machinary.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
           
            if(not total_field_exist):
                activeno = machineries.exclude(machine__exact="جمع کل").aggregate(Sum('activeno'))['activeno__sum']
                inactiveno = machineries.exclude(machine__exact="جمع کل").aggregate(Sum('inactiveno'))['inactiveno__sum']
                total_exist = True if machineries.filter(machine__exact="جمع کل").count() > 0 else False 
                if(not total_exist):
                    Machinary.objects.create(contractid=contract, dateid=date, 
                                            machine="جمع کل", activeno=activeno or 0, 
                                            inactiveno=inactiveno or 0, priority=1, description=machinery.description or '')
                else:
                    total = Machinary.objects.filter(contractid__exact=contractId, dateid__exact=dateId, machine__exact="جمع کل")[0]
                    total.activeno = activeno
                    total.inactiveno = inactiveno
                    total.save()
                    
            machineries = Machinary.objects.filter(contractid__exact=contractId, dateid__exact=dateId).order_by("priority", "machinaryid")     
            serializer = MachinerySerializer(instance=machineries, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the machinery for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])            
            
            machineries = Machinary.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = MachinerySerializer(instance=machineries, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProjectPersonalAPI(viewsets.ModelViewSet):
    """
    API for the ProjectPersonal model.
    """
    queryset = ProjectPersonnel.objects.all()
    serializer_class = ProjectPersonalSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the project personal for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
                        
            flg = 1	if ProjectPersonnel.objects.filter(contractid__exact=contractId, dateid__exact=dateId).count() > 0 else 0

            if flg == 0:
                contract = Contract.objects.get(pk=contractId)
                date = ReportDate.objects.get(pk=dateId)
                ProjectPersonnel.objects.update_or_create(contractid=contract ,dateid=date, 
                                                          defaults={'dpno':0 ,'dcpno':0 ,'mepno':0})
        
            projectPersonals = ProjectPersonnel.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('dateid')
            serializer = ProjectPersonalSerializer(instance=projectPersonals, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the project personal for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            projectPersonals = ProjectPersonnel.objects.filter(contractid__exact=contractId, dateid__lte=dateId).order_by('-dateid')[:9:-1]
            serializer = ProjectPersonalReportSerializer(instance=projectPersonals, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  

class ProblemAPI(viewsets.ModelViewSet):
    """
    API for the Problem model.
    """
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the problem for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)
            
            problems = Problem.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = ProblemSerializer(problems, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the problem for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            problems = Problem.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = ProblemSerializer(problems, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  
class CriticalActionAPI(viewsets.ModelViewSet):
    """
    API for the CriticalAction model.
    """
    queryset = CriticalAction.objects.all()
    serializer_class = CriticalActionSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """
        Get the critical action for the contract month.
        """
        try:
            data = request.data
            userId = int(data["userid"])
            contractId = int(data["contractid"])
            dateId = int(data["dateid"])
            reportId = int(data["reportid"])
            
            SetReportVisit(userId, contractId, dateId, reportId)            
            
            criticalActions = CriticalAction.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = CriticalActionSerializer(instance=criticalActions, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """
        Get the critical action for the contract month report.
        """
        try:
            contractId = int(kwargs["contractid"])
            dateId = int(kwargs["dateid"])
            
            criticalActions = CriticalAction.objects.filter(contractid__exact=contractId, dateid__exact=dateId)
            serializer = CriticalActionSerializer(instance=criticalActions, many=True)
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "data": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


