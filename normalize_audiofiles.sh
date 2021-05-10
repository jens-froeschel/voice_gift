set -eux

pushd audiofiles
for f in *"-"*; do
	mv -- "$f" "${f//-/_}" || true
done
for f in *" "*; do
	mv -- "$f" "${f// /_}" || true
done
for f in *","*; do
	mv -- "$f" "${f//,/_}" || true
done
for f in *"___"*; do
	mv -- "$f" "${f//___/_}" || true
done
for f in *"__"*; do
	mv -- "$f" "${f//__/_}" || true
done

for f in $( ls | grep [A-Z] ); do 
	mv -i $f `echo $f | tr 'A-Z' 'a-z'`;
done

for f in *; do
	filename=$(basename -- "$f")
	extension="${filename##*.}"
	if [ "$extension" = "wav" ]; then
		continue;
	fi
	filename="${filename%.*}"
	ffmpeg -n -i "$f" "${filename}.wav"
	rm $f
done

for f in *.wav; do
        ffmpeg -y -i "${f}" -ar 48000 -filter:a loudnorm tmp.wav
	mv tmp.wav "$f"
#	ffmpeg -y -i tmp.wav -ar 48000 -filter:a "volume=0.75" ${f}
#	ffmpeg-normalize ${f}
done


popd
