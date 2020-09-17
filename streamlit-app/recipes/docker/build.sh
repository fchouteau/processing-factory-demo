# Go to streamlit/ folder

echo "We assume that pesto is installed and the pesto.whl is located in /home/${USER}/.pesto/dist/pesto_cli-1.0.0-py3-none-any.whl"
cd ../../
cp /home/${USER}/.pesto/dist/pesto_cli-1.0.0-py3-none-any.whl .
docker build . -f recipes/docker/Dockerfile -t streamlit-pesto:1.0.0
