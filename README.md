# Doc orientation webservice

web service para la orientacion de documentos.

Implementado con flask, pytesseract y dockers.

## Requests

GET /

Respuesta:
> :heavy_check_mark: "Up and Running!"

POST /doc/ 

Post data: 
* file: image (binary data)

Respuestas:

> :heavy_check_mark: Imagen orientada (binary data)

> :heavy_multiplication_x: Imagen original (binary data)

> :heavy_multiplication_x: "Se requiere una imagen en el post"


## Ejemplo

### [httpie](https://httpie.org/)

http -f POST http://localhost:8000/doc/ file@/path/to/image.JPEG > path/to/out/image.JPEG
