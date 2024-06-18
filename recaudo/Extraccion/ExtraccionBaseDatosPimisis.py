import psycopg2
import os
from dotenv import load_dotenv
import pymssql
from datetime import datetime

load_dotenv()


def consultar_tabla_mssql():
    try: 
        # Intentar establecer la conexión MS SQL Server
        conn_mssql = pymssql.connect(
            server = os.environ['MS_SQL_SERVER_HOST'],
            user = os.environ['MS_SQL_SERVER_USER'],
            password = os.environ['MS_SQL_SERVER_PASSWORD'],
            database = os.environ['MS_SQL_SERVER_DB'])
        print("Conexión MS SQL Server exitosa!")

        cursor = conn_mssql.cursor()

        # Consultar los datos de la tabla T970TRAMITE
        select_query_970 = """ SELECT 
                T970CodCia,T970IdTramite,T970Agno,T970CodTipoTramite,T970CodExpediente,T970CodDepen,T970NumRadicadoEntrada,T970FechaRadicadoEntrada,T970Descripcion,T970IdTramiteRef,T970Observacion,T970CodEstadoTram,
                T970TUAFECHAINIPERM,T970TUAMESESPLAZO,T970TUAFECHAFINPERM,T970NUMRESOLPERM,T970FECHARESPERM,T970TUACAUDALCONCESI,T970TUAPREDIO,T970VERIFICO_FUN
            FROM T970TRAMITE """
        cursor.execute(select_query_970)
        column_data_970 = cursor.fetchall()

        select_query_987 = """SELECT 
                T987CodCia,T987NumTR,T987Consecutivo,T987CodTipoFuenteHid,T987CodFuenteHid,T987CodTramo,T987CaudalCaptado,T987AguaEnBloque,T987ConsumoAcueducto,T987CodUbicacion
            FROM T987TRVERTIMIENTO
        """
        cursor.execute(select_query_987)
        column_data_987 = cursor.fetchall()

        
        select_query_986 = """ SELECT 
                T986CodCia,T986NumTR,T986CodActividadCIIU,T986Descripcion  
            FROM 
                T986TRACTIVIDAD
        """
        cursor.execute(select_query_986)
        select_query_986 = cursor.fetchall()


        select_query_985 = """SELECT 
                T985CodCia,T985NumTR,T985Agno,T985Periodo,T985NumFormulario,T985CodTipoDeclaracion,T985Aprobada,T985FechaDiligenciamiento,T985Fecha,T985NumRadicadoEntrada,T985FechaRadicadoEntrada,T985Nit,T985CodDpto,T985CodMpio,
                T985CodPostal,T985Direccion,T985Telefono,T985CodTipoUsuario,T985NitRepLegal,T985CodUbicacion,T985IdCobro,T985Anulado,T985Observacion,T985NitElaboro,T985CargoElaboro,T985LugarElaboro,T985NumFicha,T985NumMatricula,T985GeoUbicacion,T985IdTramite
            FROM 
                T985TR
        """
        cursor.execute(select_query_985)
        column_data_985 = cursor.fetchall()


        select_query_982 = """SELECT 
        T982CodCia,T982NumTUA,T982Consecutivo,T982CodTipoFuenteHid,T982CodClaseUsoAgua,T982CodFuenteHid,T982CodTramo,T982CodDpto,T982CodMpio,T982FactorRegional
    FROM 
        T982TUACAPTACION
        """
        cursor.execute(select_query_982)
        column_data_982 = cursor.fetchall()


        # Consultar los datos de la tabla T982TUACAPTACION
        select_query_981 = """SELECT 
        T981CodCia,T981NumTUA,T981CodActividadCIIU,T981Descripcion
    FROM 
        T981TUAACTIVIDAD
        """
        cursor.execute(select_query_981)
        column_data_981 = cursor.fetchall()



        # Consultar los datos de la tabla T980TUA
        select_query_980 = """
        SELECT 
        T980CodCia,T980NumTUA,T980Agno,T980Periodo,T980NumFormulario,T980CodTipoDeclaracion,T980Aprobada,T980FechaDiligenciamiento,T980Fecha,T980NumRadicadoEntrada,T980FechaRadicadoEntrada,T980Nit,T980CodDpto,T980CodMpio,T980CodPostal,
        T980Direccion,T980Telefono,T980CodTipoUsuario,T980NitRepLegal,T980CodUbicacion,T980IdCobro,T980Anulado,T980Observacion,T980IdTramite
    FROM 
        T980TUA
        """
        cursor.execute(select_query_980)
        column_data_980 = cursor.fetchall()


        # Consultar los datos de la tabla T956FUENTEHID
        select_query_956 = """
        SELECT 
        T956CodCia,T956CodFuenteHid,T956Nombre,T956Observacion,T956GeoUbicacion,T956AreaCuenca,T956LongitudCauce,T956Movimiento
    FROM
        T956FUENTEHID
        """
        cursor.execute(select_query_956)
        column_data_956 = cursor.fetchall()


        # Consultar los datos de la tabla T904RENTACTABANCO
        select_query_904 = """
        SELECT 
        T904CodCia,T904CodTipoRenta,T904CodCtaBanco 
    FROM
        T904RENTACTABANCO 
        """
        cursor.execute(select_query_904)
        column_data_904 = cursor.fetchall()
        

    # Consultar los datos de la tabla T914DISTRIBUCION
        select_query_914 = """
        SELECT 
        T914CodCia,T914CodTipoRenta,T914NumDistribucion,T914Agno,T914CodTipoDoc,T914NumeroDoc,T914CodCtaBanco,T914CodGrupoRec,T914Fecha,T914NumOrigen,T914CodOrigen,T914AbonarLiq,T914Anulado,T914NumeroDocRnt
    FROM
        T914DISTRIBUCION  
        """
        cursor.execute(select_query_914)
        column_data_914 = cursor.fetchall()
        

         # Consultar los datos de la tabla T914DISTRIBUCION
        select_query_913 = """
        SELECT 
        T913CodCia,T913CodTipoRenta,T913NumRecaudo,T913Agno,T913CodTipoDoc,T913CodCtaBanco,T913CodGrupoRec,T913Nit,T913Fecha,T913FechaReal,T913Valor,T913TipoDistribucion,T913CodTipoFormulario,T913NumFormulario,T913NumFormularioPago,
        T913Anulado,T913NumAnulacion,T913CodFormaPago,T913NumDocPago
    FROM
        T913RECAUDO  
        """
        cursor.execute(select_query_913)
        column_data_913 = cursor.fetchall()

        # Consultar los datos de la tabla T915DISTRIBUCIONLIQ 
        select_query_915 = """SELECT 
        T915CodCia,T915CodTipoRenta,T915NumDistribucion,T915NumLiquidacion,T915CodConcepto,T915ValorPagado,T915ValorPrescripcion,T915ValorPagadoDet 
    FROM
        T915DISTRIBUCIONLIQ   
        """
        cursor.execute(select_query_915)
        column_data_915 = cursor.fetchall()


        # Consultar los datos de la tabla T915DISTRIBUCIONLIQ 
        select_query_916 = """SELECT 
        T916CodCia,T916CodTipoRenta,T916NumDistribucion,T916NumLiquidacion,T916NumCuota,T916ValorCapital,T916ValorInteres,T916FechaIniInt,T916ValorInt1066,T916ValorPrescripcion
    FROM
        T916DISTRIBUCIONCUOT    
        """
        cursor.execute(select_query_916)
        column_data_916 = cursor.fetchall()


   # Consultar los datos 
        select_query_954 = """SELECT 
        T954CodCia,T954IdCobro,T954CodTipoRenta,T954CodTipoCobro,T954Nit,T954Liquidado,T954NumLiquidacion,T954SeCobra,T954CodOrigenCobro,T954NumOrigenCobro,T954IdPaso,T954ConsecPaso,T954NumNotificacion,T954Anulado,
        T954TUATM, T954TUAFR,T954TUAVALORTUA,T954TRTMDBO,T954TRTMSST,T954TRFRDBO,T954TRFRSST,T954TRVALORTRDBO,T954TRVALORTRSST,T954TRCANTPERANIDBO,T954TRCANTPERANISST,T954TRTIENEPSMV,T954TUAPORCDCTO,T954TUANORMADCTO,T954TUAUSARVMANUAL,
        T954REPLEGALIMPORTAD,T954TSETVB,T954TRAPLICADCTO465
    FROM
        T954COBRO    
        """
        cursor.execute(select_query_954)
        column_data_954 = cursor.fetchall()


   # Consultar los datos 
        select_query_03 = """SELECT 
        T03CodCia, T03Nit, T03CodCiudadCed, T03CodRapido, T03LibretaMil,T03MatriProf, T03Nombre, T03PrimerApellido, T03SegundoApellido,T03PrimerNombre, T03SegundoNombre, T03CodPostal, T03Direccion,
        T03Telefono, T03Fax, T03EMail, T03WebSite, T03CodTipoSociedad,T03FechaIngreso, T03CodCalifica, T03Observacion, T03CargoExterno,T03NitRel, T03CodTipoRegimen, T03TipoSeparaNombre, T03CodDpto,
        T03CodMpio, T03CODCGN, T03CODCTACONTABCAUSA, T03CODACTRUT1,T03CODACTRUT, T03CODACTRUT3, T03CodPais, T03CodTipoDocumId,T03CODRECIPROCA, T03EntAseguradora, T03CODENTCHIP, T03FECHANACIMIENTO,
        T03GENERO, T03ACTCERTIFPYG, T03FECHAACTWEBINFO, T03FECHASOLWEBINFO,T03IPADDRACTSERV, T03WEBPASSWORD, T03ACTRECIBOSICAR, T03ID_PCI_SIIF
    FROM
        T03TERCERO    
        """
        cursor.execute(select_query_03)
        column_data_03 = cursor.fetchall()



        select_query_955 = """SELECT 
        T955CodCia, T955IdCobro, T955IdItemCobro, T955Consecutivo, T955Valor,T955TUAQMES, T955TUANUMDIASMES, T955TUANUMHORAS, T955TUAVCMES,T955TUAVVMES, T955TUAFOPMES, T955TUAVMES, T955TUAVALORTOTAL,
        T955TRQMES, T955TRNUMDIASMES, T955TRNUMHORAS, T955TRCONCDBOMES,T955TRCARGACDBOMES, T955TRVALORDBO, T955TRCONCSSTMES, T955TRCARGACSSTMES,T955TRVALORSST, T955TRVALORTOTAL, T955TUAVMESMANUAL, T955TUADCTOMES
    FROM
        T955COBROITEM    
        """
        cursor.execute(select_query_955)
        column_data_955 = cursor.fetchall()


        select_query_908 = """SELECT 
        T908CodCia, T908CodTipoRenta, T908NumLiquidacion, T908Agno, T908Periodo,T908Nit, T908Fecha, T908Valor, T908ValorPagado, T908ValorPrescripcion,
        T908Anulado, T908NumResolucion, T908AgnoResolucion, T908CodOrigenLiq,T908Observacion, T908CodTipoBeneficio, T908FechaContab, T908SeCobra,T908FechaEnFirme, T908NumOrigenLiq
    FROM
        T908LIQUIDACION    
        """
        cursor.execute(select_query_908)
        column_data_908 = cursor.fetchall()




        select_query_912 = """SELECT 
        T912CodCia, T912CodTipoRenta, T912NumAnulacionLiq, T912NumLiquidacion,T912Fecha, T912NumeroDoc,T912Observacion
    FROM
        T912ANULLIQUIDACION    
        """
        cursor.execute(select_query_912)
        column_data_912 = cursor.fetchall()




        select_query_920 = """
        SELECT 
        T920CodCia, T920CodExpediente, T920CodTipoExpCorp, T920NumExpedienteSILA,T920CodExpedienteRel, T920Descripcion, T920CodEstadoExp, T920IdTramitePpal
    FROM
        T920EXPEDIENTE     
        """
        cursor.execute(select_query_920)
        column_data_920 = cursor.fetchall()




        select_query_900 = """SELECT 
        T900CodCia, T900CodTipoRenta, T900Nombre, T900Descripcion,T900CodTipoCalculoInt, T900Tramite, T900Prescripcion,T900FacilidadPago, T900Delete, T900CodEAN13,T900SubCodAltEAN13, T900PreSFavor
    FROM
        T900TIPORENTA      
        """
        cursor.execute(select_query_900)
        column_data_900 = cursor.fetchall()


        select_query_971 = """SELECT 
        T971CodCia,T971IdTramite,T971Nit,T971CodTramTipoTer,T971Observacion 

    FROM
        T971TRAMITETERCERO       
        """
        cursor.execute(select_query_971)
        column_data_971 = cursor.fetchall()


        select_query_972 = """SELECT 
        T972CodCia,T972IdTramite,T972CodUbicacion,T972Direccion,T972Observacion
    FROM
        T972TRAMITEUBICACION        
        """
        cursor.execute(select_query_972)
        column_data_972 = cursor.fetchall()




        select_query_973 = """SELECT 
        T973CodCia,T973IdTramite,T973Consecutivo,T973CodTipoFuenteHid,T973CodFuenteHid,T973CodTramo
    FROM
        T973TRAMITEFTEHIDTRA         
        """
        cursor.execute(select_query_973)
        column_data_973 = cursor.fetchall()


        select_query_976 = """
        SELECT 
        T976CodCia, T976IdTramite, T976IdPaso, T976ConsecPaso, T976IdCobro,T976NumRadicadoEntrada, T976FechaRadicadoEntrada, T976CodEstadoTram,
        T976CodEstadoTramAnt, T976FechaInicial, T976FechaFinal, T976FechaRealizacion,T976Cumplido, T976TimeStamp, T976AFVOLUMENTOTAL, T976OTORGADO, T976Nit,T976FechaCobro, T976DIRECFECHASALIDA, T976DIRECFECHADEVOL 
    FROM
        T976TRAMITEPASO          
        """
        cursor.execute(select_query_976)
        column_data_976 = cursor.fetchall()





        select_query_918 = """SELECT 
       T918CodCia, T918CodTipoExpCorp, T918Nombre, T918Observacion, T918Delete, T918CodSerie
    FROM
        T918TIPOEXPEDIENTE           
        """
        cursor.execute(select_query_918)
        column_data_918 = cursor.fetchall()


        select_query_909 = """
        SELECT 
       T909CodCia,T909CodTipoRenta,T909NumLiquidacion,T909CodConcepto,T909Valor,T909ValorPagado,T909ValorBaseSancion,T909FechaBaseSancion,T909ValorPrescripcion,T909ValorDescBenef,T909ValorPagoAntBenef,T909ValorDeterioro, T909ValorPagadoDet 
    FROM
        T909LIQCONCEPTO            
        """
        cursor.execute(select_query_909)
        column_data_909 = cursor.fetchall()



        select_query_919 = """SELECT 
        T919CodCia, T919CodEstadoExp, T919Nombre, T919Observacion, T919Delete
    FROM
        T919ESTADOEXPEDIENTE             
        """
        cursor.execute(select_query_919)
        column_data_919 = cursor.fetchall()




        select_query_901 = """SELECT 
        T901CodCia ,T901CodCia ,T901Agno ,T901Periodo ,T901Descripcion,T901FechaInicial,T901FechaFinal,T901CodTipoCalcFacilidad ,T901CodActividadCIIUPref 
    FROM
        T901PERIODO             
        """
        cursor.execute(select_query_901)
        column_data_901 = cursor.fetchall()



        select_query_903 = """SELECT 
        T903CodCia, T903CodTipoRenta, T903CodConcepto,  T903Nombre, T903Etiqueta, T903TipoOper, T903ValorRango, T903Observacion,T903CodConceptoDist 
    FROM
        T903CONCEPTO             
        """
        cursor.execute(select_query_903)
        column_data_903 = cursor.fetchall()


        select_query_906 = """SELECT 
        T906CodCia, T906CodTipoRenta, T906Agno, T906CodConcepto, T906CodTipoAsiento, T906Consecutivo, T906CodCta, T906CodCentro, T906Nit, T906Referencia, T906Detalle, T906ValorBase, T906ValorDebito, T906ValorCredito
    FROM
        T906CONCEPTOCONTAB             
        """
        cursor.execute(select_query_906)
        column_data_906 = cursor.fetchall()


        select_query_993 = """SELECT 
        T993CodCia, T993NumTransfSectElect, T993Agno, T993Periodo, T993NumFormulario, T993CodTipoDeclaracion, T993Aprobada, T993FechaDiligenciamiento, T993Fecha, T993NumRadicadoEntrada, T993FechaRadicadoEntrada, T993Nit, T993IdCobro, T993Anulado, T993Observacion
    FROM
        T993TRANSFSECTELECT             
        """
        cursor.execute(select_query_993)
        column_data_993 = cursor.fetchall()


        select_query_994 = """SELECT 
       T994CodCia, T994NumNotificacion, T994CodModoNotificacion, T994FechaEnvioCorreoCert, T994FechaRptaRecibidoCorreoCert, T994CodMotivoDevolCorreoCert, T994Nit, T994CodDpto, T994CodMpio, T994Direccion,T994CodPostal,T994Telefono, T994EMail, T994CodTipoRpteNotif, T994NitRpteNotif, T994NombreRpteNotif,
       T994FechaNotificacion, T994DocNotifPersonal, T994Observacion, T994DocCitacion, T994FechaEnvioCitacion, T994CodMotivoDevolCitacion, T994DocNoRecibeCitacion, T994DocAviso, T994FechaEnvioAviso,
       T994CodMotivoDevolAviso, T994FechaRecibidoAviso, T994AplicaCodigoNuevo, T994FechaEdicto, T994FechaEnFirme, T994CodOrigenNotif, T994FechaInterpusoRecurso, T994Anulado, T994FechaAnulacion, T994MotivoAnulacion,
       T994FechaInicio, T994FechaRecibidoCitacion, T994TimeStamp, T994FechaAvisoWeb, T994FechaPublicaCitacion, T994DocAvisoConstancia, T994DocEdicto, T994DocFijaAviso, T994DocPublicaCitacion
    FROM
        T994NOTIFICACION             
        """
        cursor.execute(select_query_994)
        column_data_994 = cursor.fetchall()


        select_query_05 = """SELECT 
        T05CodTipoSociedad, T05Nombre, T05Observacion, T05Delete
    FROM
        T05TIPOSOCIEDAD             
        """
        cursor.execute(select_query_05)
        column_data_05 = cursor.fetchall()

        select_query_25 = """SELECT 
        T25CodDpto, T25CodMpio, T25Nombre, T25Observacion
    FROM
        T25MUNICIPIO             
        """
        cursor.execute(select_query_25)
        column_data_25 = cursor.fetchall()



        select_query_26 = """SELECT 
        T26CodPais, T26Nombre, T26Observacion, T26Delete, T26Alfa2CodPais, T26Alfa3CodPais, T26ExogenaCodPais
    FROM
        T26PAIS             
        """
        cursor.execute(select_query_26)
        column_data_26 = cursor.fetchall()

        select_query_27 = """SELECT 
        T27CodTipoDocumId, T27Nombre, T27Observacion, T27Delete, T27Alfa2CodTipoDocumId, T27Alfa1CodTipoDocumId
    FROM
        T27TIPODOCUMID             
        """
        cursor.execute(select_query_27)
        column_data_27 = cursor.fetchall()

        select_query_10 = """SELECT 
        T10CodCia, T10Agno, T10CodTipoRet, T10RangoDesde, T10RangoHasta, T10Porcentaje, T10Valor, T10ValorUVTAdic
    FROM
        T10TIPORETENRANGO             
        """
        cursor.execute(select_query_10)
        column_data_10 = cursor.fetchall()


        select_query_17 = """SELECT 
        T17CodTipoRegimen, T17Nombre, T17Observacion, T17Delete
    FROM
        T17TIPOREGIMEN             
        """
        cursor.execute(select_query_17)
        column_data_17 = cursor.fetchall()



    
        # #Mostrar los datos obtenidos
        # print("Datos obtenidos de la tabla column en MS SQL Server:")
        # for row in column_data_17:
        #     print(row)


        # Cerrar la conexión a MS SQL Server
        conn_mssql.close()

        # Retornar los datos obtenidos
        return column_data_970, column_data_987, select_query_986 ,column_data_985,column_data_982,column_data_981,column_data_980,column_data_956,column_data_904,column_data_914,column_data_913,column_data_915,column_data_916,column_data_954,column_data_03,column_data_955,column_data_908,column_data_912,column_data_920,column_data_900,column_data_971,column_data_972,column_data_973,column_data_976,column_data_918,column_data_909,column_data_919,column_data_901,column_data_903,column_data_906,column_data_993,column_data_994,column_data_05,column_data_25,column_data_26,column_data_27,column_data_10,column_data_17

    except Exception as e:
        # Manejar errores de conexión
        print("Error de conexión MS SQL Server:", e)
        return None, None, None
    




def insertar_datos_postgresql(data_970, data_987, data_986, data_985 , data_982 ,data_981 ,data_980,data_956,data_904,data_914,data_913,data_915,data_916,data_954,data_03,data_955,data_908,data_912,data_920,data_900,data_971,data_972,data_973,data_976,data_918,data_909,data_919,data_901,data_903,data_906,data_993,data_994,data_05,data_25,data_26,data_27,data_10,data_17):
    try:
        # Intentar establecer la conexión PostgreSQL
        conn_postgresql = psycopg2.connect(
          host=os.environ['BIA_DB_HOST'], 
          port=os.environ['BIA_DB_PORT'],
          database=os.environ['BIA_DB_NAME'], 
          user=os.environ['BIA_DB_USER'],
          password=os.environ['BIA_DB_PASSWORD']
        )
        print("Conexión PostgreSQL exitosa!")

        cursor = conn_postgresql.cursor()


        # Eliminar datos existentes de las tablas
        # cursor.execute("DELETE FROM Tabla#")
     





        # Consultar los registros existentes en la tabla rt994notificacion usando los campos especificados para la validación
        cursor.execute("""SELECT 
            t994codcia, t994numnotificacion, t994nit, t994coddpto, t994codmpio, t994direccion, t994codpostal, t994telefono, t994email
        FROM rt994notificacion
        """)
        existing_records = cursor.fetchall()
        existing_records_set = {(rec[0], rec[1], rec[2], rec[3], rec[4], rec[5], rec[6], rec[7], rec[8]) for rec in existing_records}

        # Comparar y encontrar los nuevos registros
        nuevos_registros_994 = [
            dato_994 for dato_994 in data_994 
            if (dato_994[0], dato_994[1], dato_994[6], dato_994[7], dato_994[8], dato_994[9], dato_994[10], dato_994[11], dato_994[12]) not in existing_records_set
        ]

        if nuevos_registros_994:
            print("Nuevos registros a insertar en la tabla rt994notificacion:")
            for registro in nuevos_registros_994:
                print(registro)

            insert_query_994 = """
            INSERT INTO rt994notificacion (
                t994codcia, t994numnotificacion, t994codmodonotificacion,t994fechaenviocorreocert, t994fecharptarecibidocorreocert, t994codmotivodevolcorreocert, 
                t994nit, t994coddpto, t994codmpio, t994direccion, t994codpostal, t994telefono, t994email, t994codtiporptenotif, t994nitrptenotif, t994nombrerptenotif, 
                t994fechanotificacion, t994docnotifpersonal, t994observacion, t994doccitacion, t994fechaenviocitacion, t994codmotivodevolcitacion, t994docnorecibecitacion, t994docaviso, 
                t994fechaenvioaviso, t994codmotivodevolaviso, t994fecharecibidoaviso, t994aplicacodigonuevo,t994fechaedicto, t994fechaenfirme, t994codorigennotif, t994fechainterpusorecurso, 
                t994anulado, t994fechaanulacion, t994motivoanulacion, t994fechainicio, t994fecharecibidocitacion,t994timestamp, t994fechaavisoweb, t994fechapublicacitacion, t994docavisoconst, t994docedicto, 
                t994docfijaaviso, t994docpublicacitacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            for dato_994 in nuevos_registros_994:
                dato_994 = tuple(None if val is None else val for val in dato_994)
                # Convertir fechas de cadena a objetos datetime si es necesario
                for i, value in enumerate(dato_994):
                    if i in [3, 4, 17, 20, 24, 26, 28, 29, 31, 33, 35, 36, 38, 39, 41] and isinstance(value, str):
                        try:
                            dato_994 = list(dato_994)
                            dato_994[i] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            dato_994 = tuple(dato_994)
                        except ValueError:
                            pass  # El valor no es una fecha válida, dejarlo como está
                cursor.execute(insert_query_994, dato_994)
            conn_postgresql.commit()
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt994notificacion.")










        cursor.execute("SELECT   t05codtiposociedad, t05nombre, t05observacion, t05delete FROM rt05tiposociedad")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_05 for dato_05 in data_05 if tuple(dato_05) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt27tipodocumid:")
            for registro in nuevos_registros:
                print(registro)
            insert_query_05 = """
            INSERT INTO rt05tiposociedad   (
             t05codtiposociedad, t05nombre, t05observacion, t05delete
             )VALUES (%s, %s, %s, %s)"""
            for dato_05 in nuevos_registros:
                dato_05 = tuple(None if val is None else val for val in dato_05)
                cursor.execute(insert_query_05, dato_05)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt05tiposociedad.")







        cursor.execute("SELECT t10codcia, t10agno, t10codtiporet, t10rangodesde, t10rangohasta, "
                       "t10porcentaje, t10valor, t10valoruvtadic FROM rt10tiporetenrango")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros_10 = [dato_10 for dato_10 in data_10 if tuple(dato_10[:8]) not in existing_records_set]

        if nuevos_registros_10:
            print("Nuevos registros a insertar en la tabla rt10tiporetenrango:")
            for registro in nuevos_registros_10:
                print(registro)

            insert_query_10 = """
                INSERT INTO rt10tiporetenrango (
                    t10codcia, t10agno, t10codtiporet, t10rangodesde, t10rangohasta, 
                    t10porcentaje, t10valor, t10valoruvtadic
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            for dato_10 in nuevos_registros_10:
                dato_10 = tuple(None if val is None else val for val in dato_10)
                cursor.execute(insert_query_10, dato_10)
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt10tiporetenrango.")




        cursor.execute("SELECT t17codtiporegimen, t17nombre, t17observacion, t17delete FROM rt17tiporegimen")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_17 for dato_17 in data_17 if tuple(dato_17) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt17tiporegimen:")
            for registro in nuevos_registros:
                print(registro)
            insert_query_17 = """
                INSERT INTO rt17tiporegimen (
                    t17codtiporegimen, t17nombre, t17observacion, t17delete
                )
                VALUES (%s, %s, %s, %s)
            """
            for dato_17 in nuevos_registros:
                dato_17 = tuple(None if val is None else val for val in dato_17)
                cursor.execute(insert_query_17, dato_17)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt17tiporegimen.")






        cursor.execute("SELECT    t25coddpto, t25codmpio, t25nombre, t25observacion FROM rt25municipio")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_25 for dato_25 in data_25 if tuple(dato_25) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt27tipodocumid:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_25 = """
            INSERT INTO rt25municipio   (
             t25coddpto, t25codmpio, t25nombre, t25observacion)VALUES (%s, %s, %s, %s)"""
            for dato_25 in nuevos_registros:
                dato_25 = tuple(None if val is None else val for val in dato_25)
                cursor.execute(insert_query_25, dato_25)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt25municipio.")








        cursor.execute("SELECT   t26codpais, t26nombre, t26observacion, t26delete, t26alfa2codpais, t26alfa3codpais, t26exogenacodpais FROM rt26pais")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_26 for dato_26 in data_26 if tuple(dato_26) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt27tipodocumid:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_27 = """
            INSERT INTO rt26pais  ( t26codpais, t26nombre, t26observacion, t26delete, t26alfa2codpais, t26alfa3codpais, t26exogenacodpais)
            VALUES (%s, %s, %s, %s, %s, %s, %s) """
            for dato_26 in nuevos_registros:
                dato_26 = tuple(None if val is None else val for val in dato_26)
                cursor.execute(insert_query_27, dato_26)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt26pais.")






        # Consultar datos existentes en rt901periodo
        cursor.execute("SELECT t901codcia, t901codtiporenta, t901agno, t901periodo, t901descripcion "
                       "FROM rt901periodo")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)

        # Filtrar nuevos registros que no están en la tabla
        nuevos_registros = []
        for registro in data_901:
            clave_primaria = (registro[0], registro[1], registro[2], registro[3], registro[4])
            if clave_primaria not in existing_records_set:
                nuevos_registros.append(registro)

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt901periodo:")
            for registro in nuevos_registros:
                print(registro)

                # Preparar la consulta de inserción
                insert_query_901 = """
                    INSERT INTO rt901periodo (
                        t901codcia, t901codtiporenta, t901agno, t901periodo, t901descripcion,
                        t901fechainicial, t901fechafinal, t901codtipocalcfacilidad, t901codactividadciiupref
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                # Convertir fechas de cadena a objetos datetime si es necesario
                registro = list(registro)  # Convertir a lista para modificar las fechas
                for i, value in enumerate(registro):
                    if i in [5, 6] and isinstance(value, str):
                        try:
                            registro[i] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            print(f"Error: La fecha '{value}' en el registro no es válida.")
                            continue  # Puedes manejar el error de fecha inválida según sea necesario

                # Ejecutar la consulta de inserción
                cursor.execute(insert_query_901, tuple(registro))  # Convertir de nuevo a tupla para la ejecución
            print("Registros insertados correctamente en la tabla rt901periodo.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt901periodo.")








        # Obtener todos los registros existentes
        cursor.execute("""
            SELECT t993numtransfsectelect
            FROM rt993transfsectelect
        """)
        existing_records = cursor.fetchall()
        existing_records_set = set(record[0] for record in existing_records)
        nuevos_registros = [dato_993 for dato_993 in data_993 if dato_993[1] not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt993transfsectelect:")
            for registro in nuevos_registros:
                print(registro)
            
            insert_query_993 = """
            INSERT INTO rt993transfsectelect (
                t993codcia, t993numtransfsectelect, t993agno, t993periodo, t993numformulario, t993codtipodeclaracion, t993aprobada, t993fechadiligenciamiento, t993fecha, 
                t993numradicadoentrada, t993fecharadicadoentrada, t993nit, t993idcobro, t993anulado, t993observacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            for dato_993 in nuevos_registros:
                # Asegurarse de que ningún valor sea None si se requiere
                dato_993 = tuple(None if val is None else val for val in dato_993)
                cursor.execute(insert_query_993, dato_993)
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt993transfsectelect.")







   




      # Obtener registros existentes de la tabla rt909liqconcepto
        cursor.execute("""
            SELECT t909codcia, t909codtiporenta, t909numliquidacion, t909codconcepto, t909valor, t909valorpagado 
            FROM rt909liqconcepto
        """)
        existing_records = cursor.fetchall()
        existing_records_set = {tuple(record) for record in existing_records}

        # Filtrar los registros nuevos
        nuevos_registros = [registro for registro in data_909 if tuple(registro[:6]) not in existing_records_set]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt909liqconcepto:")
            for registro in nuevos_registros:
                print(registro)

                insert_query_909 = """
                INSERT INTO rt909liqconcepto (
                    t909codcia, t909codtiporenta, t909numliquidacion, t909codconcepto, t909valor, t909valorpagado
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """

                registro = tuple(None if val is None else val for val in registro)
                # Convertir fechas de cadena a objetos datetime si es necesario
                for i, value in enumerate(registro):
                    if i in [7, 8, 10] and isinstance(value, str):
                        try:
                            registro = list(registro)
                            registro[i] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            registro = tuple(registro)
                        except ValueError:
                            pass  # El valor no es una fecha válida, dejarlo como está

                cursor.execute(insert_query_909, registro[:6])  # Seleccionar solo las primeras 6 columnas
            print("Registros insertados correctamente en la tabla rt909liqconcepto.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt909liqconcepto.")













        # Consulta inicial para obtener registros existentes
        cursor.execute("SELECT t916codcia, t916codtiporenta, t916numdistribucion, t916numliquidacion, t916numcuota FROM rt916distribucioncuot")
        existing_records = cursor.fetchall()
        existing_records_set = {(rec[0], rec[1], rec[2], rec[3], rec[4]) for rec in existing_records}

        # Filtrar los registros nuevos
        nuevos_registros = [
            dato_916 for dato_916 in data_916
            if (dato_916[0], dato_916[1], dato_916[2], dato_916[3], dato_916[4]) not in existing_records_set
        ]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt916distribucioncuot:")
            for registro in nuevos_registros:
                print(registro)

                # Preparar los datos para la inserción
                registro = tuple(None if val is None else val for val in registro)

                # Convertir fechas de cadena a objetos datetime si es necesario
                for i, value in enumerate(registro):
                    if i == 7 and isinstance(value, str):
                        try:
                            registro[i] = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            pass  # El valor no es una fecha válida, dejarlo como está

                # Insertar el registro nuevo
                insert_query_916 = """
                    INSERT INTO rt916distribucioncuot (
                        t916codcia, t916codtiporenta, t916numdistribucion, t916numliquidacion,
                        t916numcuota, t916valorcapital, t916valorinteres, t916fechainiint,
                        t916valorint1066, t916valorprescripcion
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query_916, registro)

            print("Registros insertados correctamente en rt916distribucioncuot.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt916distribucioncuot.")







        


        cursor.execute("SELECT   t915codcia,t915codtiporenta,t915numdistribucion,t915numliquidacion,t915codconcepto,t915valorpagado,t915valorprescripcion,t915valorpagadodet FROM rt915distribucionliq")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_915 for dato_915 in data_915 if tuple(dato_915) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt915distribucionliq:")
            for registro in nuevos_registros:
                print(registro)
            insert_query_915 = """
            INSERT INTO rt915distribucionliq   (
                t915codcia,t915codtiporenta,t915numdistribucion,t915numliquidacion,t915codconcepto,t915valorpagado,t915valorprescripcion,t915valorpagadodet)VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
            for dato_915 in nuevos_registros:
                dato_915 = tuple(None if val is None else val for val in dato_915)
                cursor.execute(insert_query_915, dato_915)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt915distribucionliq.")










        # Consulta para obtener registros existentes de rt912anulliquidacion
        cursor.execute("SELECT t912codcia, t912codtiporenta, t912numanulacionliq, t912numliquidacion, t912fecha, t912numerodoc, t912observacion FROM rt912anulliquidacion")
        existing_records = cursor.fetchall()
        existing_records_set = {(rec[0], rec[1], rec[2], rec[3], rec[5], rec[6]) for rec in existing_records}
        nuevos_registros = [
            (
                dato[0], dato[1], dato[2], dato[3], dato[5], dato[6]
            ) for dato in data_912 if (
                dato[0], dato[1], dato[2], dato[3], dato[5], dato[6]
            ) not in existing_records_set
        ]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt912anulliquidacion:")
            for registro in nuevos_registros:
                print(registro)

                # Insertar registros nuevos
                insert_query_912 = """
                    INSERT INTO rt912anulliquidacion (
                        t912codcia, t912codtiporenta, t912numanulacionliq, t912numliquidacion, 
                        t912numerodoc, t912observacion
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """
            cursor.execute(insert_query_912, registro)

            print("Registros insertados correctamente en rt912anulliquidacion.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt912anulliquidacion.")







        # Consulta para obtener registros existentes de rt913recaudo
        cursor.execute("SELECT t913codctabanco, t913nit, t913valor  FROM rt913recaudo")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)

        # Filtrar los registros nuevos
        nuevos_registros = [dato_913 for dato_913 in data_913 if (dato_913[5], dato_913[7], dato_913[10]) not in existing_records_set]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt913recaudo:")
            for registro in nuevos_registros[:20]:  # Limitar la impresión a los primeros 20 registros
                print(registro)

            insert_query_913 = """
            INSERT INTO rt913recaudo (
                t913codcia, t913codtiporenta, t913numrecaudo, t913agno, t913codtipodoc, t913codctabanco, t913codgruporec, 
                t913nit, t913fecha, t913fechareal, t913valor, t913tipodistribucion, t913codtipoformulario, t913numformulario, 
                t913numformulariopago, t913anulado, t913numanulacion, t913codformapago, t913numdocpago
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            for dato_913 in nuevos_registros:
                dato_913 = tuple(None if val is None else val for val in dato_913)
                cursor.execute(insert_query_913, dato_913)
            print("Registros insertados correctamente.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt913recaudo.")






        # Obtener registros existentes de la tabla rt985tr
        cursor.execute("""
            SELECT t985codcia, t985numtr, t985agno, t985periodo, t985numformulario, t985codtipodeclaracion,
                   t985aprobada, t985fechadiligenciamiento, t985fecha, t985numradicadoentrada, t985fecharadicadoentrada,
                   t985nit, t985coddpto, t985codmpio, t985codpostal, t985direccion, t985telefono, t985codtipousuario,
                   t985nitreplegal, t985codubicacion, t985idcobro, t985anulado, t985observacion, t985nitelaboro,
                   t985cargoelaboro, t985lugarelaboro, t985numficha, t985nummatricula, t985geoubicacion, t985idtramite
            FROM rt985tr
        """)
        existing_records = cursor.fetchall()
        existing_records_set = {tuple(record) for record in existing_records}

        # Filtrar los registros nuevos
        nuevos_registros = []
        for dato in data_985:
            exists = False
            for record in existing_records:
                if dato[:6] == record[:6]:
                    exists = True
                    break
            if not exists:
                nuevos_registros.append(dato)

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt985tr:")
            for i, registro in enumerate(nuevos_registros):
                    print(registro)
               
            insert_query_985 = """
            INSERT INTO rt985tr (
                t985codcia, t985numtr, t985agno, t985periodo, t985numformulario, t985codtipodeclaracion,
                t985aprobada, t985fechadiligenciamiento, t985fecha, t985numradicadoentrada, t985fecharadicadoentrada,
                t985nit, t985coddpto, t985codmpio, t985codpostal, t985direccion, t985telefono, t985codtipousuario,
                t985nitreplegal, t985codubicacion, t985idcobro, t985anulado, t985observacion, t985nitelaboro,
                t985cargoelaboro, t985lugarelaboro, t985numficha, t985nummatricula, t985geoubicacion, t985idtramite
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for dato_985 in nuevos_registros:
                dato_985 = tuple(None if val is None else val for val in dato_985)
                # Convertir fechas de cadena a objetos datetime si es necesario
                for i, value in enumerate(dato_985):
                    if i in [7, 8, 10] and isinstance(value, str):  # Añadir más índices si es necesario
                        try:
                            dato_985 = list(dato_985)
                            dato_985[i] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                            dato_985 = tuple(dato_985)
                        except ValueError:
                            pass  # El valor no es una fecha válida, dejarlo como está

                cursor.execute(insert_query_985, dato_985)
            print("Registros insertados correctamente.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt985tr.")










        # Insertar datos en la tabla rt976tramitepaso
        cursor.execute("SELECT t976idtramite, t976idpaso, t976consecpaso FROM rt976tramitepaso")
        existing_records = cursor.fetchall()
        existing_ids = {(record[0], record[1], record[2]) for record in existing_records}

        # Filtrar los registros nuevos
        nuevos_registros = [registro for registro in data_976 if (registro[1], registro[2], registro[3]) not in existing_ids]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt976tramitepaso:")
            for registro in nuevos_registros:
                print(registro)

                insert_query_976 = """
                INSERT INTO rt976tramitepaso (
                    t976codcia, t976idtramite, t976idpaso, t976consecpaso, t976idcobro,
                    t976numradicadoentrada, t976fecharadicadoentrada, t976codestadotram,
                    t976codestadotramant, t976fechainicial, t976fechafinal, t976fecharealizacion,
                    t976cumplido, t976timestamp, t976afvolumentotal, t976otorgado, t976nit,
                    t976fechacobro, t976direcfechasalida, t976direcfechadevol
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                registro = tuple(None if val is None else val for val in registro)
                # Convertir fechas de cadena a objetos datetime si es necesario
                for i, value in enumerate(registro):
                    if i in [6, 10, 11, 16, 17, 18] and isinstance(value, str):
                        try:
                            registro[i] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S').date()
                        except ValueError:
                            pass  # El valor no es una fecha válida, dejarlo como está

                cursor.execute(insert_query_976, registro)
            print("Registros insertados correctamente.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt976tramitepaso.")






        # Insertar datos en la tabla rt908liquidacion
        cursor.execute("SELECT t908nit, t908observacion, t908codtiporenta FROM rt908liquidacion")
        existing_records = cursor.fetchall()
        existing_nits = [record[0] for record in existing_records]
        existing_tiporenta = [record[2] for record in existing_records]

        # Filtrar los registros nuevos
        nuevos_registros = [registro for registro in data_908 if registro[5] not in existing_nits or registro[1] not in existing_tiporenta]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt908liquidacion:")
            for registro in nuevos_registros:
                print(registro)

                insert_query_908 = """
                INSERT INTO rt908liquidacion (
                    t908codcia, t908codtiporenta, t908numliquidacion, t908agno, t908periodo,
                    t908nit, t908fecha, t908valor, t908valorpagado, t908valorprescripcion,
                    t908anulado, t908numresolucion, t908agnoresolucion, t908codorigenliq,
                    t908observacion, t908codtipobeneficio, t908fechacontab, t908secobra,
                    t908fechaenfirme, t908numorigenliq
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                registro = tuple(None if val is None else val for val in registro)
                # Convertir fechas de cadena a objetos datetime si es necesario
                for i, value in enumerate(registro):
                    if i in [6, 16, 18] and isinstance(value, str):
                        try:
                            registro[i] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S').date()
                        except ValueError:
                            pass  # El valor no es una fecha válida, dejarlo como está

                cursor.execute(insert_query_908, registro)
            print("Registros insertados correctamente.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt908liquidacion.")






        cursor.execute("SELECT t914numdistribucion,t914codctabanco FROM rt914distribucion")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)

        # Filtrar los registros nuevos
        nuevos_registros = [dato for dato in data_914 if dato[2] not in {rec[0] for rec in existing_records_set}]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt914distribucion:")
            for registro in nuevos_registros:
                print(registro)

                insert_query_914 = """
                INSERT INTO rt914distribucion (
                    t914codcia, t914codtiporenta, t914numdistribucion, t914agno, t914codtipodoc,
                    t914numerodoc, t914codctabanco, t914codgruporec, t914fecha, t914numorigen,
                    t914codorigen, t914abonarliq, t914anulado, t914numerodocrnt
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                registro = tuple(None if val is None else val for val in registro)
                # Convertir fechas de cadena a objetos datetime si es necesario
                for i, value in enumerate(registro):
                    if i in [8] and isinstance(value, str):
                        try:
                            registro[i] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            pass  # El valor no es una fecha válida, dejarlo como está

                cursor.execute(insert_query_914, registro)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt914distribucion.")








        # Consulta para obtener registros existentes de rt980tua
        cursor.execute("""
            SELECT 
                t980codcia, t980numtua, t980agno, t980periodo, t980numformulario,t980codtipodeclaracion, t980aprobada, t980fechadiligenciamiento, t980fecha, 
                t980numradicadoentrada, t980fecharadicadoentrada, t980nit, t980coddpto,t980codmpio, t980codpostal, t980direccion, t980telefono, t980codtipousuario, 
                t980nitreplegal, t980codubicacion, t980idcobro, t980anulado, t980observacion,t980idtramite 
            FROM rt980tua
        """)
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)

        # Filtrar los registros nuevos
        nuevos_registros = [
            (
                dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], 
                dato[8], dato[9], dato[10], dato[11], dato[12], dato[13], dato[14], dato[15], 
                dato[16], dato[17], dato[18], dato[19], dato[20], dato[21], dato[22], dato[23]
            ) for dato in data_980 if (
                dato[0], dato[1]
            ) not in {(rec[0], rec[1]) for rec in existing_records_set}
        ]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt980tua:")
            for registro in nuevos_registros:
                print(registro)

                # Convertir fechas de cadena a objetos datetime si es necesario
                registro = list(registro)
                for i, value in enumerate(registro):
                    if i in [7, 8, 10, 21] and isinstance(value, str):
                        try:
                            registro[i] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            pass  # El valor no es una fecha, dejarlo como está

                cursor.execute("""
                    INSERT INTO rt980tua (
                        t980codcia, t980numtua, t980agno, t980periodo, t980numformulario,t980codtipodeclaracion, t980aprobada, t980fechadiligenciamiento, t980fecha, 
                        t980numradicadoentrada, t980fecharadicadoentrada, t980nit, t980coddpto, t980codmpio, t980codpostal, t980direccion, t980telefono, t980codtipousuario, 
                        t980nitreplegal, t980codubicacion, t980idcobro, t980anulado, t980observacion, t980idtramite
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(registro))

        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt980tua.")

 








      # Consulta para obtener registros existentes de rt970tramite
        cursor.execute("""
            SELECT 
                t970codcia, t970idtramite, t970agno, t970codtipotramite, t970codexpediente, t970coddepen, t970numradicadoentrada, t970fecharadicadoentrada, t970descripcion, 
                t970idtramiteref, t970observacion, t970codestadotram, t970tuafechainiperm,t970tuamesesplazo, t970tuafechafinperm, t970numresolperm, t970fecharesperm, t970tuacaudalconcesi, t970tuapredio, t970verifico_fun 
            FROM rt970tramite
        """)
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)

        # Filtrar los registros nuevos
        nuevos_registros = [
            (
                dato[0], dato[1], dato[2], dato[3], dato[4], dato[5], dato[6], dato[7], 
                dato[8], dato[9], dato[10], dato[11], dato[12], dato[13], dato[14], dato[15], 
                dato[16], dato[17], dato[18], dato[19]
            ) for dato in data_970 if (
                dato[0], dato[1]
            ) not in {(rec[0], rec[1]) for rec in existing_records_set}
        ]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt970tramite:")
            for registro in nuevos_registros:
                print(registro)

                # Convertir fechas de cadena a objetos datetime si es necesario
                registro = list(registro)
                if isinstance(registro[7], str):
                    registro[7] = datetime.strptime(registro[7], '%Y-%m-%d %H:%M:%S')
                if isinstance(registro[12], str):
                    registro[12] = datetime.strptime(registro[12], '%Y-%m-%d %H:%M:%S')
                if isinstance(registro[14], str):
                    registro[14] = datetime.strptime(registro[14], '%Y-%m-%d %H:%M:%S')
                if isinstance(registro[16], str):
                    registro[16] = datetime.strptime(registro[16], '%Y-%m-%d %H:%M:%S')

                cursor.execute("""
                    INSERT INTO rt970tramite (
                        t970codcia, t970idtramite, t970agno, t970codtipotramite, t970codexpediente,t970coddepen, t970numradicadoentrada, t970fecharadicadoentrada, t970descripcion,
                        t970idtramiteref, t970observacion, t970codestadotram, t970tuafechainiperm,t970tuamesesplazo, t970tuafechafinperm, t970numresolperm, t970fecharesperm,
                        t970tuacaudalconcesi, t970tuapredio, t970verifico_fun
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, tuple(registro))

        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt970tramite.")









        cursor.execute("SELECT  t987codcia,t987numtr,t987consecutivo,t987codtipofuentehid,t987codfuentehid,t987codtramo,t987caudalcaptado,t987aguaenbloque,t987consumoacueducto,t987codubicacion FROM rt987trvertimiento")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_987 for dato_987 in data_987 if tuple(dato_987) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt987trvertimiento:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_987 = """
            INSERT INTO rt987trvertimiento   (
           t987codcia,t987numtr,t987consecutivo,t987codtipofuentehid,t987codfuentehid,t987codtramo,t987caudalcaptado,t987aguaenbloque,t987consumoacueducto,t987codubicacion)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            for dato_987 in nuevos_registros:
                dato_987 = tuple(None if val is None else val for val in dato_987)
                cursor.execute(insert_query_987, dato_987)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt987trvertimiento.")







        cursor.execute("SELECT t986codcia,t986numtr,t986codactividadciiu,t986descripcion FROM rt986tractividad")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_986 for dato_986 in data_986 if tuple(dato_986) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt986tractividad:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_986 = """
            INSERT INTO rt986tractividad   (
            t986codcia,t986numtr,t986codactividadciiu,t986descripcion)VALUES (%s,%s,%s,%s)"""
            for dato_986 in nuevos_registros:
                dato_986 = tuple(None if val is None else val for val in dato_986)
                cursor.execute(insert_query_986, dato_986)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt986tractividad.")






        cursor.execute("SELECT  t982codcia,t982numtua,t982consecutivo,t982codtipofuentehid,t982codclaseusoagua,t982codfuentehid,t982codtramo,t982coddpto,t982codmpio,t982factorregional FROM rt982tuacaptacion")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_982 for dato_982 in data_982 if tuple(dato_982) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt982tuacaptacion:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_982 = """
            INSERT INTO rt982tuacaptacion   (
             t982codcia,t982numtua,t982consecutivo,t982codtipofuentehid,t982codclaseusoagua,t982codfuentehid,t982codtramo,t982coddpto,t982codmpio,t982factorregional)VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            for dato_982 in nuevos_registros:
                dato_982 = tuple(None if val is None else val for val in dato_982)
                cursor.execute(insert_query_982, dato_982)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt982tuacaptacion.")





        cursor.execute("SELECT t981codcia,t981numtua,t981codactividadciiu,t981descripcion FROM rt981tuaactividad")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_981 for dato_981 in data_981 if tuple(dato_981) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt981tuaactividad:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_981 = """
            INSERT INTO rt981tuaactividad   (
             t981codcia,t981numtua,t981codactividadciiu,t981descripcion)VALUES (%s,%s,%s,%s)"""
            for dato_981 in nuevos_registros:
                dato_981 = tuple(None if val is None else val for val in dato_981)
                cursor.execute(insert_query_981, dato_981)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt981tuaactividad.")


    
   

        cursor.execute("SELECT t956codcia,t956codfuentehid,t956nombre,t956observacion,t956geoubicacion,t956areacuenca,t956longitudcauce,t956movimiento FROM rt956fuentehid")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_956 for dato_956 in data_956 if tuple(dato_956) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt956fuentehid:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_956 = """
            INSERT INTO rt956fuentehid   (
                t956codcia,t956codfuentehid,t956nombre,t956observacion,t956geoubicacion,t956areacuenca,t956longitudcauce,t956movimiento)VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
            for dato_956 in nuevos_registros:
                dato_956 = tuple(None if val is None else val for val in dato_956)
                cursor.execute(insert_query_956, dato_956)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt956fuentehid.")




        cursor.execute("SELECT  t904codcia,t904codtiporenta,t904codctabanco FROM rt904rentactabanco")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_904 for dato_904 in data_904 if tuple(dato_904) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt904rentactabanco:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_904 = """
            INSERT INTO rt904rentactabanco   (
                t904codcia,t904codtiporenta,t904codctabanco)VALUES (%s,%s,%s)"""
            for dato_904 in nuevos_registros:
                dato_904 = tuple(None if val is None else val for val in dato_904)
                cursor.execute(insert_query_904, dato_904)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt904rentactabanco.")





        cursor.execute("SELECT   t920codcia, t920codexpediente, t920codtipoexpcorp,t920numexpedientesila, t920codexpedienterel, t920descripcion,t920codestadoexp, t920idtramiteppal FROM rt920expediente")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_920 for dato_920 in data_920 if tuple(dato_920) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt920expediente:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_920 = """
            INSERT INTO rt920expediente   (
               t920codcia, t920codexpediente, t920codtipoexpcorp,t920numexpedientesila, t920codexpedienterel, t920descripcion,t920codestadoexp, t920idtramiteppal)VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            for dato_920 in nuevos_registros:
                dato_920 = tuple(None if val is None else val for val in dato_920)
                cursor.execute(insert_query_920, dato_920)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt920expediente.")





        cursor.execute("SELECT t900codcia, t900codtiporenta, t900nombre, t900descripcion, t900codtipocalculoint,t900tramite, t900prescripcion, t900facilidadpago, t900delete, t900codean13, t900subcodaltean13,t900presfavor FROM rt900tiporenta")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_900 for dato_900 in data_900 if tuple(dato_900) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt900tiporenta:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_900 = """
            INSERT INTO rt900tiporenta   (
                t900codcia, t900codtiporenta, t900nombre, t900descripcion, t900codtipocalculoint,t900tramite, t900prescripcion, t900facilidadpago, t900delete, t900codean13, t900subcodaltean13,t900presfavor)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            for dato_900 in nuevos_registros:
                dato_900 = tuple(None if val is None else val for val in dato_900)
                cursor.execute(insert_query_900, dato_900)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt900tiporenta.")



        cursor.execute("SELECT  t971codcia,t971idtramite,t971nit,t971codtramtipoter,t971observacion FROM rt971tramitetercero")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_971 for dato_971 in data_971 if tuple(dato_971) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt971tramitetercero:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_971 = """
            INSERT INTO rt971tramitetercero   (
                t971codcia,t971idtramite,t971nit,t971codtramtipoter,t971observacion)VALUES (%s, %s, %s, %s, %s)"""
            for dato_971 in nuevos_registros:
                dato_971 = tuple(None if val is None else val for val in dato_971)
                cursor.execute(insert_query_971, dato_971)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt971tramitetercero.")







        cursor.execute("SELECT   t972codcia,t972idtramite,t972codubicacion,t972direccion,t972observacion FROM rt972tramiteubicacion")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_972 for dato_972 in data_972 if tuple(dato_972) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt972tramiteubicacion:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_972 = """
            INSERT INTO rt972tramiteubicacion   (
                 t972codcia,t972idtramite,t972codubicacion,t972direccion,t972observacion)VALUES (%s, %s, %s, %s, %s)"""
            for dato_972 in nuevos_registros:
                dato_972 = tuple(None if val is None else val for val in dato_972)
                cursor.execute(insert_query_972, dato_972)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt972tramiteubicacion.")




        cursor.execute("SELECT  t973codcia,t973idtramite,t973consecutivo,t973codtipofuentehid,t973codfuentehid,t973codtramo FROM rt973tramiteftehidtra")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_973 for dato_973 in data_973 if tuple(dato_973) not in existing_records_set]
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt973tramiteftehidtra:")
            for registro in nuevos_registros:
                print(registro)
            insert_query_973 = """
            INSERT INTO rt973tramiteftehidtra   (
                 t973codcia,t973idtramite,t973consecutivo,t973codtipofuentehid,t973codfuentehid,t973codtramo)VALUES (%s, %s, %s, %s, %s, %s)"""
            for dato_973 in nuevos_registros:
                dato_973 = tuple(None if val is None else val for val in dato_973)
                cursor.execute(insert_query_973, dato_973)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt973tramiteftehidtra.")





        cursor.execute("SELECT  t918codcia, t918codtipoexpcorp, t918nombre, t918observacion, t918delete, t918codserie FROM rt918tipoexpediente")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_918 for dato_918 in data_918 if tuple(dato_918) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt918tipoexpediente:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_919 = """
            INSERT INTO rt918tipoexpediente   (
                  t918codcia, t918codtipoexpcorp, t918nombre, t918observacion, t918delete, t918codserie)VALUES (%s, %s, %s, %s, %s, %s)"""
            for dato_918 in nuevos_registros:
                dato_918 = tuple(None if val is None else val for val in dato_918)
                cursor.execute(insert_query_919, dato_918)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt918tipoexpediente.")




        cursor.execute("SELECT  t919codcia, t919codestadoexp, t919nombre, t919observacion, t919delete FROM rt919estadoexpediente")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_919 for dato_919 in data_919 if tuple(dato_919) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt919estadoexpediente:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_919 = """
            INSERT INTO rt919estadoexpediente   (
                    t919codcia, t919codestadoexp, t919nombre, t919observacion, t919delete)VALUES (%s, %s, %s, %s, %s)"""
            for dato_919 in nuevos_registros:
                dato_919 = tuple(None if val is None else val for val in dato_919)
                cursor.execute(insert_query_919, dato_919)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt919estadoexpediente.")


   



        cursor.execute("SELECT  t903codcia, t903codtiporenta, t903codconcepto, t903nombre, t903etiqueta, t903tipooper, t903valorrango, t903observacion, t903codconceptodist FROM rt903concepto")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_903 for dato_903 in data_903 if tuple(dato_903) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt903concepto:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_903 = """
            INSERT INTO rt903concepto   (
                       t903codcia, t903codtiporenta, t903codconcepto, t903nombre, t903etiqueta, t903tipooper, t903valorrango, t903observacion, t903codconceptodist)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            for dato_903 in nuevos_registros:
                dato_903 = tuple(None if val is None else val for val in dato_903)
                cursor.execute(insert_query_903, dato_903)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt903concepto.")




        cursor.execute("SELECT  t906codcia, t906codtiporenta, t906agno, t906codconcepto, t906codtipoasiento, t906consecutivo, t906codcta, t906codcentro, t906nit, t906referencia, t906detalle, t906valorbase, t906valordebito, t906valorcredito FROM rt906conceptocontab")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_906 for dato_906 in data_906 if tuple(dato_906) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt906conceptocontab:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_906 = """
            INSERT INTO rt906conceptocontab   (
                       t906codcia, t906codtiporenta, t906agno, t906codconcepto, t906codtipoasiento, t906consecutivo, t906codcta, t906codcentro, t906nit, t906referencia, t906detalle, t906valorbase, t906valordebito, t906valorcredito)VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            for dato_906 in nuevos_registros:
                dato_906 = tuple(None if val is None else val for val in dato_906)
                cursor.execute(insert_query_906, dato_906)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt906conceptocontab.")








        cursor.execute("SELECT  t27codtipodocumid, t27nombre, t27observacion, t27delete, t27alfa2codtipodocumid, t27alfa1codtipodocumid FROM rt27tipodocumid")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)
        nuevos_registros = [dato_27 for dato_27 in data_27 if tuple(dato_27) not in existing_records_set]
        
        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt27tipodocumid:")
            for registro in nuevos_registros:
                print(registro)

            insert_query_27 = """
            INSERT INTO rt27tipodocumid  (t27codtipodocumid, t27nombre, t27observacion, t27delete, t27alfa2codtipodocumid, t27alfa1codtipodocumid)
            VALUES (%s, %s, %s, %s, %s, %s) """
            for dato_27 in nuevos_registros:
                dato_27 = tuple(None if val is None else val for val in dato_27)
                cursor.execute(insert_query_27, dato_27)
        else:
             print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt27tipodocumid.")








        # Consulta para obtener registros existentes de rt955cobroitem
        cursor.execute("SELECT t955codcia, t955idcobro, t955iditemcobro, t955consecutivo, t955valor, t955tuaqmes, t955tuanumdiasmes, t955tuanumhoras, t955tuavcmes, t955tuavvmes, t955tuafopmes, t955tuavmes, t955tuavalortotal, t955trqmes, t955trnumdiasmes, t955trnumhoras, t955trconcdbomes, t955trcargacdbomes, t955trvalordbo, t955trconcsstmes, t955trcargacsstmes, t955trvalorssst, t955trvalortotal, t955tuavmesmanual, t955tuadctomes FROM rt955cobroitem")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)

        # Filtrar los registros nuevos
        nuevos_registros = [
            dato for dato in data_955 if tuple(dato) not in existing_records_set
        ]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt955cobroitem:")
            for registro in nuevos_registros:
                print(registro)

                insert_query_955 = """
                INSERT INTO rt955cobroitem (
                    t955codcia, t955idcobro, t955iditemcobro, t955consecutivo, t955valor, 
                    t955tuaqmes, t955tuanumdiasmes, t955tuanumhoras, t955tuavcmes, t955tuavvmes, 
                    t955tuafopmes, t955tuavmes, t955tuavalortotal, t955trqmes, t955trnumdiasmes, 
                    t955trnumhoras, t955trconcdbomes, t955trcargacdbomes, t955trvalordbo, 
                    t955trconcsstmes, t955trcargacsstmes, t955trvalorssst, t955trvalortotal, 
                    t955tuavmesmanual, t955tuadctomes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                # Asegurarse de que los valores nulos sean manejados correctamente
                registro = tuple(None if val is None else val for val in registro)
                cursor.execute(insert_query_955, registro)

        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt955cobroitem.")




        # Consulta para obtener registros existentes de rt954cobro
        cursor.execute("SELECT t954codcia, t954idcobro, t954codtiporenta, t954codtipocobro, t954nit, t954liquidado, t954numliquidacion, t954secobra, t954codorigencobro, t954numorigencobro, t954idpaso, t954consecpaso, t954numnotificacion, t954anulado, t954tuatm, t954tuafr, t954tuavalortua, t954trtmdbo, t954trtmsst, t954trfrdbo, t954trfrsst, t954trvalortrdbo, t954trvalortrsst, t954trcantperanidbo, t954trcantperanisst, t954trtienepsmv, t954tuaporcdcto, t954tuanormadcto, t954tuausarvmanual, t954replegalimportad, t954tsetvb, t954traplicadcto465 FROM rt954cobro")
        existing_records = cursor.fetchall()
        existing_records_set = set(existing_records)

        # Filtrar los registros nuevos
        nuevos_registros = [
            dato for dato in data_954 if tuple(dato) not in existing_records_set
        ]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt954cobro:")
            for registro in nuevos_registros:
                print(registro)

                insert_query_954 = """
                INSERT INTO rt954cobro (
                    t954codcia, t954idcobro, t954codtiporenta, t954codtipocobro, t954nit, t954liquidado, 
                    t954numliquidacion, t954secobra, t954codorigencobro, t954numorigencobro, t954idpaso, 
                    t954consecpaso, t954numnotificacion, t954anulado, t954tuatm, t954tuafr, t954tuavalortua, 
                    t954trtmdbo, t954trtmsst, t954trfrdbo, t954trfrsst, t954trvalortrdbo, t954trvalortrsst, 
                    t954trcantperanidbo, t954trcantperanisst, t954trtienepsmv, t954tuaporcdcto, t954tuanormadcto, 
                    t954tuausarvmanual, t954replegalimportad, t954tsetvb, t954traplicadcto465
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                # Asegurarse de que los valores nulos sean manejados correctamente
                registro = tuple(None if val is None else val for val in registro)
                cursor.execute(insert_query_954, registro)

        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt954cobro.")




        # Consulta para obtener registros existentes
        cursor.execute("SELECT t03nit,t03nombre FROM rt03tercero")
        existing_recor = cursor.fetchall()
        existing_records_sett = {rec[0] for rec in existing_recor}

        # Filtrar los registros nuevos que no están en la tabla
        nuevos_registros = [dato for dato in data_03 if dato[1] not in existing_records_sett]

        if nuevos_registros:
            print("Nuevos registros a insertar en la tabla rt03tercero:")
            for registro in nuevos_registros:
                print(registro)

                # Convertir fechas de cadena a objetos datetime si es necesario
                registro = list(registro)  # Convertir tupla a lista para modificar valores
                for i, value in enumerate(registro):
                    if isinstance(value, str) and i == 18:  # Indicar el índice correspondiente a t03fechaingreso
                        try:
                            registro[i] = datetime.strptime(value, '%Y-%m-%d').date()
                        except ValueError:
                            print(f"Error: La fecha '{value}' en el registro no es válida.")
                            continue  # Otra acción según sea necesario si la fecha no es válida
                registro = tuple(None if val is None else val for val in registro)

                # Convertir valores None a None en la tupla dato_03
                 

                insert_query_03 = """
            INSERT INTO rt03tercero   (
               t03codcia, t03nit, t03codciudadced, t03codrapido, t03libretamil,t03matriprof, t03nombre, t03primerapellido, t03segundoapellido,t03primernombre, t03segundonombre, t03codpostal, t03direccion,t03telefono, t03fax, t03email, t03website, t03codtiposociedad,t03fechaingreso, t03codcalifica, t03observacion, t03cargoexterno, t03nitrel, t03codtiporegimen, t03tiposeparanombre, t03coddpto,t03codmpio, t03codcgn, t03codctacontabcausa, t03codactrut1,t03codactrut, t03codactrut3, t03codpais, t03codtipodocumid,t03codreciproca, t03entaseguradora, t03codentchip, t03fechanacimiento,t03genero, t03actcertifpyg, t03fechaactwebinfo, t03fechasolwebinfo,t03ipaddractserv, t03webpassword, t03actrecibosicar, t03id_pci_siif
               )VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                cursor.execute(insert_query_03, registro)

            print("Registros insertados correctamente en rt03tercero.")
        else:
            print("No hay nuevos registros para insertar. Los registros no han cambiado en la tabla rt03tercero.")






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
def extraccion_pimisis_job():
    load_dotenv()

    # Obtener los datos de las columnas T970TRAMITE, T987TRVERTIMIENTO y T986TRACTIVIDAD
    datos_970, datos_987, datos_986 , datos_985 , datos_982 , datos_981 , datos_980 , datos_956 , datos_904 ,datos_914 ,datos_913 ,datos_915,datos_916,datos_954,datos_03,datos_955,datos_908,datos_912,datos_920,datos_900,datos_971,datos_972,datos_973,datos_976,datos_918,datos_909,datos_919,datos_901,datos_903,datos_906,datos_993,datos_994,datos_05,datos_25,datos_26,datos_27,datos_10,datos_17= consultar_tabla_mssql()

    
    # Insertar los datos en PostgreSQL
    if datos_970 and datos_987 and datos_986 and datos_985 and datos_982 and datos_981 and datos_980 and datos_956 and datos_904 and datos_914 and datos_913 and datos_915 and datos_916 and datos_954 and datos_03 and datos_955 and datos_908 and datos_912 and datos_920 and datos_900 and datos_971 and datos_972 and datos_973 and datos_976 and datos_918 and datos_909 and datos_919 and datos_901 and datos_903 and datos_906 and datos_993 and datos_994 and datos_05 and datos_25 and datos_26 and datos_27 and datos_10 and datos_17:
         insertar_datos_postgresql(datos_970, datos_987,datos_986,datos_985 ,datos_982 ,datos_981,datos_980 ,datos_956,datos_904 ,datos_914,datos_913,datos_915,datos_916,datos_954,datos_03 ,datos_955,datos_908 ,datos_912,datos_920, datos_900,datos_971 ,datos_972,datos_973 ,datos_976 , datos_918 ,datos_909 ,datos_919,datos_901, datos_903 ,datos_906,datos_993,datos_994 ,datos_05,datos_25,datos_26,datos_27,datos_10,datos_17)
