from flask import Flask, request, send_file
from os import path, remove, environ
from pytesseract import image_to_osd, Output, TesseractError
import uuid

try:
    from PIL import Image
except ImportError:
    import Image


def apply_orientation_correction(image_name, image_path, target_size=1800, retry=False):
    """
    apply_orientation_correction aplica a la imagen la deteccion de orientacion
    y la aplicacion de la correccion.
    """
    image = Image.open(image_path)
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
            print("[INFO] Ocurrio un error por la resulucion de la imagen, reintentando...")
            apply_orientation_correction(image_name, image_path, target_size=2000, retry=True)
        else:
            image_name, image_path, False
    else:
        print(f"[INFO] Image orientation {result['orientation']}, rotation {result['rotate']}")
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
    temp_filename = f"{name}-{uid}{ext}"

    tempfile_path = path.join(folder, temp_filename)
    file.save(tempfile_path)

    print(f"[INFO] Image: {orig_filename}")
    return orig_filename, tempfile_path 

def clean(file):
    """
    clean elimina los archivos temporales creados.
    """
    print("[INFO] Deleting:", file)
    remove(file)

app = Flask(__name__)


@app.route("/")
def hello():
	return "Up and Running!"


@app.route('/doc/', methods=['POST'])
def doc_orientation():
    """
    doc_orientation recibe una imagen de un documento, determina su orientacion,
    la gira para que quede orientada en 0 grados y la envia como respuesta.
    """
    # SE VERIFICA QUE EL ARCHIVO VENGA EN EL REQUEST
    if 'file' not in request.files:
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
    

if __name__ == "__main__":
    port = int(environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
