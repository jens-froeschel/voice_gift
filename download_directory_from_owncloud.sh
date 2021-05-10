set -eux

link_id=$1

mkdir -p audiofiles

pushd audiofiles
wget --no-check-certificate --content-disposition -O audiofiles.zip "https://owncloud.fraunhofer.de/public.php?service=files&t=${link_id}&download"
unzip -j audiofiles.zip
rm audiofiles.zip
popd


bash normalize_audiofiles.sh
