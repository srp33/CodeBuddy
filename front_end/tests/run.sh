#! /bin/bash

set -o errexit

currentDir="$(pwd)"
tmpDir=/tmp/codebuddy_front_end_tests

rm -rf $tmpDir
mkdir -p $tmpDir

image_name=codebuddy/front_end_tests

cp Containerfile $tmpDir/
cp ../requirements.txt $tmpDir/
cp ../../Settings.yaml $tmpDir/
cp ../../VERSION $tmpDir/
cp build_test_scripts.py $tmpDir/
cp start_web_server_code.py $tmpDir/
cp create_database.py $tmpDir/
cp -r ../build_html.sh $tmpDir/
cp handler_tests.dat $tmpDir/

mkdir $tmpDir/migration_scripts
for f in ../migration_scripts/*
do
    echo "Tweaking $f"
    python3 tweak_migration_script.py $f $tmpDir/migration_scripts/$(basename $f)
done

cp -r ../../back_ends $tmpDir/
cp -r ../query_templates $tmpDir/
cp -r ../secrets $tmpDir/
cp -r ../server $tmpDir/
python3 remove_lines_starting_with.py ../server/ui_methods.py "from " $tmpDir/ui_methods.py
cp -r ../templates $tmpDir/
mkdir $tmpDir/database $tmpDir/logs

cd ..

bash build_html.sh server/html
cp -r server/html/* $tmpDir/

cd $tmpDir

docker build -t ${image_name}:latest \
             -f Containerfile \
             --build-arg USER_ID=$(id -u ${USER}) \
             --build-arg GROUP_ID=$(id -g ${USER}) \
             .

docker run -i -t --rm \
    -v "${tmpDir}":/app \
    --user $(id -u):$(id -g) \
    ${image_name}:latest \
    bash -c "python3 build_test_scripts.py;python3 -m unittest test_app"

rm -rf $tmpDir
