import speech_recognition as sr
import csv
import matplotlib.pyplot as plt
from matplotlib.image import imread
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from geopy.point import Point
import os
import folium
import webbrowser
# Librerías para la detección de patente
import cv2
import imutils
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\54113\AppData\Local\Tesseract-OCR\tesseract.exe'

# CONSTANTES
RECLAMOS: str = 'reclamosad.csv'
CAPTURA: str = 'robados.txt'
RIVER_LOC: list = ['-34.545173623765045','-58.44980708914722']
BOCA_LOC:list = ['-34.63547846773916','-58.36471338729659']
MESES: list = ["Enero", "Febrero", "Marzo", "Abril", 
    "Mayo", "Junio", "Julio", "Agosto", "Septiembre",
    "Octubre", "Noviembre", "Diciembre" ]

# Detectar y escribir patente
def detectar_patente(ruta_img: str)-> str:
    """ Pre: requiere la ruta absoluta de la imágen a analizar como argumento
        post: devuelve el número de patente en formato str
    """
    # Optimizacion de imagen para detectar patente
    img = cv2.imread(ruta_img,cv2.IMREAD_COLOR)
    # img = cv2.resize(img, (600,400))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    gray = cv2.bilateralFilter(gray, 13, 15, 15) 

    edged = cv2.Canny(gray, 30, 200) 
    contours = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
    screenCnt = None

    for c in contours:
        
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
    
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        detected = 0
        print ("No contour detected")
        print(f"No se ha podido detectar la patente de la foto {ruta_img}.")
        return "No detectado"
    else:
        detected = 1

    if detected == 1:
        cv2.drawContours(img, [screenCnt], -1, (0, 0, 255), 3)

    # Segmentación de caracteres
    mask = np.zeros(gray.shape,np.uint8)
    new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
    new_image = cv2.bitwise_and(img,img,mask=mask)

    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    Cropped = gray[topx:bottomx+1, topy:bottomy+1]
    
    # Análisis de caracteres segmentados
    text = pytesseract.image_to_string(Cropped, config='--psm 11')
    print("El número de patente detectado es: ",text)
    img = cv2.resize(img,(500,300))
    Cropped = cv2.resize(Cropped,(400,200))
    # cv2.imshow('car',img)
    # cv2.imshow('Cropped',Cropped)

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return text

def transcrpicion_audio(ruta_audio: str)->str:
    """
    Pre: Require la ruta absoluta de un audio en formato wav
    Post: Devuelve la trancricion del audio como str
    """
    r = sr.Recognizer()
    transcripcion: str = ""
    try:
        with sr.AudioFile(ruta_audio) as source:
            audio = r.record(source)
        transcripcion = r.recognize_google(audio, language = 'es')
    except FileNotFoundError:
        transcripcion="Reclamo sin audio"
    except sr.UnknownValueError:
        transcripcion= "Google Speech Recognition no pudo entender el audio"
    except sr.RequestError as e:
        transcripcion ="No se pudieron solicitar los resultados de Google Speech Recognition service; {0}".format
    return transcripcion

# Archivos
def leerArchivo(nom_arc:str,separador:str)->list:
    """
    Pre: Require el nombre del archivo como str y el caracter de serparacion como str
    Post: Al ser un procedimiento no posee, guarda los datos leído del archivo en una lista vacía
    """
    try:
        file = open(nom_arc,'r',encoding = "UTF-8")
        lista: list = list()

        for linea in file:
            registro = []
            linea = linea.strip()
            registro = linea.split(separador)
            lista.append(registro)
            
        file.close()
    except IOError:
        print("Se producjo un error de entrada y salida del archivo")
    return lista

def crear_csv(reclamos_datos_nuevos: list)->None:
    """
    Pre: Require un lista con los datos de los reclamos ya procesados
    Post: Al ser un procedimiento no posee, crea un archivo csv con eso datos.
    """
    with open("reclamos_nuevo.csv", 'w', newline='', encoding="UTF-8") as reclamos:
        csv_writer = csv.writer(reclamos, delimiter=',', quotechar='"', quoting= csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(["Timestamp", "Telefono", "Direccion", "Localidad", "Provincia", "Patente", "Descripcion texto", "Descripcion audio"])
        
        for reclamo in reclamos_datos_nuevos:
            csv_writer.writerow(reclamo)

# Geopy
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
    prov: str = ""
    if ubicarl[4] in comunas: 
        localidad = ubicarl[4]
        prov = 'CABA'
    elif ubicarl[5] in comunas:
        localidad = ubicarl[5]
        prov = 'CABA'
    else:
        prov = "Fuera de CABA"

    datos: list = [calle,localidad,prov]

    return datos
    
def dentroDeLaDistancia(direcc1:list,direcc2:list,distan:int)->bool:
    """
    Pre: ingresas dos direcciones en forma de lista con dos elementos string, y el radio un int
    Post: retorna un bool que indica si las direcciones poseen una distancia menor o igual a la indicada en el radio
    """
    dist = geodesic(direcc1,direcc2).km
    esta_dentro_de_la_distancia: bool = dist<=distan
    return esta_dentro_de_la_distancia

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

def compararDatos(datos1:list,datos2:list)->list:
    """
    Pre: Requiere dos listas, la primera es una general, la segunda es especifica.
    Post: Devuelve una lista que posee los datos en comun que tiene la primera lista con la segunda.
    """
    elementos_en_comun:list = []

    for x in range(len(datos2)):
        if datos2[x][5] in datos1:
            coincidentes = datos2[x][5]
            elementos_en_comun.append(coincidentes)

    return elementos_en_comun

def listarReclamos(datos_reclamos: list, datos_reclamos_nuevo: list, locacion: str)->None:
    for i in range(len(datos_reclamos) - 1):
        linea: list = datos_reclamos[i]

        if linea != datos_reclamos[0]:
            coord: list = [linea[2],linea[3]]
            unix: list = linea[0].split(' ')
            fecha:str = unix[0]
            direcc: str = datos_reclamos_nuevo[i][2]
            prov: str = datos_reclamos_nuevo[i][4]
            cercano: bool = dentroDeLaDistancia(locacion,coord,1)
            if cercano:
                print(f"Se realizó un reclamo para la patente {datos_reclamos_nuevo[i][5]} el día {fecha} en {direcc},{prov}")

def listarReclamosCentro(datos_reclamos: list, datos_reclamos_nuevo: list)-> None:
    for i in range(len(datos_reclamos)):
        linea = datos_reclamos[i]

        if linea != datos_reclamos[0]:
            coord = [linea[2],linea[3]]
            unix= linea[0].split(' ')
            fecha = unix[0]
            cuadrante: bool = dentroDelCuadrante(coord)

            if cuadrante:
                print(f"Se realizó un reclamo para la patente {datos_reclamos_nuevo[i][5]} el día {fecha} en el centro de CABA")

# Mostrar resultados en pantalla
def mostrarAlerta(pat:str,tiempo:str,ubicacion:list):
    """
    Pre: Requiete la patente como str, la fecha como str, y una lista con direccion, localidad, provincia
    Post: Imprime un cartel en la terminal en color rojo, con una alerta
    """
    c:str = "—"*77
    print("\033[0;31m"+c+"\033[0;m")
    print("\033[0;31m"+"ALERTA"+"\033[0;m")
    print("El día: ",tiempo)
    print(f'Su ubicación es {ubicacion[0]} en {ubicacion[1]}, {ubicacion[2]}')
    print(f"El movil con patente {pat},tiene un pedido de captura ")
    print("\033[0;31m"+c+"\033[0;m")

def infoAlerta(lista_robados:list,info_file:list):
    """
    Pre: Requiere una lista con las patentes coincidentes con el pedido de captura, y requiere los datos procesados de las denuncias
    Post:  Es un procedimiento que imprime en pantalla como alerta los datos de todas la denucias correspondientes a una patente con pedido de captura 
    """
    fechas: list = []
    ubicaciones: list = []

    for i in range(len(info_file)):

        for j in range(len(lista_robados)):
            if info_file[i][5]==lista_robados[j]:
                ubic: list = [info_file[i][2],info_file[i][3],info_file[i][4]]
                unix= info_file[i][0].split(' ')
                fecha = unix[0]
                fechas.append(fecha)
                ubicaciones.append(ubic)

    for i in range(len(lista_robados)):
        patente: str = lista_robados[i]
        time: str = fechas[i]
        ubicacion: list = ubicaciones[i]
        mostrarAlerta(patente,time,ubicacion)

def mostrarImg(rutai:str):
    """
    Pre: Requiere la ruta de la img a mostrar
    Post: Es un procedimiento que muestra en pantalle una imagen
    """
    ruta = os.path.abspath(rutai)
    img = imread(ruta)
    imgplot = plt.imshow(img)
    plt.show()

def mostrarMapa(coordenada:list,patente:str):
    """
    Pre: Requiere las coordenadas a mostrar y una decripcion de una o dos palabrar sobre dicha coordenada
    Post: Traza un mapa, e inserta en el un puntero en la localizacion de las coordenadas ingresadas,luego abre dicho mapa en el navegador
    """
    print("Entrando a MOSTRAR MAPA")
    ubicacion: list = [float(coordenada[0]),float(coordenada[1])]
    mapa=folium.Map(location=ubicacion)
    mapa.add_child(folium.Marker(location=ubicacion,popup=patente,icon=folium.Icon(color='green')))
    mapa.save('mapa.html')
    archivo = 'mapa.html'
    directorio = os.getcwd()
    ruta = os.path.join(directorio, archivo) # El archivo se crea automaticamente y se guarda en la misma carpeta del presente programa
    webbrowser.open(ruta)

def mostrarDatosPatente(datos_reclamos:list, datos_reclamos_nuevo:list):
    time: str = ''
    tel:str = ''
    ruta_foto: str = ''
    coord: list = []
    patente: str = input("Ingrese la pantente a consultar: ")

    for line in datos_reclamos_nuevo:
        if patente in line:
            time = line[0]
            tel = line[1]

    for line in datos_reclamos:
        if time in line and tel in line:
            ruta_foto = line[4]
            coord = [line[2],line[3]]
    

    print("Para el movil de patente: ",patente)
    print("Se encuentra asociado: ")
    print("Su imagen: ")
    mostrarImg(ruta_foto)
    print("Su mapa: ")
    mostrarMapa(coord,patente)

def reclamosMensuales(datos: list)->list:
    cantxmeses: list = []

    for mes in range (1,13):
        cantxmes: int = 0
        for reclamo in datos:
            if mes ==  int(reclamo[0][5:7]):
                cantxmes += 1
        cantxmeses.append(cantxmes)
    return cantxmeses

def graficoMetricas(cantxmeses: list, MESES:list):
    fig, ax = plt.subplots()
    ax.bar(MESES, cantxmeses)
    plt.show()

def main()->None:
    datos_reclamos: list = leerArchivo(RECLAMOS,';')
    pedido_captura: list = leerArchivo(CAPTURA,'\n')   
    datos_reclamos_nuevo: list = []

    print("Creando nuevo listado")
    print("Inicio de programa")
    print("Prosesado datos y generando nuevo archivo fortmato csv")

    for reclamo in datos_reclamos:
        # (Timestamp, Teléfono_celular, coord_latitud, coord_long, ruta_foto, descripción texto,ruta_audio)
        if reclamo != datos_reclamos[0]:
            ubicacion: list = coordenadasADireccion(reclamo[2],reclamo[3])
            patente: str = detectar_patente(os.path.abspath(reclamo[4]))
            descripcion_audio: str = transcrpicion_audio(os.path.abspath(reclamo[6]))
            datos_reclamos_nuevo.append([reclamo[0],reclamo[1],ubicacion[0], ubicacion[1], ubicacion[2], patente.rstrip(), reclamo[5], descripcion_audio])
    crear_csv(datos_reclamos_nuevo)

    print("Listando reclamos a 1 Km. del estadio River Plate ")
    listarReclamos(datos_reclamos, datos_reclamos_nuevo, RIVER_LOC)

    print("Listando reclamos a 1 Km. del estadio Boca Juniors")
    listarReclamos(datos_reclamos, datos_reclamos_nuevo, BOCA_LOC)

    print("Listando reclamos en el centro de la ciudad")
    listarReclamosCentro(datos_reclamos, datos_reclamos_nuevo)

    print("Alertas de patentes con pedidos de captura")
    sospechosos: list = compararDatos(pedido_captura,datos_reclamos_nuevo) 
    infoAlerta(sospechosos,datos_reclamos_nuevo) 
    print("Ingresar una patente y obtener su imagen y ubicacion en un mapa")
    mostrarDatosPatente(datos_reclamos,datos_reclamos_nuevo)
    print("Generando grafico de reclamos mensuales")

    cantxmeses: list = reclamosMensuales(datos_reclamos_nuevo)
    graficoMetricas(cantxmeses, MESES)

main()

    
    

    
