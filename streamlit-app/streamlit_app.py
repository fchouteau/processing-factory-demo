import json
from enum import Enum
from pathlib import Path
import time
import jsonschema
import streamlit as st
from pesto.common.testing.endpoint_manager import EndpointManager
from pesto.common.testing.payload_generator import PayloadGenerator
from pesto.common.testing.service_manager import ServiceManager
from pesto.common.testing.service_tester import ServiceTester
from pesto.common.utils import truncate_dict_for_debug

import pesto_streamlit as streamlit_utils

st.set_option('deprecation.showfileUploaderEncoding', False)

WORKDIR = Path(__file__).parent

DEFAULT_PAYLOAD_IN = WORKDIR / "pesto_streamlit" / "default" / "input"
DEFAULT_PAYLOAD_OUT = WORKDIR / "pesto_streamlit" / "default" / "output"

SERVICE_NAME = 'pytorch-deployment-tutorial:1.0.0.dev0'
SERVICE_PORT = 4000

### A lot of code designed to interact with the service manager provided by pesto to launch the docker in various ways
### and to find it automatically
try:
    SERVICE = ServiceManager(docker_image=SERVICE_NAME, host_port=SERVICE_PORT)
except:
    SERVICE = "docker-compose"

# Try with docker compose
with st.spinner("Loading App"):

    if SERVICE == "docker-compose":
        # We are inside a container and service was started through docker compose or docker
        SERVICE_URL = streamlit_utils.check_urls(
            ["http://localhost:8080", "http://localhost:4000", "http://pesto:8080"])
        SERVICE = "docker-compose"
    else:
        # We are in local mode
        SERVICE_PORT = 4000
        SERVICE_URL = "http://localhost:{}".format(SERVICE_PORT)

# Wrapper around pesto endpoints to manage get & post requests
ENDPOINTS = EndpointManager(server_url=SERVICE_URL)

# Tester utils to compare payloads / responses against expected values
TESTER = ServiceTester(server_url=SERVICE_URL)


class AppModes(Enum):
    SHOW_INSTRUCTIONS = "Show Instructions"
    DESCRIBE = "/describe"
    RUN = "/process"
    CODE = "/code"


def show_code():
    with open(__file__, "r") as f:
        st.code(f.read(), )


def show_instruction():
    st.sidebar.success('To continue select either "/describe or /process" modes')


def view_describe():
    # check that the server is alive
    st.text("Is the service alive ? {}".format(ENDPOINTS.is_alive))

    # get describe
    if ENDPOINTS.is_alive:
        st.markdown("## /api/v1/describe")
        st.json(ENDPOINTS.describe)


def run_process():
    # generate input payload
    input_schema = ENDPOINTS.input_schema
    output_schema = ENDPOINTS.output_schema

    st.markdown("## Schemas")

    st.markdown("### Input Schema")
    st.json(input_schema['properties'])
    st.markdown("### Output Schema")
    st.json(output_schema['properties'])

    st.markdown("## Payload")

    default_payload = PayloadGenerator(images_as_base64=False).generate(DEFAULT_PAYLOAD_IN)

    input_payload = {}
    for key in input_schema["properties"]:

        key_type = input_schema['properties'][key].get("type") or input_schema['properties'][key].get("$ref")

        if key_type == "#/definitions/Image":
            val = st.file_uploader(label="{}: {}".format(key, input_schema['properties'][key]),
                                   type=["png", "jpg", "tif", "jp2"])
        else:
            val = st.text_input(
                label="{}: {}".format(key, input_schema['properties'][key]),
                value=default_payload[key],
            )

        if key_type == "#/definitions/Image" and val is not None:
            # Convert image as base64 for processing
            val = streamlit_utils.encode_image_from_upload(val)

        if val is not None:
            try:
                input_payload[key] = json.loads(val)
            except:
                input_payload[key] = val

    if st.button(label="SEND PAYLOAD"):
        st.json(truncate_dict_for_debug(input_payload))
        try:
            jsonschema.validate(input_payload, input_schema)
            st.text("Input payload valid !")
        except jsonschema.ValidationError as e:
            st.text(e)
        except jsonschema.SchemaError as e:
            st.text(e)

        @st.cache(show_spinner=False)
        def _process(input_payload):
            return ENDPOINTS.process(input_payload)

        t1 = time.time()
        with st.spinner("Processing"):
            response = _process(input_payload)
        t2 = time.time()

        st.balloons()

        st.markdown("## Display")
        image, result = streamlit_utils.parse_payloads(input_payload, response)
        st.image(image, channels="RGB", use_column_width=True, caption="RGB image clipped to 8 bits")

        st.markdown("## Response")
        st.success("Response computed in {:.02f}s".format(t2 - t1))
        st.json(response)

def main():
    global SERVICE, SERVICE_NAME
    # Render the readme as markdown using st.markdown.
    readme_text = st.markdown(streamlit_utils.read_file_as_string(WORKDIR / "README.md"))

    # Once we have the dependencies, add a selector for the app mode on the sidebar.
    st.sidebar.title("What to do")

    app_mode = st.sidebar.selectbox(
        "Choose the app mode",
        [m.value for m in AppModes],
    )
    if SERVICE == "docker-compose":
        st.sidebar.info("Service {} accessible at {} from docker network".format(SERVICE_NAME, SERVICE_URL))
    elif isinstance(SERVICE, ServiceManager):
        if SERVICE.is_alive:
            st.sidebar.info("Service {} started at {}".format(SERVICE_NAME, SERVICE.server_url))
            if SERVICE._container is not None:
                if st.sidebar.button("STOP SERVICE"):
                    SERVICE.stop()
                    st.sidebar.info('Service Stopped')
        else:
            if st.sidebar.button("START SERVICE"):
                st.sidebar.info("Spawning container for service {}".format(SERVICE_NAME))
                SERVICE.run()
                st.sidebar.info('Service started at {}'.format(SERVICE.server_url))

    if app_mode == AppModes.SHOW_INSTRUCTIONS.value:
        show_instruction()

    elif app_mode == AppModes.RUN.value:
        readme_text.empty()
        readme_text = st.markdown(streamlit_utils.read_file_as_string(WORKDIR / "pesto_streamlit" / "_process.md"))
        st.sidebar.success('Entering /process mode')

        run_process()

    elif app_mode == AppModes.DESCRIBE.value:
        readme_text.empty()
        readme_text = st.markdown(streamlit_utils.read_file_as_string(WORKDIR / "pesto_streamlit" / "_describe.md"))
        st.sidebar.success('Entering /describe mode')

        view_describe()

    elif app_mode == AppModes.CODE.value:
        st.sidebar.success('Entering /code mode')
        readme_text.empty()

        show_code()
    else:
        st.sidebar.info("Wrong column")


if __name__ == "__main__":
    main()
