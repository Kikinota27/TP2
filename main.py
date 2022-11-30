import speech_recognition as sr
import csv
import matplotlib.pyplot as plt 
# crear nuevo CSV
def transcrpicion_audio (path_audio: str)->str:
    r = sr.Recognizer()
    transcripcion: str = ""
    with sr.AudioFile(path_audio) as source:
        audio = r.record(source)
    try:
        transcripcion = r.recognize_google(audio)
    except sr.UnknownValueError:
        transcripcion= "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        transcripcion ="Could not request results from Google Speech Recognition service; {0}".format(e)
    return transcripcion
    
def leer_cvs()-> list: 
    reclamos_datos: list = []
    with open("reclamos.csv", newline='', encoding="UTF-8") as reclamos:
        csv_reader = csv.reader(reclamos, delimiter=';')
        next(csv_reader)
        for elemento in csv_reader:
            reclamos_datos.append(elemento)
    return reclamos_datos

def coordenadasADireccion(lat:str,long:str)->list:
    """
Pre: Requiere dos numeros flotante, el primero sera la longitud, el segundo la latitud.
Post: Devuelve una lista con la direccion, la localidad, y la provincia
"""
    direccion: list = []
    localidad: str = ''
    provincia:str =''
    localizador = Nominatim(user_agent="khasi@gmail.com")#Nominatim requiere si o si una identificacioin para limitar la cantidad de usos por usuario
    ubicacion:str = str(localizador.reverse(lat+' , '+long))#Aca se guarda la direccion a la que hacen referencias las coordenadas
    datos: list = ubicacion.split(',')#ubicacion es un str, con altura,calle,barrio,localidad,CP,provincia,pais
    esnumero:bool = datos[0].isdigit()
    #Dependiendo de si es provincia, o  capital o si es un lugar conocido o no, la cantidad de datos que posee ubicacion es mayor o menor que 9 elementos
    if len(datos)>=9:
        #Si posee mas de nueve elementos pertenece a CABA
        if esnumero:
            #Si el primer elemento es un numero es un lugar de caba aleatorio
            aux=datos[1]
            direccion.append(aux)
            aux=datos[0]
            direccion.append(aux)
            localidad=datos[3]
            provincia=datos[6]
            direccion.append(aux)
        else:
            #De lo contrario es un lugar conocido de caba
            aux=datos[2]
            direccion.append(aux)
            aux=datos[1]
            direccion.append(aux)
            localidad=datos[4]
            provincia=datos[7]
    elif len(datos)<=8:
        #Pertenece a provincia
        if esnumero:
            #Si el primero es la altura de la calle es un lugar aleatorio de provincia
            aux=datos[1]
            direccion.append(aux)
            aux=datos[0]
            direccion.append(aux)
            localidad=datos[3]
            provincia=datos[5]
        else:
            #Es un lugar conocido de prov si posee el nombre o titulo por que la se lo conoce popularmente
            aux=datos[2]
            direccion.append(aux)
            aux=datos[1]
            direccion.append(aux)
            localidad=datos[4]
            provincia=datos[6]
    direcc = ",".join(direccion) #convierto la direccion con formato nombre_de_calle,altura , en un str(para que no se modifique) 
    ubicar: list = [direcc,localidad,provincia]
    return ubicar

def reconocimiento_patente(path_img: str)->str:
    pass
    
def crear_cvs(reclamos_datos_nuevos: list)->None:
    with open("reclamos_nuevo.csv", 'w', newline='', encoding="UTF-8") as reclamos:
        csv_writer = csv.writer(reclamos, delimiter=',', quotechar='"', quoting= csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(["Timestamp", "Telefono", "Direccion", "Localidad", "Provincia", "Patente", "Descripcion texto", "Descripcion audio"])
        for reclamo in reclamos_datos_nuevos:
            csv_writer.writerow(reclamo)


#Listar a 1km de river y boca

#Listar centro

#robados
def leer_txt()-> list:
    with open("robados.txt", "r") as tf:
        robados_patentes: list = tf.read().split('\n') #arreglar ultimo item en blanco
    return robados_patentes

#mostrar foto y mapa

#mostrar grafico

def main()->None:
    datos_reclamos: list = leer_cvs()
    datos_reclamos_nuevo: list = []
    
    print("Creando nuevo listado")
    for reclamo in datos_reclamos:
        ubicacion: list = geolocaizacion(reclamo[2])#o [reclamo[2], reclamo[3]] //// (calle altura, localida, provincia)
        patente: str = reconocimiento_patente(reclamo[3])# reclamo[4]
        descripcion_audio: str = transcrpicion_audio(reclamo[4])# o reclamo[5] 
        datos_reclamos_nuevo.append([reclamo[0],reclamo[1],ubicacion[0], ubicacion[1], ubicacion[3], patente, reclamo[5], descripcion_audio])
    
    print("Listando reclamos a 1 Km. del estadio River Plate ")

    print("Listando reclamos a 1 Km. del estadio Boca Juniors")

    print("Listando reclamos en el centro de la ciudad")

    print("Buscando autos sospechosos")
    robados_patentes: list = leer_txt()
    for reclamo in datos_reclamos_nuevo:
        if reclamo[5] in robados_patentes:
            print(f'ALERTA, el auto con patente {reclamo[5]} tiene un pedido de caputra')
            print(f'Su posible ubicación es {reclamo[2]} en {reclamo[3]}, {reclamo[4]}')
    
    
    meses: list = ["Enero", "Febrero", "Marzo", "Abril", 
        "Mayo", "Junio", "Julio", "Agosto", "Septiembre",
        "Octubre", "Noviembre", "Diciembre" ]
    cantxmeses: list = []
    for mes in range (1,13):
        cantxmes: int = 0
        for reclamo in datos_reclamos_nuevo:
            if mes ==  int(reclamo[0][5:7]):
                cantxmes += 1
        cantxmeses.append(cantxmes)

    fig, ax = plt.subplots()
    ax.bar(meses, cantxmeses)
    plt.show()


    
    

    
    
