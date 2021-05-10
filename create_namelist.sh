set -eu

mv names.txt names.txt.bak

for f in audiofiles/*; do
    filename=$(basename -- "$f")
    filename="${filename%.*}"
    echo "$filename" | sed 's#_# #g' >>names.txt
done

echo "The namelist is:"
echo "----"
cat names.txt
echo "----"
