import speech_recognition as sr
import csv
import matplotlib.pyplot as plt
from matplotlib.image import imread
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
import folium
import webbrowser
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
def leerArchivo(nom_arc:str,lista:list,separador:str):
    """
Pre: Require el nombre del archivo como str y una lista vacia donde guardar los datos
Post: Al ser un procedimiento no posee, guarda los datos leído del archivo en una lista vacía
"""
    try:
        file = open(nom_arc,'r',encoding = "UTF-8")
        for linea in file:
            registro = []
            linea = linea.strip()
            registro = linea.split(separador)
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
def compararDatos(datos1:list,datos2:list)->list:
    """
Pre: Requiere dos listas, la primera es una general, la segunda es especifica.
Post: Devuelve una lista que posee los datos en comun que tiene la primera lista con la segunda.
"""
    elementos_en_comun:list = []
    for x in range(len(datos1)):
        if datos1[x][5] in datos2:
            coincidentes = datos1[x][5]
            elementos_en_comun.append(coincidentes)
    return elementos_en_comun
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
#mostrar foto y mapa
def mostrarImg(ruta:str):
    """
Pre: Requiere la ruta de la img a mostrar
Post: Es un procedimiento que muestra en pantalle una imagen
"""
    #archivo = 'prueba.jpg'
    #directorio = os.getcwd()
    #ruta = os.path.join(directorio, archivo)
    img = mpimg.imread(ruta)
    imgplot = plt.imshow(img)
    plt.show()
def mostrarMapa(coordenada:list,patente:str):
    """
Pre: Requiere las coordenadas a mostrar y una decripcion de una o dos palabrar sobre dicha coordenada
Post: Traza un mapa, e inserta en el un puntero en la localizacion de las coordenadas ingresadas,luego abre dicho mapa en el navegador
"""
    ubicacion: list = [float(coordenada[0]),float(coordenada[1])]
    mapa=folium.Map(location=ubicacion)
    mapa.add_child(folium.Marker(location=ubicacion,popup=patente,icon=folium.Icon(color='green')))
    mapa.save('mapa.html')
    archivo = 'mapa.html'
    directorio = os.getcwd()
    ruta = os.path.join(directorio, archivo)#El archivo se crea automaticamente y se guarda en la misma carpeta del presente programa
    webbrowser.open(ruta)
def mostrarDatosPatente(archivo1:list,archivo2:list):
    time: str = ''
    tel:str = ''
    ruta_foto: str = ''
    coord: list = []
    patente: str = input("Ingrese la pantente a consultar: ")
    for line in archivo2:
        if patente in line:
            time = line[0]
            tel = line[1]
    for line in archivo1:
        if time in line and tel in line:
            ruta_foto = line[4]
            coord = [line[2],line[3]]
    print("Para el movil de patente: ",patente)
    print("Se encuentrar asociados: ")
    print("Su imagen: ")
    mostrarImg(ruta_foto)
    print("Su mapa: ")
    mostrarMapa(coord,patente)
#mostrar grafico

def main()->None:
    datos_reclamos: list = []
    datos_reclamos_nuevo: list = []
    pedido_captura: list = []
    reclamos: str = 'reclamosad.csv'
    captura: str = 'robados.txt'
    leerArchivo(reclamos,datos_reclamos,';')
    leerArchivo(captura,pedido_captura,',')
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
    print("Alertas de patentes con pedidos de captura")
    sospechosos: list = compararDatos(pedido_captura,datos_reclamos_nuevo) #Falta probar
    infoAlerta(sospechosos,datos_reclamos_nuevo) #falta informacion para probar la funcion
    print("Ingresar una patente y obtener su imagen y ubicacion en un mapa")
    mostrarDatosPatente(datos_reclamos,datos_reclamos_nuevo)#pendiente por comprobar que funciona
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

    
    
