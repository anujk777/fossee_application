from io import BytesIO
import pandas as pd
from django.contrib.auth import authenticate
from django.http import FileResponse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import UploadRecord
from .serializers import UploadRecordSerializer
from .services import (
    build_chart_buffers,
    build_pdf_report,
    compute_summary,
    validate_columns,
)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'username': user.username})


@api_view(['POST'])
def upload_csv(request):
    csv_file = request.FILES.get('file')
    if not csv_file:
        return Response({'detail': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

    df = pd.read_csv(csv_file)
    missing_cols = validate_columns(df)
    if missing_cols:
        return Response({'detail': f'Missing columns: {missing_cols}'}, status=status.HTTP_400_BAD_REQUEST)

    summary = compute_summary(df)
    UploadRecord.objects.create(file_name=csv_file.name, summary=summary)

    stale_records = UploadRecord.objects.all()[5:]
    if stale_records:
        UploadRecord.objects.filter(id__in=[r.id for r in stale_records]).delete()

    return Response({'file_name': csv_file.name, 'summary': summary}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def summary(request):
    latest = UploadRecord.objects.first()
    if not latest:
        return Response({'detail': 'No uploads available.'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'file_name': latest.file_name, 'summary': latest.summary})


@api_view(['GET'])
def history(request):
    records = UploadRecord.objects.all()[:5]
    serializer = UploadRecordSerializer(records, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def report_pdf(request):
    latest = UploadRecord.objects.first()
    if not latest:
        return Response({'detail': 'No uploads available.'}, status=status.HTTP_404_NOT_FOUND)

    file_name = request.query_params.get('file_name', latest.file_name)

    try:
        selected = UploadRecord.objects.get(file_name=file_name)
    except UploadRecord.DoesNotExist:
        selected = latest

    # Recreate demo dataframe from summary is not possible; use latest upload by requiring re-upload via API.
    # For report generation we build a minimal dataframe from latest summary when historical data is unavailable.
    sample = pd.DataFrame(
        {
            'Session ID': ['S1'],
            'Board Type': ['Freeride'],
            'Wind Speed (km/h)': [selected.summary['average_wind_speed']],
            'Distance Covered (km)': [selected.summary['average_distance_covered']],
        }
    )
    chart_buffers = build_chart_buffers(
        sample.rename(columns={'Board Type': 'Board Type'})
    )
    pdf_buffer = BytesIO()
    build_pdf_report(pdf_buffer, selected.summary, selected.file_name, chart_buffers)

    return FileResponse(pdf_buffer, as_attachment=True, filename='windsurf_report.pdf')
