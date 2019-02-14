from flask import Flask, request, send_file
from os import path, environ, listdir, rename, remove
from shutil import rmtree
from pytesseract import image_to_osd, Output, TesseractError
import uuid
import zipfile
from io import BytesIO
import logging

try:
    from PIL import Image
except ImportError:
    import Image

app = Flask(__name__)

def apply_orientation_correction(image_name, image_path, target_size=1800, retry=False):
    """
    apply_orientation_correction aplica a la imagen la deteccion de orientacion
    y la aplicacion de la correccion.
    """
    try:
        image = Image.open(image_path)
    except OSError:
        app.logger.error(f"No se puede leer la imagen: {image_name}")
        image_name, image_path, False
    W, H = image.size
    if W > H:
        r = target_size/W
    else:
        r = target_size/H
    image_resized = image.resize((int(W*r), int(H*r)))
    try:
        result = image_to_osd(image_resized, lang="spa", output_type=Output.DICT)
    except TesseractError:
        if not retry:
            app.logger.info("Ocurrio un error por la resulucion de la imagen, reintentando...")
            apply_orientation_correction(image_name, image_path, target_size=2000, retry=True)
        else:
            app.logger.info(f"No se pudo determinar orientacion de imagen: {image_name}")
            image_name, image_path, False
    else:
        app.logger.info(f"Imagen: {image_name}\tOrientacion: {result['orientation']}\tRotacion: {result['rotate']}")
        rotated_image = image.rotate(-result["rotate"], expand=True)
        rotated_image.save(image_path)

    return image_name, image_path, True

def save_file(file, folder):
    """
    Guarda un archivo en el directorio especificado
    folder debe ser en relacion a ROOT y terminar con trailing slash
    ejemplo: folder = '/temp/'
    file debe ser un archivo rescatado desde el request
    ejemplo: file = request.files['file']
    Devuelve el nombre del archivo y el path completo al archivo
    """
    orig_filename = file.filename
    uid = uuid.uuid4().hex[:10]
    name, ext = path.splitext(orig_filename)

    # Genera un uuid unico para no generar colisiones con instantias con el mismo nombre
    temp_filename = f"{name}-{uid}{ext}"

    tempfile_path = path.join(folder, temp_filename)
    file.save(tempfile_path)

    app.logger.info(f"File: {orig_filename}")
    return orig_filename, tempfile_path 

def extract_zip(fullpath):
    """
    Funcion que extrae un arhivo zip conociendo el fullpath y deja su contenido en folder.
    Además elimina el archivo original.
    """
    # EXTRAER EL NOMBRE DEL ARCHIVO PARA GENERAR CARPETA
    temp_zip_folder = path.splitext(fullpath)[0]

    # EXTRAER LOS ARCHIVOS DEL ZIP
    with zipfile.ZipFile(fullpath, 'r') as zip_ref:
        zip_ref.extractall(temp_zip_folder)

    # ARCHIVOS EXTRAIRDOS
    imgs_path = [path.join(temp_zip_folder, img_path) for img_path in listdir(temp_zip_folder)]

    return temp_zip_folder, imgs_path

def compress_folder_content(folder):
	"""
	Comprime todos los archivos de una carpeta en un unico zip y devuelve el archivo en memoria.	
	"""
	files = listdir(folder)
	memory_file = BytesIO()
	with zipfile.ZipFile(memory_file, 'w') as zf:
		for file in files:
			filepath = path.join(folder, file)
			zf.write(filepath, arcname=file)
	memory_file.seek(0)
	return memory_file

def clean(path_file):
    """
    clean elimina los archivos temporales creados.
    """
    app.logger.info(f"Deleting: {path_file}")
    if path.isdir(path_file):
        rmtree(path_file)
    else:
        remove(path_file)

@app.route("/")
def hello():
	return "Up and Running!"


@app.route('/image/', methods=['POST'])
def doc_orientation():
    """
    doc_orientation recibe una imagen de un documento, determina su orientacion,
    la gira para que quede orientada en 0 grados y la envia como respuesta.
    """
    # SE VERIFICA QUE EL ARCHIVO VENGA EN EL REQUEST
    if 'file' not in request.files:
        app.logger.error("POST no contiene imagen")
        return "Se requiere una imagen en el post"
    
    # GUARDAR EL ARCHIVO EN UNA CARPETA TEMPORAL
    temp_folder = '/tmp/'
    orig_file_name, temp_file = save_file(request.files['file'], temp_folder)
    
    # SE APLICA LA CORRECCION
    new_file_name, new_file_path, success = apply_orientation_correction(orig_file_name, temp_file)
    if not success:
        name, ext = path.splitext(new_file_name)
        new_file_name = name + "_original" + ext
        # PREPARAR RESPUESTA
        respond = send_file(new_file_path, attachment_filename=new_file_name, as_attachment=True)
    else:
        # PREPARAR RESPUESTA
        respond = send_file(new_file_path, attachment_filename=new_file_name, as_attachment=True)

    # ELIMINAR ARCHIVOS ORIGINALES
    clean(new_file_path)

    # ENVIAR RESULTADO
    return respond

@app.route('/zip/', methods=['POST'])
def zip_orientation():
    """
    zip_orientation recibe un .zip de imagenes de documentos, determina su orientacion,
    las gira para que quede orientada en 0 grados y envia un .zip como respuesta.
    """
    # SE VERIFICA QUE EL ARCHIVO VENGA EN EL REQUEST
    if 'file' not in request.files:
        app.logger.error("POST no contiene .zip")
        return "Se requiere un .zip en el post"
    
    # GUARDAR EL ARCHIVO EN UNA CARPETA TEMPORAL
    temp_folder = '/tmp/'
    orig_file_name, temp_file = save_file(request.files['file'], temp_folder)
    
    # SE CORROBORA QUE ES UN ARCHIVO ZIP
    if path.splitext(temp_file)[1] not in (".zip", ".ZIP"):
        app.logger.error("POST no contiene .zip")
        return "Se requiere un .zip en el post"

    # SE EXTRAE EL ARCHIVO ZIP
    temp_zip_folder, imgs_path = extract_zip(temp_file)

    # APLICAR LA CORRECCION
    for img_path in imgs_path:
        img_file_name = path.basename(img_path)
        new_img_file_name, new_img_path, success = apply_orientation_correction(img_file_name, img_path)
        if not success:
            # Agregar que imagen es la original
            name, ext = path.splitext(new_img_path)
            rename(new_img_path, name + "_original" + ext)
    
    # PREPARAR RESPUESTA    
    memory_file = compress_folder_content(temp_zip_folder)
    respond = send_file(memory_file, attachment_filename=orig_file_name, as_attachment=True)

    # ELIMINAR ARCHIVOS ORIGINALES
    clean(temp_file)
    clean(temp_zip_folder)

    # ENVIAR RESULTADO
    return respond

if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == "__main__":
    port = int(environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
