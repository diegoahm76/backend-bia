from rest_framework.views import exception_handler

def api_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        # Using the description's of the HTTPStatus class as error message.
        
        error_message = ""
        
        try:
            if isinstance(response.data, dict):
                for key, value in response.data.items():
                    if isinstance(value, list):
                        separator = ', ' if key != list(response.data)[-1] else ''
                        for i in range(len(value)):
                            value[i] = 'El campo es requerido' if value[i] == 'This field is required.' else value[i]
                        error_message += key + ': ' + ' '.join(value) + separator
                    else:
                        error_message += value
            elif isinstance(response.data, list):
                dict_list = {k: v for d in response.data for k, v in d.items()}
                dict_list_vls = [k for k, v in dict_list.items()]
                dict_list_msg = [v for k, v in dict_list.items()]
                error_message_dict = dict(zip(dict_list_vls, dict_list_msg))
                for index, (key, value) in enumerate(error_message_dict.items()):
                    key = 'Error' if key == 'non_field_errors' else key
                    for i in range(len(value)):
                        value[i] = 'El campo es requerido' if value[i] == 'This field is required.' else value[i]
                    
                    separator = ', '
                    if index == len(error_message_dict)-1:
                        separator = ''
                        
                    error_message += key + ': ' + ', '.join(value) + separator
            else:
                error_message = response.data
        except:
            error_message = response.data
        
        #error_message = response.data
        
        error_payload = {
            "success": False,
            "detail": error_message,
        }
        
        response.data = error_payload
    return response