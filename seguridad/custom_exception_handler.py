from rest_framework.views import exception_handler

def api_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        
        # error_message = ""
        
        # try:
        #     if isinstance(response.data, dict):
        #         for key, value in response.data.items():
        #             if isinstance(value, list):
        #                 separator = ' ' if key != list(response.data)[-1] else ''
        #                 error_message += key + ': ' + ' '.join(value) + separator
        #             else:
        #                 error_message += value
        #     elif isinstance(response.data, list):
        #         dict_list = {k: v for d in response.data for k, v in d.items()}
        #         dict_list_msg = [v for k, v in dict_list.items()]
        #         error_message = ', '.join(dict_list_msg[0])
        #     else:
        #         error_message = response.data
        # except:
        #     error_message = response.data
        
        error_message = response.data
        
        error_payload = {
            "success": False,
            "detail": error_message,
        }
        
        response.data = error_payload
    return response