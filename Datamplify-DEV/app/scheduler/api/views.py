from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from croniter import croniter
import pendulum

from app.scheduler.models import Scheduler
from .serializers import SchedulerSerializer
from app.scheduler.services.publish import publish_scheduler

class SchedulerViewSet(viewsets.ModelViewSet):
    queryset = Scheduler.objects.all().order_by("-id")
    serializer_class = SchedulerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        flowboard = self.request.query_params.get("flowboard")
        if flowboard:
            qs = qs.filter(flowboard_id=flowboard)
        return qs

    def perform_create(self, serializer):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("SchedulerViewSet.perform_create called")
        obj = serializer.save()
        logger.info(f"Scheduler saved with ID: {obj.id}, calling publish_scheduler")
        try:
            result = publish_scheduler(obj)
            logger.info(f"publish_scheduler returned: {result}")
        except Exception as e:
            logger.error(f"publish_scheduler failed: {str(e)}")
            raise

    def perform_update(self, serializer):
        import logging
        logger = logging.getLogger(__name__)
        logger.info("SchedulerViewSet.perform_update called")
        obj = serializer.save()
        logger.info(f"Scheduler updated with ID: {obj.id}, calling publish_scheduler")
        try:
            result = publish_scheduler(obj)
            logger.info(f"publish_scheduler returned: {result}")
        except Exception as e:
            logger.error(f"publish_scheduler failed: {str(e)}")
            raise

    def create(self, request, *args, **kwargs):
        data = request.data
        if data.get("schedule"):
            s = data["schedule"]
            if not (s.startswith("@") or croniter.is_valid(s)):
                return Response({"error": "Invalid cron/preset"}, status=400)

        tz = data.get("timezone") or "Asia/Kolkata"
        if data.get("start_date"):
            start = pendulum.parse(data["start_date"]).in_timezone(tz)
            if start > pendulum.now(tz):
                data["start_date"] = pendulum.now(tz).subtract(minutes=1).to_iso8601_string()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
