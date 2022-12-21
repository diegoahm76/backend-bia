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
                        key = 'Error' if key == 'non_field_errors' else key
                        for i in range(len(value)):
                            value[i] = 'El campo es requerido' if value[i] == 'This field is required.' else value[i]
                            value[i] = 'El campo debe ser único' if value[i] == 'This field must be unique.' else value[i]
                            value[i] = 'El campo no debe ser vacío' if value[i] == 'This field may not be blank.' else value[i]
                            value[i] = 'No es una opción válida' if 'is not a valid choice.' in value[i] else value[i]
                            value[i] = 'El valor ingresado no existe' if 'object does not exist.' in value[i] else value[i]
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
                        value[i] = 'El campo debe ser único' if value[i] == 'This field must be unique.' else value[i]
                        value[i] = 'El campo no debe ser vacío' if value[i] == 'This field may not be blank.' else value[i]
                        value[i] = 'No es una opción válida' if 'is not a valid choice.' in value[i] else value[i]
                        value[i] = 'El valor ingresado no existe' if 'object does not exist.' in value[i] else value[i]
                    
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