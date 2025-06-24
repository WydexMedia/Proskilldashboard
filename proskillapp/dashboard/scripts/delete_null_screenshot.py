from dashboard.models import OgaRequest
OgaRequest.objects.filter(screenshot__isnull=True).delete()
print('Deleted all OgaRequest rows with null screenshot.')
