#!/bin/bash

if [ $# -eq 0 ]; then
  echo "Se necesita ruta a la carpeta con .zip's"
  exit 1
fi

directory=$1
if [ ! -d "$directory" ]; then
  echo "$directory no es un directorio"
fi

rm -rf ./out
rm -rf ./tmp

mkdir ./tmp
mkdir ./out

for test_file in $directory/*.zip; do 
  echo "Probando archivo ${test_file##*/}"
  tmp="./tmp/${test_file##*/}"
  out="./out/${test_file##*/}"
  echo "Convirtiendo a jpeg..."
  http -f POST http://tiff-a-jpg-s4b.eastus2.azurecontainer.io:8000/tiff2jpeg/ file@$test_file > $tmp
  echo "Aplicando correccion de orientacion..."
  http --timeout=300 -f POST http://0.0.0.0:8000/zip/ file@$tmp > $out
done
rm -rf ./tmp
