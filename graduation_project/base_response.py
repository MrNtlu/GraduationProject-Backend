from rest_framework.response import Response

def handleResponseMessage(status, message, data=None):
    response = {}

    response['status'] = status
    response['message'] = message
    response['data'] = data
        
    return Response(response)