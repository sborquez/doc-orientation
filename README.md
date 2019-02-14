# Doc orientation webservice

web service para la orientacion de documentos.

Implementado con flask, pytesseract y dockers.

## Requests

GET /

Respuesta:
> :heavy_check_mark: "Up and Running!"

POST /image/ 

Post data: 
* file: image (binary data)

Respuestas:

> :heavy_check_mark: Imagen orientada (binary data)

> :heavy_multiplication_x: Imagen_original (binary data)

> :heavy_multiplication_x: "Se requiere una imagen en el post"

POST /zip/

Post data:
* file: .zip (binary data)

> :heavy_check_mark: zip con imagenes orientadas (binary data)

> :heavy_multiplication_x: "Se requiere un .zip en el post"


## Ejemplos una imagen

### [httpie](https://httpie.org/)

```
http -f POST http://0.0.0.0:8000/image/ file@/path/to/image.JPEG > path/to/out/image.JPEG
```

### C#
```csharp
var client = new RestClient("http://0.0.0.0:8000/image/");
var request = new RestRequest(Method.POST);
request.AddHeader("Postman-Token", "a673af4a-ae13-4cb2-926e-e923045e96ee");
request.AddHeader("cache-control", "no-cache");
request.AddHeader("Content-Type", "application/x-www-form-urlencoded");
request.AddHeader("content-type", "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW");
request.AddParameter("multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW", "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"file\"; filename=\"/path/to/image.JPEG\"\r\nContent-Type: image/jpeg\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```

## Ejemplos zip con imagenes

### [httpie](https://httpie.org/)

```
http -f POST http://0.0.0.0:8000/zip/ file@/path/to/images.zip > path/to/out/images.zip
```

### C#
```csharp
var client = new RestClient("http://0.0.0.0:8000/zip/");
var request = new RestRequest(Method.POST);
request.AddHeader("Postman-Token", "3aecb473-f316-44bf-8d94-8bf66df28d73");
request.AddHeader("cache-control", "no-cache");
request.AddHeader("Content-Type", "application/x-www-form-urlencoded");
request.AddHeader("content-type", "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW");
request.AddParameter("multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW", "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"file\"; filename=\"/path/to/images.zip\"\r\nContent-Type: application/zip\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--", ParameterType.RequestBody);
IRestResponse response = client.Execute(request);
```