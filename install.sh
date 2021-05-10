set -eux


sudo apt install -y python3 python3-pip
sudo apt install -y git 
sudo apt install -y libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0 libportaudio2 ffmpeg

pip3 install vosk pygame RPi.GPIO 
pip3 install ffmpeg-normalize sounddevice pyaudio 

git clone https://github.com/alphacep/vosk-api


#Setup seeed voicecard
git clone https://github.com/respeaker/seeed-voicecard.git
pushd seeed-voicecard
#sudo ./install.sh
#Currently there is a bug in the kernel of respeak, run the following instead:
sudo ./install.sh --compat-kernel
popd

wget -O model.zip https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip
unzip model.zip
mv vosk-model* model

#Setup the present service
sudo cp present.service /etc/systemd/system/
systemctl status present
sudo systemctl enable present
sudo systemctl restart present
systemctl status present
sudo journalctl -u present


sudo reboot


