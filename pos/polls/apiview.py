from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from polls.permission import IsAdminRole,IsUserOrAdmin

class AdminOnlyView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]
    
    def get(self, request):
        # All users can see this
        return Response({"message": "This is visible to all authenticated users"})
    
    def post(self, request):
        # Only superusers can post here
        return Response({"message": "This action requires superuser status"})
    
class StaffUserView(APIView):
    permission_classes = [IsUserOrAdmin]  # Only staff members can access

    def get(self, request):
        return Response({"message": "Hello User member!"})