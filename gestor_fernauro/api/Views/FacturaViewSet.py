import os

import numpy as np
from django.core.cache import cache
from django.db.models import Avg, Sum
from django.http import HttpResponse
from PIL import Image
from rest_framework import request, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import Token

from ..Decorators.Actions import FacturaDecorator
from ..Models.FacturaModel import Factura
from ..Permissions.permissions import IsAdminUser, IsNormalUser
from ..Serializers.FacturaSerializer import FacturaSerializer


class FacturaViewSet(viewsets.ModelViewSet,
                     FacturaDecorator):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    cache_key = ''
    # permission_classes = [IsNormalUser]

    # Funcion para listar las facturas existentes
    def list(self,request,*args,**kwargs):
        facturas = cache.get(self.cache_key)
        serializer = None

        if not facturas:
            # Obtenemos todas las facturas
            facturas = Factura.objects.all()

            # Convertimos a formatos json las facturas
            serializer = self.get_serializer(facturas, many=True)

            # Guardamos los datos en la cache durante 10 minutos
            cache.set(self.cache_key, facturas, timeout=60 * 10)
            print("Guardamos los datos en la cache ")

        # Si facturas ya estaba en caché, asignamos el serializer
        if serializer is None:
            serializer = self.get_serializer(facturas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Sobreescribimos el método post que ya viene definido por django
    def create(self, request, *args, **kwargs):
        # Serializar los datos de la solicitud
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        factura = serializer.save()

        # Intentar obtener las facturas desde la caché
        cached_facturas = cache.get(self.cache_key)

        if cached_facturas:
            # Si las facturas están en caché, agregamos la nueva factura
            cached_facturas.append(serializer.data)
            cache.set(self.cache_key, cached_facturas, timeout=60 * 10)
            print("Caché actualizada con la nueva factura.")
        else:
            # Si la caché está vacía, obtenemos todas las facturas de la base de datos
            all_facturas = Factura.objects.all()
            all_facturas_data = FacturaSerializer(all_facturas, many=True).data
            cache.set(self.cache_key, all_facturas_data, timeout=60 * 10)
            print("Caché regenerada después de crear una factura.")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    '''
        Método para sellar imagenes lo cual es muy útil para empresas 
    '''
    @action(detail=False, methods=['post'])
    def mergue_images(self, request):
        imagen_1 = request.FILES.get('imagen_1')
        sello = request.FILES.get('sello')

        try:
            # Abrir las imágenes usando PIL (usamos Image.open() en lugar de .convert())
            imagen_1 = Image.open(imagen_1)
            sello = Image.open(sello)

            # Convertir ambas imágenes a RGBA para asegurarse de que tienen un canal alfa
            imagen_1 = imagen_1.convert('RGBA')
            sello = sello.convert('RGBA')

            # Redimensionar el sello
            imagen_sello = sello.resize((300, 300))

            # Calcular la posición donde colocar el sello en la imagen base
            posicion_sello = (imagen_1.width - imagen_sello.width - 10, imagen_1.height - imagen_sello.height - 10)

            imagen_1.paste(imagen_sello, posicion_sello, imagen_sello)

            ruta_guardado = os.path.join('media/imagenes_combinadas', 'imagen_combinada.png')

            response = HttpResponse(content_type='image/png')

            imagen_1.save(response, 'PNG')

            os.makedirs(os.path.dirname(ruta_guardado), exist_ok=True)

            imagen_1.save(ruta_guardado, 'PNG')

            return response

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['get'])
    def suma_total(self,request):
        # Mediante la siguiente línea de código, calculamos la suma total de todas las facturas
        facturas_totales = (Factura.objects
                            .aggregate(total=Sum('total')))

        return Response(facturas_totales, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def media_total(self,request):
        # A continuación, calculamos la media de los totales de todas las facturas ya que usamos el método agregate
        facturas_totales = (Factura.objects
                            .aggregate(media=Avg('total')))

        return Response(facturas_totales, status=status.HTTP_200_OK)


















    '''
    @action(detail=False, methods=['post'])
    def pixelar_rostros(self, request):
        imagen = request.FILES.get('imagen')

        try:
            # Cargar la imagen con PIL y convertirla a formato OpenCV
            imagen_pil = Image.open(imagen).convert('RGB')
            imagen_cv = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)

            # 1. Detectar rostros usando Haar Cascade
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            gray = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2GRAY)
            rostros = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            # 2. Pixelar cada rostro detectado
            for (x, y, w, h) in rostros:
                roi = imagen_cv[y:y + h, x:x + w]  # Región de interés (rostro)

                # Reducir la resolución y escalar para crear efecto pixelado
                pixelacion = 0.008  # A menor valor, más pixelado
                ancho_pixel = int(w * pixelacion)
                alto_pixel = int(h * pixelacion)

                if ancho_pixel > 0 and alto_pixel > 0:
                    # Redimensionar a baja resolución
                    roi_pequeno = cv2.resize(roi, (ancho_pixel, alto_pixel), interpolation=cv2.INTER_LINEAR)
                    # Escalar de vuelta al tamaño original
                    roi_pixelado = cv2.resize(roi_pequeno, (w, h), interpolation=cv2.INTER_NEAREST)
                    # Reemplazar el ROI original con el pixelado
                    imagen_cv[y:y + h, x:x + w] = roi_pixelado

            # Convertir de OpenCV a PIL y guardar
            imagen_pixelada_pil = Image.fromarray(cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2RGB))

            # Devolver la imagen procesada
            response = HttpResponse(content_type='image/jpeg')
            imagen_pixelada_pil.save(response, 'JPEG')
            return response

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=False, methods=['post'])
    def pixelar_rostros_jovenes(self, request):
        imagen = request.FILES.get('imagen')

        try:
            # Cargar la imagen con PIL y convertirla a formato OpenCV
            imagen_pil = Image.open(imagen).convert('RGB')
            imagen_cv = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)

            # 1. Detectar rostros usando Haar Cascade
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            gray = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2GRAY)
            rostros = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            # 2. Pixelar los rostros de personas jóvenes
            for (x, y, w, h) in rostros:
                rostro = imagen_cv[y:y + h, x:x + w]  # Región de interés (rostro)

                # Usar DeepFace para predecir la edad, con enforce_detection=False
                try:
                    resultado = DeepFace.analyze(rostro, actions=['age'], enforce_detection=False)
                    edad = resultado[0]['age']

                    # Si la persona es joven (por ejemplo, menos de 18 años), pixelar el rostro
                    if edad < 18:
                        # Reducir la resolución y escalar para crear el efecto pixelado
                        pixelacion = 0.08 # A menor valor, más pixelado
                        ancho_pixel = int(w * pixelacion)
                        alto_pixel = int(h * pixelacion)

                        if ancho_pixel > 0 and alto_pixel > 0:
                            # Redimensionar a baja resolución
                            roi_pequeno = cv2.resize(rostro, (ancho_pixel, alto_pixel), interpolation=cv2.INTER_LINEAR)
                            # Escalar de vuelta al tamaño original
                            roi_pixelado = cv2.resize(roi_pequeno, (w, h), interpolation=cv2.INTER_NEAREST)
                            # Reemplazar el ROI original con el pixelado
                            imagen_cv[y:y + h, x:x + w] = roi_pixelado

                except Exception as e:
                    print(f"Error al analizar la edad: {e}")

            # Convertir de OpenCV a PIL y guardar
            imagen_pixelada_pil = Image.fromarray(cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2RGB))

            # Devolver la imagen procesada
            response = HttpResponse(content_type='image/jpeg')
            imagen_pixelada_pil.save(response, 'JPEG')
            return response

        except Exception as e:
            return Response({'error': str(e)}, status=400)    
    '''
