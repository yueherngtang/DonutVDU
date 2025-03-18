#import argparse
import torch
from PIL import Image
import numpy as np
from io import BytesIO

from donut import DonutModel
#from transformers import DonutProcessor

class DonutInference:
    def __init__(self, task_name="cord-v2", pretrained_path="naver-clova-ix/donut-base-finetuned-cord-v2"):

        self.task_name = task_name
        self.task_prompt = "<s_docvqa><s_question>{user_input}</s_question><s_answer>" if "docvqa" == task_name else f"<s_{task_name}>"
        self.pretrained_model = self._load_model(pretrained_path)
        #self.processor = DonutProcessor.from_pretrained(pretrained_path)

    def _load_model(self, pretrained_path):

        model = DonutModel.from_pretrained(pretrained_path)
        if torch.cuda.is_available():
            model.half()
            model.to(torch.device("cuda"))
        else:
            pass
            #model.encoder.to(torch.bfloat16)

        model.eval()
        return model

    def run_inference(self, image):
         # Ensure image is in PIL.Image.Image format
        if isinstance(image, str):  
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        elif isinstance(image, BytesIO):
            image = Image.open(image).convert("RGB")

        output = self.pretrained_model.inference(image=image, prompt=self.task_prompt)["predictions"][0]

        return output
    

if  __name__ == "__main__":
    image = Image.open("C:/Users/User/Documents/DONUTVDU/testing.png")
    image.show()
    donut = DonutInference()
    print(donut.run_inference(image))