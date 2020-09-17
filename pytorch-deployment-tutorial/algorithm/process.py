import json
import os

import numpy as np
import torch.cuda
import torchvision.models
import torchvision.transforms
from PIL import Image

if torch.cuda.is_available():
    device = torch.device("cuda")
    cpu = torch.device("cpu")
else:
    device = torch.device("cpu")
    cpu = torch.device("cpu")

# Load Classes
with open(os.path.join("/etc/assets/", "classes.json"), "r") as f:
    IMAGENET_CLASS_INDEX = json.load(f)

# Load Model

# Make sure to pass `pretrained` as `True` to use the pretrained weights:
MODEL = torchvision.models.resnet50(pretrained=True)

if torch.cuda.is_available():
    MODEL = MODEL.to(device)

# Since we are using our model only for inference, switch to `eval` mode:
MODEL.eval()


class Process:
    @staticmethod
    def on_start() -> None:
        """
        Process.on_start will be called at server start time.
        If you need to load heavy resources before processing data, this should be done here.
        """
        image = (np.random.random((256, 256, 3)) * 255.0).astype(np.uint8)
        image = Image.fromarray(image)
        tensor = Process.transform_image(image).to(device)
        _ = MODEL.forward(tensor)
        print("DUMMY RUN OK")

    # Preprocessing function
    @staticmethod
    def transform_image(image: Image):
        my_transforms = torchvision.transforms.Compose([
            torchvision.transforms.Resize(255),
            torchvision.transforms.CenterCrop(224),
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        return my_transforms(image).unsqueeze(0)

    # Main processing function
    @staticmethod
    def process(image: np.ndarray):
        """
        The core algorithm is implemented here.
        """

        # pesto gives images as C,H,W so we will convert them back to H,W,C to convert them as PIL.Image
        image = image.transpose((1, 2, 0))
        image = image[:, :, :3]
        pil_image = Image.fromarray(image)

        # A tensor with a batch size of 1 (1, C, H, W)
        tensor = Process.transform_image(image=pil_image)

        if torch.cuda.is_available():
            tensor = tensor.to(device)

        # Forward
        outputs = MODEL.forward(tensor)

        if torch.cuda.is_available():
            outputs = outputs.to(cpu)

        # Postprocess
        _, y_hat = outputs.max(1)
        predicted_idx = str(y_hat.item())
        class_id, class_name = IMAGENET_CLASS_INDEX[predicted_idx]

        # Always return a dictionary, as in RestFUL API, return type is a POST request
        result = {"category": class_name}

        return result
