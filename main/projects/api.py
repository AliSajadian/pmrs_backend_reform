"""
API views for the projects application.
All business logic has been moved to service.py.
"""
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action

from projects.models import (
    ReportDate, ReportConfirm, FinancialInfo, Hse, ProgressState,
    TimeprogressState, Invoice, FinancialInvoice, WorkVolume, 
    PmsProgress, Budgetcost, Problem, CriticalAction, 
    Machinary, ProjectPersonnel
)
from .serializers import (
    ReportDateSerializerEx, ReportConfirmSerializer, ReportsConfirmedSerializer,
    ProjectManagerReportConfirmSerializer, CoordinatorReportConfirmSerializer, 
    FinancialInfoSerializer, FinancialInfoReportSerializer, HseSerializer, 
    ProgressStateSerializer, TimeProgressStateSerializer, InvoiceSerializer, 
    FinancialInvoiceSerializer, WorkvolumeSerializer, PmsprogressSerializer,
    BudgetCostSerializer, MachinerySerializer, ProjectPersonalSerializer, 
    ProblemSerializer, CriticalActionSerializer, HseReportSerializer, 
    ProgressStateReportSerializer, InvoiceReport1Serializer, 
    InvoiceReport2Serializer, FinancialInvoiceReportSerializer,
    BudgetCostReportSerializer, ProjectPersonalReportSerializer
)
from .services import (
    ReportDateService, ReportConfirmService, FinancialInfoService,
    HseService, ProgressStateService, TimeProgressStateService,
    InvoiceService, FinancialInvoiceService, WorkVolumeService,
    PmsProgressService, BudgetCostService, MachineryService,
    ProjectPersonnelService, ProblemService, CriticalActionService
)


class ReportDateAPIEx(APIView):
    """API for the ReportDate model."""
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, *args, **kwargs):
        """
        Get report dates. Automatically creates records for missing months.
        """
        report_dates = ReportDateService.get_and_create_report_dates()
        serializer = ReportDateSerializerEx(report_dates, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class ReportConfirmAPI(viewsets.ModelViewSet):
    """API for the ReportConfirm model."""
    
    queryset = ReportConfirm.objects.all()
    serializer_class = ReportConfirmSerializer
    # permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])   
    def getConfirmedReports(self, *args, **kwargs):
        """Get the confirmed reports."""
        contract_id = int(kwargs["contract_id"])
        date_id = int(kwargs["date_id"])
        
        objects = ReportConfirmService.get_confirmed_reports(contract_id, date_id)
        serializer = ReportsConfirmedSerializer(instance=objects, many=True)
        
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])   
    def isProjectManagerConfirmedReport(self, request, *args, **kwargs):
        """Check if the project manager has confirmed the report."""
        data = request.data
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        
        obj = ReportConfirmService.is_project_manager_confirmed(contract_id, date_id)
        
        serializer = ProjectManagerReportConfirmSerializer(
            instance=obj, many=False
        ) if obj is not None else {"pm_c": "0", "pmconfirmdate": ""}
        
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )
        
    @action(detail=False, methods=['post'])   
    def projectManagerReportConfirm(self, request, *args, **kwargs):
        """Confirm the project manager report."""
        data = request.data
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        confirmed = int(data["confirmed"])

        result = ReportConfirmService.project_manager_confirm(
            contract_id, date_id, confirmed
        )
        
        if result is not None:
            serializer = ReportsConfirmedSerializer(instance=result, many=True)
            return Response(
                {"status": "success", "data": serializer.data}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"status": "error", "data": "Err:01"}, 
                status=status.HTTP_200_OK
            )

    @action(detail=False, methods=['post'])   
    def isCoordinatorConfirmedReport(self, request, *args, **kwargs):
        """Check if the coordinator has confirmed the report."""
        data = request.data
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_type = int(data["type"])
        
        obj = ReportConfirmService.is_coordinator_confirmed(
            contract_id, date_id, report_type
        )
        
        default_data = {
            "userconfirmer": "", 
            "user_c": "0", 
            "userconfirmdate": ""
        }
        serializer = CoordinatorReportConfirmSerializer(
            instance=obj, many=False
        ) if obj is not None else default_data
        
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])   
    def coordinatorReportConfirm(self, request, *args, **kwargs):
        """Confirm the coordinator report."""
        data = request.data
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        user_id = int(data["userid"])
        confirmed = int(data["confirmed"])
        report_type = int(data["type"])
        
        result = ReportConfirmService.coordinator_confirm(
            contract_id, date_id, user_id, confirmed, report_type
        )
        
        serializer = ReportsConfirmedSerializer(instance=result, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class FinancialInfoAPI(viewsets.ModelViewSet):
    """API for the FinancialInfo model."""
    
    queryset = FinancialInfo.objects.all()
    serializer_class = FinancialInfoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the financial info for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        financial_info = FinancialInfoService.get_or_create_financial_info(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = FinancialInfoSerializer(instance=financial_info, many=False)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the financial info for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        financial_info = FinancialInfoService.get_financial_info_for_report(
            contract_id, date_id
        )
        
        serializer = FinancialInfoReportSerializer(
            instance=financial_info, many=False
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def updateFinancialInfo(self, request, *args, **kwargs):
        """Update the financial info."""
        financial_info_id = int(kwargs["financialInfoId"])
        data = request.data
        
        # Convert all data to integers
        for key in data:
            if key not in ["contractid", "dateid"] and isinstance(data[key], str):
                data[key] = int(data[key])
        
        financial_info = FinancialInfoService.update_financial_info(
            financial_info_id, data
        )
        
        serializer = FinancialInfoSerializer(instance=financial_info, many=False)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class HseAPI(viewsets.ModelViewSet):
    """API for the Hse model."""
    
    queryset = Hse.objects.all()
    serializer_class = HseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the HSE for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        hse = HseService.get_or_create_hse(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = HseSerializer(instance=hse, many=False)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the HSE for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        hse = HseService.get_hse_for_report(contract_id, date_id)
        
        serializer = HseReportSerializer(instance=hse, many=False)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class ProgressStateAPI(viewsets.ModelViewSet):
    """API for the ProgressState model."""
    
    queryset = ProgressState.objects.all()
    serializer_class = ProgressStateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the progress state for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        progress_states = ProgressStateService.get_or_create_progress_state(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = ProgressStateSerializer(instance=progress_states, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the progress state for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        progress_states = ProgressStateService.get_progress_state_for_report(
            contract_id, date_id
        )
        
        serializer = ProgressStateReportSerializer(
            instance=progress_states, many=True
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class TimeProgressStateAPI(viewsets.ModelViewSet):
    """API for the TimeProgressState model."""
    
    queryset = TimeprogressState.objects.all()
    serializer_class = TimeProgressStateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the time progress state for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        time_progress_states = TimeProgressStateService.get_or_create_time_progress_state(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = TimeProgressStateSerializer(
            instance=time_progress_states, many=True
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class InvoiceAPI(viewsets.ModelViewSet):
    """API for the Invoice model."""
    
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the invoice for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        invoices = InvoiceService.get_or_create_invoices(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = InvoiceSerializer(data=invoices, many=True)
        serializer.is_valid()
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def contractMonthReportList1(self, request, *args, **kwargs):
        """Get the invoice for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        invoice = InvoiceService.get_invoice_for_report_1(contract_id, date_id)
        
        serializer = InvoiceReport1Serializer(instance=invoice, many=False)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList2(self, request, *args, **kwargs):
        """Get the invoice for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        invoices = InvoiceService.get_invoice_for_report_2(contract_id, date_id)
        
        serializer = InvoiceReport2Serializer(instance=invoices, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class FinancialInvoiceAPI(viewsets.ModelViewSet):
    """API for the FinancialInvoice model."""
    
    queryset = FinancialInvoice.objects.all()
    serializer_class = FinancialInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the financial invoice for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        financial_invoices = FinancialInvoiceService.get_or_create_financial_invoices(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = FinancialInvoiceSerializer(
            data=financial_invoices, many=True
        )
        serializer.is_valid()
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the financial invoice for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        invoices = FinancialInvoiceService.get_financial_invoices_for_report(
            contract_id, date_id
        )
        
        serializer = FinancialInvoiceReportSerializer(
            instance=invoices, many=True
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class WorkVolumeAPI(viewsets.ModelViewSet):
    """API for the WorkVolume model."""
    
    queryset = WorkVolume.objects.all()
    serializer_class = WorkvolumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the work volume for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        work_volumes = WorkVolumeService.get_or_create_work_volumes(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = WorkvolumeSerializer(instance=work_volumes, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, request, *args, **kwargs):
        """Get the work volume for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        work_volumes = WorkVolumeService.get_work_volumes_for_report(
            contract_id, date_id
        )
        
        serializer = WorkvolumeSerializer(instance=work_volumes, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class PmsprogressAPI(viewsets.ModelViewSet):
    """API for the PmsProgress model."""
    
    queryset = PmsProgress.objects.all()
    serializer_class = PmsprogressSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the PMS progress for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        pms_progresses = PmsProgressService.get_or_create_pms_progress(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = PmsprogressSerializer(instance=pms_progresses, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the PMS progress for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        pms_progresses = PmsProgressService.get_pms_progress_for_report(
            contract_id, date_id
        )
        
        serializer = PmsprogressSerializer(instance=pms_progresses, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class BudgetCostAPI(viewsets.ModelViewSet):
    """API for the BudgetCost model."""
    
    queryset = Budgetcost.objects.all()
    serializer_class = BudgetCostSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the budget cost for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        budget_costs = BudgetCostService.get_or_create_budget_cost(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = BudgetCostSerializer(instance=budget_costs, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['put'])
    def setAdminDescription(self, request, *args, **kwargs):
        """Set the admin description for the budget cost."""
        data = request.data
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        description = str(data["description"])
        
        BudgetCostService.set_admin_description(
            contract_id, date_id, description
        )
        
        return Response({"status": "success"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the budget cost for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        budget_costs = BudgetCostService.get_budget_cost_for_report(
            contract_id, date_id
        )
        
        serializer = BudgetCostReportSerializer(
            instance=budget_costs, many=True
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class MachineryAPI(viewsets.ModelViewSet):
    """API for the Machinery model."""
    
    queryset = Machinary.objects.all()
    serializer_class = MachinerySerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the machinery for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        machineries = MachineryService.get_or_create_machinery(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = MachinerySerializer(instance=machineries, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the machinery for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        machineries = MachineryService.get_machinery_for_report(
            contract_id, date_id
        )
        
        serializer = MachinerySerializer(instance=machineries, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class ProjectPersonalAPI(viewsets.ModelViewSet):
    """API for the ProjectPersonal model."""
    
    queryset = ProjectPersonnel.objects.all()
    serializer_class = ProjectPersonalSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the project personnel for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        project_personnel = ProjectPersonnelService.get_or_create_project_personnel(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = ProjectPersonalSerializer(
            instance=project_personnel, many=True
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the project personnel for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        project_personnel = ProjectPersonnelService.get_project_personnel_for_report(
            contract_id, date_id
        )
        
        serializer = ProjectPersonalReportSerializer(
            instance=project_personnel, many=True
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class ProblemAPI(viewsets.ModelViewSet):
    """API for the Problem model."""
    
    queryset = Problem.objects.all()
    serializer_class = ProblemSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the problems for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        problems = ProblemService.get_problems(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = ProblemSerializer(problems, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the problems for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        problems = ProblemService.get_problems_for_report(
            contract_id, date_id
        )
        
        serializer = ProblemSerializer(problems, many=True)
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )


class CriticalActionAPI(viewsets.ModelViewSet):
    """API for the CriticalAction model."""
    
    queryset = CriticalAction.objects.all()
    serializer_class = CriticalActionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def contractMonthList(self, request, *args, **kwargs):
        """Get the critical actions for the contract month."""
        data = request.data
        user_id = int(data["userid"])
        contract_id = int(data["contractid"])
        date_id = int(data["dateid"])
        report_id = int(data["reportid"])
        
        critical_actions = CriticalActionService.get_critical_actions(
            user_id, contract_id, date_id, report_id
        )
        
        serializer = CriticalActionSerializer(
            instance=critical_actions, many=True
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def contractMonthReportList(self, *args, **kwargs):
        """Get the critical actions for the contract month report."""
        contract_id = int(kwargs["contractid"])
        date_id = int(kwargs["dateid"])
        
        critical_actions = CriticalActionService.get_critical_actions_for_report(
            contract_id, date_id
        )
        
        serializer = CriticalActionSerializer(
            instance=critical_actions, many=True
        )
        return Response(
            {"status": "success", "data": serializer.data}, 
            status=status.HTTP_200_OK
        )
