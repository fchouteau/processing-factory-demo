# Pesto Streamlit App

Demo of using Streamlit + Pesto

To run the service, you can either:

- install streamlit and pesto locally and run the app using `streamlit run streamlit_app.py`. You will then be able to run a container using the local docker client or connect to an existing service exposed on port 4000

- go to `recipes/docker` and use the `docker-compose.yml` file: `docker-compose up`. This will start a container with streamlit on port 8501 and a container with the service on port 4000 and both containers will communicate 

- prestart your service using `docker run --rm -p 4000:8080 --network=host pytorch-deployment-tutorial:1.0.0.dev0` (or any other service with the same api...) then run the streamlit docker container using `docker run --rm --network=host pytorch-deployment-tutorial:1.0.0.dev0 ` with network mode ON

Then go to `http://localhost:8501` and follow the instructions

If you are using the app locally, you should see a `START SERVICE` button on the left. Use it to start the service via docker (CPU only) . If there is already a process exposed at port 4000, it will connect to it (if you started the docker through ssh or something...)

There are 2 modes:

- Describe: This should display the content of `/api/v1/describe`

- Process: This should allow you to pass a processing request to the service while uploading your own image
