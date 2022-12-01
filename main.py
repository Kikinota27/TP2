import speech_recognition as sr
import csv
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from geopy.distance import geodesic       
# crear nuevo CSV
def transcrpicion_audio (ruta_audio: str)->str:
    r = sr.Recognizer()
    transcripcion: str = ""
    with sr.AudioFile(ruta_audio) as source:
        audio = r.record(source)
    try:
        transcripcion = r.recognize_google(audio, language = 'es')
    except FileNotFoundError:
        transcripcion="Reclamo sin audio"
    except sr.UnknownValueError:
        transcripcion= "Google Speech Recognition no pudo entender el audio"
    except sr.RequestError as e:
        transcripcion ="No se pudieron solicitar los resultados de Google Speech Recognition service; {0}".format(e)
    return transcripcion
def leerCsv(nom_arc:str,lista:list):
    """
Pre: Require el nombre del archivo como str y una lista vacia donde guardar los datos
Post: Al ser un procedimiento no posee, guarda los datos leído del archivo en una lista vacía
"""
    try:
        file = open(nom_arc,'r',encoding = "UTF-8")
        for linea in file:
            registro = []
            linea = linea.strip()
            registro = linea.split(';')
            lista.append(registro)
        file.close()
    except IOError:
        print("Se producjo un error de entrada y salida del archivo")
def coordenadasADireccion(lat:float,long:float)->list:
    """
Pre: Requiere dos numero flotante, el primero sera la longitud, el segundo la latitud.
Post: Devuelve una lista con la direccion, la localidad, y la provincia
"""
    localidad: str = ''
    localizador = Nominatim(user_agent="khasi@gmail.com")
    ubicacion = localizador.reverse(str(lat)+' , '+str(long))
    ubicar = ubicacion.address
    ubicarl = ubicar.split(',')
    calle: str = str(ubicarl[1])+','+str(ubicarl[0])
    comunas: list = [' Comuna 1',' Comuna 2',' Comuna 3',' Comuna 4',' Comuna 5',' Comuna 6',' Comuna 8',' Comuna 9',' Comuna 10',' Comuna 11',' Comuna 12',' Comuna 13',' Comuna 14',' Comuna 15']
    if ubicarl[4] in comunas: 
        localidad = ubicarl[4]
    elif ubicarl[5] in comunas:
        localidad = ubicarl[5]
    else:
        print("La direccion no pertenece la CABA")
    prov: str = 'CABA'
    datos: list = [calle,localidad,prov]
    return datos
def reconocimiento_patente(path_img: str)->str:
    pass
    
def crear_cvs(reclamos_datos_nuevos: list)->None:
    with open("reclamos_nuevo.csv", 'w', newline='', encoding="UTF-8") as reclamos:
        csv_writer = csv.writer(reclamos, delimiter=',', quotechar='"', quoting= csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(["Timestamp", "Telefono", "Direccion", "Localidad", "Provincia", "Patente", "Descripcion texto", "Descripcion audio"])
        for reclamo in reclamos_datos_nuevos:
            csv_writer.writerow(reclamo)
def dentroDeLaDistancia(direcc1:list,direcc2:list,distan:int):
    """
Pre: ingresas dos direcciones en forma de lista con dos elementos string, y el radio un int
Post: retorna un bool que indica si las direcciones poseen una distancia menor o igual a la indicada en el radio
"""
    dist = geodesic(direcc1,direcc2).km
    esta_dentro_de_la_distancia: bool = dist<=distan
    return esta_dentro_de_la_distancia
#Listar centro
def dentroDelCuadrante(coord:list)->bool:
    """
Pre:Requiere un lista con dos elementos str primero es latitud y el segundo es longitud
Post:Devuelve un boleano con True si cumple las condicion de estar dentro del cuadrante
"""
#Pequeña introduccion teorica -> https://acortar.link/FdUE6k
    intersec1 = ['-34.59931087515444', '-58.39337992076712']
    #Callao y Cordoba
    intersec2 = ['-34.609349307168664', '-58.39216124478244']
    #Rivadavia y Callao
    intersec3 = ['-34.60798655424728', '-58.37018659584837']
    #Rivadavia y Alem
    intersec4 = ['-34.59814231545804', '-58.37084567449758']
    #Cordoba y Alem
    dist1 = geodesic(intersec1,coord).km
    dist2 = geodesic(intersec2,coord).km
    dist3 = geodesic(intersec3,coord).km
    dist4 = geodesic(intersec4,coord).km
    suma1=dist1*dist1
    suma2=dist2*dist2
    suma3=dist3*dist3
    suma4=dist4*dist4
    division = (suma1+suma3)/(suma2+suma4)
    en_el_cuadrante: bool = division<=1.0
    return en_el_cuadrante
#robados
def leer_txt()-> list:
    with open("robados.txt", "r") as tf:
        robados_patentes: list = tf.read().split('\n') #arreglar ultimo item en blanco
    return robados_patentes

#mostrar foto y mapa

#mostrar grafico

def main()->None:
    datos_reclamos: list = []
    datos_reclamos_nuevo: list = []
    reclamos: str = 'reclamosad.csv'
    leerCsv(reclamos,datos_reclamos)
    river_loc: list = ['-34.545173623765045','-58.44980708914722']
    boca_loc:list = ['-34.63547846773916','-58.36471338729659']
    print("Creando nuevo listado")
    for reclamo in datos_reclamos:
        # (Timestamp, Teléfono_celular, coord_latitud, coord_long, ruta_foto, descripción texto,ruta_audio)
        if reclamo != datos_reclamos[0]:
            ubicacion: list = coordenadasADireccion(reclamo[2],reclamo[3])
            patente: str = reconocimiento_patente(reclamo[4])
            descripcion_audio: str = transcrpicion_audio(reclamo[6])
            datos_reclamos_nuevo.append([reclamo[0],reclamo[1],ubicacion[0], ubicacion[1], ubicacion[2], patente, reclamo[5], descripcion_audio])

    print("Listando reclamos a 1 Km. del estadio River Plate ")
    for linea in datos_reclamos:
        if linea != datos_reclamos[0]:
            coord: list = [linea[2],linea[3]]
            unix= linea[0].split(' ')
            fecha = unix[0]
            cercano: bool = dentroDeLaDistancia(river_loc,coord,1)
            if cercano:
                print(f"Se realizó un reclamo para la patente (ingresar pat) el día {fecha} en (ingresal loc)")#falta completar info
    print("Listando reclamos a 1 Km. del estadio Boca Juniors")
    for linea in datos_reclamos:
        if linea != datos_reclamos[0]:
            coord = [linea[2],linea[3]]
            unix= linea[0].split(' ')
            fecha = unix[0]
            cercano = dentroDeLaDistancia(boca_loc,coord,1)
            if cercano:
                print(f"Se realizó un reclamo para la patente el día {fecha} en")#falta completar info
    print("Listando reclamos en el centro de la ciudad")
    for linea in datos_reclamos:
        if linea != datos_reclamos[0]:
            coord = [linea[2],linea[3]]
            unix= linea[0].split(' ')
            fecha = unix[0]
            cercano = dentroDelCuadrante(coord)#Aprovechando un bool ya definido
            if cercano:
                print(f"Se realizó un reclamo para la patente el día {fecha} en el centro de CABA")#falta completar informacion de la patente
    print("Buscando autos sospechosos")
    robados_patentes: list = leer_txt()
    for reclamo in datos_reclamos_nuevo:
        if reclamo[5] in robados_patentes:
            print(f'ALERTA, el auto con patente {reclamo[5]} tiene un pedido de caputra')
            print(f'Su posible ubicación es {reclamo[2]} en {reclamo[3]}, {reclamo[4]}')
    
    print("Generando grafico de reclamos mensuales")
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
main()

    
    
