import numpy as np
import streamlit as st
from loguru import logger
import time

from pesto.common.testing.endpoint_manager import EndpointManager
from pesto.ws.features.converter.image.image import Image as PestoImage


def check_urls(urls):
    # Healthcheck until service responds
    num_tries = 0
    max_tries = 10

    logger.info("Trying api/v1/health for {}st time".format(num_tries + 1))

    endpoints = [EndpointManager(server_url=url) for url in urls]

    while num_tries < max_tries:
        for endpoint in endpoints:
            if endpoint.is_alive:
                return endpoint.server_url
        logger.info("Server not yet alive")
        num_tries += 1
        time.sleep(2)
        logger.info("Trying api/v1/health for {}th time".format(num_tries + 1))

    return None


@st.cache(show_spinner=False)
def encode_image(path):
    return PestoImage.from_uri(path).to_base64()


@st.cache(show_spinner=False)
def encode_image_from_upload(bytes):
    return PestoImage.from_bytes(bytes).to_base64()


@st.cache(show_spinner=False)
def read_file_as_string(path):
    """
    Download a single file and make its content available as a string.
    """
    with open(path, "r") as f:
        return f.read()


@st.cache(show_spinner=False)
def parse_payloads(input_payload, output_response):

    input_image = input_payload['image']
    input_image = PestoImage.from_base64(input_image).to_array()
    input_image = input_image.transpose((1, 2, 0))

    if output_response is not None:
        output_category = output_response['category']

    return input_image, output_category
