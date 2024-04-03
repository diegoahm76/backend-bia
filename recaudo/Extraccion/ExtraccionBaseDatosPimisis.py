import psycopg2
import pyodbc
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()


def consultar_tabla_mssql():
    try: 
        # Intentar establecer la conexión MS SQL Server
        conn_mssql = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=200.10.29.112;'
            'DATABASE=PIMISYS;'
            'UID=HGUTIERREZV;'
            'PWD=CORMA123**;'
        )
        print("Conexión MS SQL Server exitosa!")

        cursor = conn_mssql.cursor()

        # Consultar los datos de la tabla T970TRAMITE
        select_query_970 = """
            SELECT 
                T970CodCia,
                T970IdTramite,
                T970Agno,
                T970CodTipoTramite,
                T970CodExpediente,
                T970CodDepen,
                T970NumRadicadoEntrada,
                T970FechaRadicadoEntrada,
                T970Descripcion,
                T970IdTramiteRef,
                T970Observacion,
                T970CodEstadoTram,
                T970TUAFECHAINIPERM,
                T970TUAMESESPLAZO,
                T970TUAFECHAFINPERM,
                T970NUMRESOLPERM,
                T970FECHARESPERM,
                T970TUACAUDALCONCESI,
                T970TUAPREDIO,
                T970VERIFICO_FUN,
                T970TRGEMAORIGEN,
                T970GEMATIPOINFRACCI,
                T970GEMATIPOINFRADES
            FROM 
                T970TRAMITE
        """
        cursor.execute(select_query_970)
        column_data_970 = cursor.fetchall()

        select_query_987 = """
            SELECT 
                T987CodCia,
                T987NumTR,
                T987Consecutivo,
                T987CodTipoFuenteHid,
                T987CodFuenteHid,
                T987CodTramo,
                T987CaudalCaptado,
                T987AguaEnBloque,
                T987ConsumoAcueducto,
                T987CodUbicacion
            FROM 
                T987TRVERTIMIENTO
        """
        cursor.execute(select_query_987)
        column_data_987 = cursor.fetchall()

        
        select_query_986 = """
            SELECT 
                T986CodCia,
                T986NumTR,
                T986CodActividadCIIU,
                T986Descripcion
                
            FROM 
                T986TRACTIVIDAD
        """
        cursor.execute(select_query_986)
        select_query_986 = cursor.fetchall()


   # Consultar los datos de la tabla T985TR
        select_query_985 = """
            SELECT 
                T985CodCia,
                T985NumTR,
                T985Agno,
                T985Periodo,
                T985NumFormulario,
                T985CodTipoDeclaracion,
                T985Aprobada,
                T985FechaDiligenciamiento,
                T985Fecha,
                T985NumRadicadoEntrada,
                T985FechaRadicadoEntrada,
                T985Nit,
                T985CodDpto,
                T985CodMpio,
                T985CodPostal,
                T985Direccion,
                T985Telefono,
                T985CodTipoUsuario,
                T985NitRepLegal,
                T985CodUbicacion,
                T985IdCobro,
                T985Anulado,
                T985Observacion,
                T985NitElaboro,
                T985CargoElaboro,
                T985LugarElaboro,
                T985NumFicha,
                T985NumMatricula,
                T985GeoUbicacion,
                T985IdTramite
            FROM 
                T985TR
        """
        cursor.execute(select_query_985)
        column_data_985 = cursor.fetchall()



   # Consultar los datos de la tabla T982TUACAPTACION
        select_query_982 = """
        SELECT 
        T982CodCia,
        T982NumTUA,
        T982Consecutivo,
        T982CodTipoFuenteHid,
        T982CodClaseUsoAgua,
        T982CodFuenteHid,
        T982CodTramo,
        T982CodDpto,
        T982CodMpio,
        T982FactorRegional
    FROM 
        T982TUACAPTACION
        """
        cursor.execute(select_query_982)
        column_data_982 = cursor.fetchall()


        # Consultar los datos de la tabla T982TUACAPTACION
        select_query_981 = """
        SELECT 
        T981CodCia,
        T981NumTUA,
        T981CodActividadCIIU,
        T981Descripcion

    FROM 
        T981TUAACTIVIDAD
        """
        cursor.execute(select_query_981)
        column_data_981 = cursor.fetchall()



        # Consultar los datos de la tabla T980TUA
        select_query_980 = """
        SELECT 
        T980CodCia,
        T980NumTUA,
        T980Agno,
        T980Periodo,
        T980NumFormulario,
        T980CodTipoDeclaracion,
        T980Aprobada,
        T980FechaDiligenciamiento,
        T980Fecha,
        T980NumRadicadoEntrada,
        T980FechaRadicadoEntrada,
        T980Nit,
        T980CodDpto,
        T980CodMpio,
        T980CodPostal,
        T980Direccion,
        T980Telefono,
        T980CodTipoUsuario,
        T980NitRepLegal,
        T980CodUbicacion,
        T980IdCobro,
        T980Anulado,
        T980Observacion,
        T980IdTramite

    FROM 
        T980TUA
        """
        cursor.execute(select_query_980)
        column_data_980 = cursor.fetchall()


        # Consultar los datos de la tabla T956FUENTEHID
        select_query_956 = """
        SELECT 
        T956CodCia,
        T956CodFuenteHid,
        T956Nombre,
        T956Observacion,
        T956GeoUbicacion,
        T956AreaCuenca,
        T956LongitudCauce,
        T956Movimiento

    FROM
        T956FUENTEHID
        """
        cursor.execute(select_query_956)
        column_data_956 = cursor.fetchall()


        # Consultar los datos de la tabla T904RENTACTABANCO
        select_query_904 = """
        SELECT 
        T904CodCia,
        T904CodTipoRenta,
        T904CodCtaBanco 
        

    FROM
        T904RENTACTABANCO 
        """
        cursor.execute(select_query_904)
        column_data_904 = cursor.fetchall()
        

    # Consultar los datos de la tabla T914DISTRIBUCION
        select_query_914 = """
        SELECT 
        T914CodCia,
        T914CodTipoRenta,
        T914NumDistribucion,
        T914Agno,
        T914CodTipoDoc,
        T914NumeroDoc,
        T914CodCtaBanco,
        T914CodGrupoRec,
        T914Fecha,
        T914NumOrigen,
        T914CodOrigen,
        T914AbonarLiq,
        T914Anulado,
        T914NumeroDocRnt
        

    FROM
        T914DISTRIBUCION  
        """
        cursor.execute(select_query_914)
        column_data_914 = cursor.fetchall()
        

         # Consultar los datos de la tabla T914DISTRIBUCION
        select_query_913 = """
        SELECT 
        T913CodCia,
        T913CodTipoRenta,
        T913NumRecaudo,
        T913Agno,
        T913CodTipoDoc,
        T913CodCtaBanco,
        T913CodGrupoRec,
        T913Nit,
        T913Fecha,
        T913FechaReal,
        T913Valor,
        T913TipoDistribucion,
        T913CodTipoFormulario,
        T913NumFormulario,
        T913NumFormularioPago,
        T913Anulado,
        T913NumAnulacion,
        T913CodFormaPago,
        T913NumDocPago

    FROM
        T913RECAUDO  
        """
        cursor.execute(select_query_913)
        column_data_913 = cursor.fetchall()

        # Consultar los datos de la tabla T915DISTRIBUCIONLIQ 
        select_query_915 = """
        SELECT 
        T915CodCia,
        T915CodTipoRenta,
        T915NumDistribucion,
        T915NumLiquidacion,
        T915CodConcepto,
        T915ValorPagado,
        T915ValorPrescripcion,
        T915ValorPagadoDet 
        

    FROM
        T915DISTRIBUCIONLIQ   
        """
        cursor.execute(select_query_915)
        column_data_915 = cursor.fetchall()


        # Consultar los datos de la tabla T915DISTRIBUCIONLIQ 
        select_query_916 = """
        SELECT 
        T916CodCia,
        T916CodTipoRenta,
        T916NumDistribucion,
        T916NumLiquidacion,
        T916NumCuota,
        T916ValorCapital,
        T916ValorInteres,
        T916FechaIniInt,
        T916ValorInt1066,
        T916ValorPrescripcion
     
        

    FROM
        T916DISTRIBUCIONCUOT    
        """
        cursor.execute(select_query_916)
        column_data_916 = cursor.fetchall()
        


        # Mostrar los datos obtenidos
        # print("Datos obtenidos de la tabla T970TRAMITE en MS SQL Server:")
        # for row in column_data_970:
        #     print(row)

        # print("Datos obtenidos de la tabla T987TRVERTIMIENTO en MS SQL Server:")
        # for row in column_data_987:
        #     print(row)

        # print("Datos obtenidos de la tabla T986TRACTIVIDAD en MS SQL Server:")
        # for row in select_query_986:
        #     print(row)
   
        # print("Datos obtenidos de la tabla T985TR en MS SQL Server:")
        # for row in column_data_985:
        #     print(row)

        # print("Datos obtenidos de la tabla T982TUACAPTACION en MS SQL Server:")
        # for row in column_data_982:
        #     print(row)
        
        # print("Datos obtenidos de la tabla T981TUAACTIVIDAD en MS SQL Server:")
        # for row in column_data_981:
        #     print(row)

        # print("Datos obtenidos de la tabla T980TUA en MS SQL Server:")
        # for row in column_data_980:
        #     print(row)

        # print("Datos obtenidos de la tabla T980TUA en MS SQL Server:")
        # for row in column_data_956:
        #     print(row)

        # print("Datos obtenidos de la tabla T904RENTACTABANCO  en MS SQL Server:")
        # for row in column_data_904:
        #     print(row)

        # print("Datos obtenidos de la tabla T914DISTRIBUCION  en MS SQL Server:")
        # for row in column_data_914:
        #     print(row)

        # print("Datos obtenidos de la tabla t913recaudo   en MS SQL Server:")
        # for row in column_data_913:
        #     print(row)

        # print("Datos obtenidos de la tabla T915DISTRIBUCIONLIQ   en MS SQL Server:")
        # for row in column_data_915:
        #     print(row)

        print("Datos obtenidos de la tabla T916DISTRIBUCIONCUOT    en MS SQL Server:")
        for row in column_data_916:
            print(row)



        # Cerrar la conexión a MS SQL Server
        conn_mssql.close()

        # Retornar los datos obtenidos
        return column_data_970, column_data_987, select_query_986 ,column_data_985,column_data_982,column_data_981,column_data_980,column_data_956,column_data_904,column_data_914,column_data_913,column_data_915,column_data_916

    except Exception as e:
        # Manejar errores de conexión
        print("Error de conexión MS SQL Server:", e)
        return None, None, None
    



def insertar_datos_postgresql(data_970, data_987, data_986, data_985 , data_982 ,data_981 ,data_980,data_956,data_904,data_914,data_913,data_915,data_916):
    try:
        # Intentar establecer la conexión PostgreSQL
        conn_postgresql = psycopg2.connect(
            host=os.environ['BIA_DB_HOST'], 
            port=os.environ['BIA_DB_PORT'],
            database=os.environ['BIA_DB_PASSWORD'], 
            user=os.environ['BIA_DB_USER'],
            password=os.environ['BIA_DB_PASSWORD']
        )
        print("Conexión PostgreSQL exitosa!")

        cursor = conn_postgresql.cursor()


        # # Eliminar datos existentes de las tablas
        #cursor.execute("DELETE FROM rt970tramite")
        # cursor.execute("DELETE FROM rt987trvertimiento")
        # cursor.execute("DELETE FROM rt986tractividad")
        # cursor.execute("DELETE FROM rt985tr")
        # cursor.execute("DELETE FROM rt982tuacaptacion")
        # cursor.execute("DELETE FROM rt981tuaactividad")
        # cursor.execute("DELETE FROM rt980tua")
        # cursor.execute("DELETE FROM rt956fuentehid")
        # cursor.execute("DELETE FROM rt904rentactabanco")
        # cursor.execute("DELETE FROM rt914distribucion")
        # cursor.execute("DELETE FROM rt913recaudo")
        # cursor.execute("DELETE FROM rt915distribucionliq")
        # cursor.execute("DELETE FROM rt916distribucioncuot")




        # Instrucción SQL de inserción para la tabla T970TRAMITE
        insert_query_970 = """
            INSERT INTO rt970tramite (
                t970codcia,
                t970idtramite,
                t970agno,
                t970codtipotramite,
                t970codexpediente,
                t970coddepen,
                t970numradicadoentrada,
                t970fecharadicadoentrada,
                t970descripcion,
                t970idtramiteref,
                t970observacion,
                t970codestadotram,
                t970tuafechainiperm,
                t970tuamesesplazo,
                t970tuafechafinperm,
                t970numresolperm,
                t970fecharesperm,
                t970tuacaudalconcesi,
                t970tuapredio,
                t970verifico_fun,
                t970trgemaorigen,
                t970gematipoinfracci,
                t970gematipoinfrades
            ) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        # # Insertar cada dato en la tabla T970TRAMITE
        # for dato_970 in data_970:
        #     dato_970 = tuple(None if val is None else val for val in dato_970)
        #     cursor.execute(insert_query_970, dato_970)

        # Instrucción SQL de inserción para la tabla T987TRVERTIMIENTO
        insert_query_987 = """
            INSERT INTO rt987trvertimiento (
                t987codcia,
                t987numtr,
                t987consecutivo,
                t987codtipofuentehid,
                t987codfuentehid,
                t987codtramo,
                t987caudalcaptado,
                t987aguaenbloque,
                t987consumoacueducto,
                t987codubicacion
            ) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        # # Insertar cada dato en la tabla T987TRVERTIMIENTO
        # for dato_987 in data_987:
        #     dato_987 = tuple(None if val is None else val for val in dato_987)
        #     cursor.execute(insert_query_987, dato_987)

        # Instrucción SQL de inserción para la tabla T986TRACTIVIDAD
        insert_query_986 = """
            INSERT INTO rt986tractividad (
                t986codcia,
                t986numtr,
                t986codactividadciiu,
                t986descripcion
            ) 
            VALUES (%s,%s,%s,%s)
        """
        # #Insertar cada dato en la tabla T986TRACTIVIDAD
        # for dato_986 in data_986:
        #     dato_986 = tuple(None if val is None else val for val in dato_986)
        #     cursor.execute(insert_query_986, dato_986)



        insert_query_985 = """
       INSERT INTO rt985tr (
        t985codcia,
        t985numtr,
        t985agno,
        t985periodo,
        t985numformulario,
        t985codtipodeclaracion,
        t985aprobada,
        t985fechadiligenciamiento,
        t985fecha,
        t985numradicadoentrada,
        t985fecharadicadoentrada,
        t985nit,
        t985coddpto,
        t985codmpio,
        t985codpostal,
        t985direccion,
        t985telefono,
        t985codtipousuario,
        t985nitreplegal,
        t985codubicacion,
        t985idcobro,
        t985anulado,
        t985observacion,
        t985nitelaboro,
        t985cargoelaboro,
        t985lugarelaboro,
        t985numficha,
        t985nummatricula,
        t985geoubicacion,
        t985idtramite
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

        # # Insertar cada dato en la tabla T985TR
        # for dato_985 in data_985:
        #  dato_985 = tuple(None if val is None else val for val in dato_985)
        #  cursor.execute(insert_query_985, dato_985)

         
        insert_query_982 = """
       INSERT INTO rt982tuacaptacion (
        t982codcia,
        t982numtua,
        t982consecutivo,
        t982codtipofuentehid,
        t982codclaseusoagua,
        t982codfuentehid,
        t982codtramo,
        t982coddpto,
        t982codmpio,
        t982factorregional
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

        # # Insertar cada dato en la tabla T982TUACAPTACION
        # for dato_982 in data_982:
        #  dato_982 = tuple(None if val is None else val for val in dato_982)
        #  cursor.execute(insert_query_982, dato_982)
   

    

        insert_query_981 = """
       INSERT INTO rt981tuaactividad (
        t981codcia,
        t981numtua,
        t981codactividadciiu,
        t981descripcion
       
    ) 
    VALUES (%s,%s,%s,%s)
"""

        #  #Insertar cada dato en la tabla t981tuaactividad
        # for dato_981 in data_981:
        #  dato_981 = tuple(None if val is None else val for val in dato_981)
        #  cursor.execute(insert_query_981, dato_981)



        insert_query_980 = """
       INSERT INTO rt980tua (
        t980codcia,
        t980numtua,
        t980agno,
        t980periodo,
        t980numformulario,
        t980codtipodeclaracion,
        t980aprobada,
        t980fechadiligenciamiento,
        t980fecha,
        t980numradicadoentrada,
        t980fecharadicadoentrada,
        t980nit,
        t980coddpto,
        t980codmpio,
        t980codpostal,
        t980direccion,
        t980telefono,
        t980codtipousuario,
        t980nitreplegal,
        t980codubicacion,
        t980idcobro,
        t980anulado,
        t980observacion,
        t980idtramite
       
       
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

        #  #Insertar cada dato en la tabla t981tuaactividad
        # for dato_980 in data_980:
        #  dato_980 = tuple(None if val is None else val for val in dato_980)
        #  cursor.execute(insert_query_980, dato_980)


        insert_query_956 = """
       INSERT INTO rt956fuentehid (
        t956codcia,
        t956codfuentehid,
        t956nombre,
        t956observacion,
        t956geoubicacion,
        t956areacuenca,
        t956longitudcauce,
        t956movimiento


    
       
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
"""

        #  #Insertar cada dato en la tabla t981tuaactividad
        # for dato_956 in data_956:
        #  dato_956 = tuple(None if val is None else val for val in dato_956)
        #  cursor.execute(insert_query_956, dato_956)

        insert_query_904 = """
       INSERT INTO rt904rentactabanco (
        t904codcia,
        t904codtiporenta,
        t904codctabanco
    


    
       
    ) 
    VALUES (%s,%s,%s)
"""

        #  #Insertar cada dato en la tabla t981tuaactividad
        # for dato_904 in data_904:
        #   dato_904 = tuple(None if val is None else val for val in dato_904)
        #   cursor.execute(insert_query_904, dato_904)


        insert_query_914 = """
       INSERT INTO rt914distribucion (
        t914codcia,
        t914codtiporenta,
        t914numdistribucion,
        t914agno,
        t914codtipodoc,
        t914numerodoc,
        t914codctabanco,
        t914codgruporec,
        t914fecha,
        t914numorigen,
        t914codorigen,
        t914abonarliq,
        t914anulado,
        t914numerodocrnt
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

        #  #Insertar cada dato en la tabla t981tuaactividad
        # for dato_914 in data_914:
        #   dato_914 = tuple(None if val is None else val for val in dato_914)
        #   cursor.execute(insert_query_914, dato_914)


        insert_query_913 = """
       INSERT INTO rt913recaudo (
        t913codcia,
        t913codtiporenta,
        t913numrecaudo,
        t913agno,
        t913codtipodoc,
        t913codctabanco,
        t913codgruporec,
        t913nit,
        t913fecha,
        t913fechareal,
        t913valor,
        t913tipodistribucion,
        t913codtipoformulario,
        t913numformulario,
        t913numformulariopago,
        t913anulado,
        t913numanulacion,
        t913codformapago,
        t913numdocpago
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

        #  #Insertar cada dato en la tabla t981tuaactividad
        # for dato_913 in data_913:
        #   dato_913 = tuple(None if val is None else val for val in dato_913)
        #   cursor.execute(insert_query_913, dato_913)



        insert_query_915 = """
       INSERT INTO rt915distribucionliq  (
        t915codcia,
        t915codtiporenta,
        t915numdistribucion,
        t915numliquidacion,
        t915codconcepto,
        t915valorpagado,
        t915valorprescripcion,
        t915valorpagadodet
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
"""

        #  #Insertar cada dato en la tabla t981tuaactividad
        # for dato_915 in data_915:
        #   dato_915 = tuple(None if val is None else val for val in dato_915)
        #   cursor.execute(insert_query_915, dato_915)


        insert_query_916 = """
       INSERT INTO rt916distribucioncuot  (
        t916codcia,
        t916codtiporenta,
        t916numdistribucion,
        t916numliquidacion,
        t916numcuota,
        t916valorcapital,
        t916valorinteres,
        t916fechainiint,
        t916valorint1066,
        t916valorprescripcion
    ) 
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

        #  #Insertar cada dato en la tabla t981tuaactividad
        # for dato_916 in data_916:
        #   dato_916 = tuple(None if val is None else val for val in dato_916)
        #   cursor.execute(insert_query_916, dato_916)





        

      

      




        # Confirmar la transacción
        conn_postgresql.commit()
        print("Datos insertados correctamente en PostgreSQL")

    except Exception as e:
        # Manejar errores de conexión
        print("Error al insertar datos en PostgreSQL:", e)
    finally:
        if 'conn_postgresql' in locals():
            # Cerrar la conexión si está abierta
            conn_postgresql.close()
            print("Conexión PostgreSQL cerrada")

# # Obtener los datos de las columnas T970TRAMITE, T987TRVERTIMIENTO y T986TRACTIVIDAD
# datos_970, datos_987, datos_986 , datos_985 , datos_982 , datos_981 , datos_980 , datos_956 , datos_904 ,datos_914 ,datos_913 ,datos_915,datos_916= consultar_tabla_mssql()

# # Insertar los datos en PostgreSQL
# if datos_970 and datos_987 and datos_986 and datos_985 and datos_982 and datos_981 and datos_980 and datos_956 and datos_904 and datos_914 and datos_913 and datos_915 and datos_916:
#     insertar_datos_postgresql(datos_970, datos_987,datos_986,datos_985 ,datos_982 ,datos_981,datos_980 ,datos_956,datos_904 ,datos_914,datos_913,datos_915,datos_916)



def extraccion_pimisis_job():
    load_dotenv()

    # Obtener los datos de las columnas T970TRAMITE, T987TRVERTIMIENTO y T986TRACTIVIDAD
    datos_970, datos_987, datos_986 , datos_985 , datos_982 , datos_981 , datos_980 , datos_956 , datos_904 ,datos_914 ,datos_913 ,datos_915,datos_916 = consultar_tabla_mssql()
    
    # Insertar los datos en PostgreSQL
    if datos_970 and datos_987 and datos_986 and datos_985 and datos_982 and datos_981 and datos_980 and datos_956 and datos_904 and datos_914 and datos_913 and datos_915 and datos_916:
        insertar_datos_postgresql(datos_970, datos_987,datos_986,datos_985 ,datos_982 ,datos_981,datos_980 ,datos_956,datos_904 ,datos_914,datos_913,datos_915,datos_916)