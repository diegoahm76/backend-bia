import os
import requests
from rest_framework.exceptions import ValidationError


class UtilsTransversal:

    @staticmethod
    def get_token_camunda(token):
        auth_headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        #TOKEN PARA SASOFTCO
        url_login_token = f"{os.environ.get('URL_SASOFTCO')}/api/Authentication/login-token-bia"
        payload={
            "access": token
        }

        try:
            response = requests.post(url_login_token,json=payload,headers=auth_headers)
            response.raise_for_status()
            data = response.json()

            if 'userinfo' in data:
                if 'userinfo' in data['userinfo']:
                    info = data['userinfo']['userinfo']
                    token = info['tokens']['access']
                    return token
            return None
        except requests.RequestException as e:
            raise ValidationError(f"Error en la solicitud: {e}")
    
    @staticmethod
    def create_grupo_funcional_camunda(token, grupos):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        url = f"{os.environ.get('URL_SASOFTCO')}/api/functional-groups"
  
        try:
            response = requests.post(url, json=grupos, headers=headers)
            response.raise_for_status()  # Si hay un error en la solicitud, generará una excepción
            
            if response.status_code == 200:
                return True
            else:
                raise ValidationError('Ocurrió un error al crear el grupo en el sistema de Camunda, comuniquese con un administrador')
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")
            raise ValidationError('Ocurrió un error al crear el grupo en el sistema de Camunda, comuniquese con un administrador')
    
    @staticmethod
    def delete_grupo_funcional_camunda(token, id_grupo):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        url = f'https://backendclerkapi.sedeselectronicas.com/api/functional-groups/{id_grupo}' 
  
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()  # Si hay un error en la solicitud, generará una excepción
            
            if response.status_code == 200:
                return True
            else:
                raise ValidationError('Ocurrió un error al crear el grupo en el sistema de Camunda, comuniquese con un administrador')
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")
            raise ValidationError('Ocurrió un error al crear el grupo en el sistema de Camunda, comuniquese con un administrador')
    
    @staticmethod
    def update_grupo_funcional_camunda(token, id_grupo, grupo):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        url = f'https://backendclerkapi.sedeselectronicas.com/api/functional-groups/{id_grupo}' 
  
        try:
            response = requests.put(url, json=grupo, headers=headers)
            response.raise_for_status()  # Si hay un error en la solicitud, generará una excepción
            data = response.json()  # Convertimos los datos a JSON
            
            if response.status_code == 200:
                return data
            else:
                raise ValidationError('Ocurrió un error al crear el grupo en el sistema de Camunda, comuniquese con un administrador')
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")
            raise ValidationError('Ocurrió un error al crear el grupo en el sistema de Camunda, comuniquese con un administrador')
    
    @staticmethod
    def get_grupo_funcional_camunda(token):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        url = f"{os.environ.get('URL_SASOFTCO')}/api/functional-groups"
  
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Si hay un error en la solicitud, generará una excepción
            data = response.json()
            
            if response.status_code == 200:
                return data
            else:
                raise ValidationError('Ocurrió un error al crear el grupo en el sistema de Camunda, comuniquese con un administrador')
        except requests.RequestException as e:
            print(f"Error en la solicitud: {e}")
            raise ValidationError('Ocurrió un error al crear el grupo en el sistema de Camunda, comuniquese con un administrador')
