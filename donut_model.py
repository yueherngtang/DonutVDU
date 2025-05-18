#import argparse
import torch
from PIL import Image
import numpy as np
from io import BytesIO

from donut import DonutModel
import donut

import streamlit as st

import torch.nn as nn

# Patch to prevent crash if _init_weights is called
def _init_weights(self, module):
    for name, param in module.named_parameters(recurse=True):
        if param.requires_grad:
            if param.dim() > 1:
                nn.init.xavier_uniform_(param)
            else:
                nn.init.zeros_(param)

DonutModel._init_weights = _init_weights  # Patch once before loading

#from transformers import DonutProcessor
# C:/Users/User/Desktop/FIT3164/Project/DonutVDU/Test_Model
# C:/Users/User/Desktop/FIT3164/Project/DonutVDU/Test_Model/Training_4
# tyhtyhtyh/donut_test
class DonutInference:
    def __init__(self, task_name="cord-v2", pretrained_path="tyhtyhtyh/Training_4"):

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

    def run_inference(self, image, image_name):
         # Ensure image is in PIL.Image.Image format
        if isinstance(image, str):  
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        elif isinstance(image, BytesIO):
            image = Image.open(image).convert("RGB")

        output = self.pretrained_model.inference(image=image, prompt=self.task_prompt)["predictions"][0]
        # if st.session_state.db_user is not None:
        #     st.session_state.db_user.save_inference_result(image_name, self.task_name, output) 

        return output
    

if  __name__ == "__main__":
    print(torch.__version__)
    image = Image.open("C:/Users/User/Downloads/dataset_for_donut/dataset_for_donut/train/0023.jpg")
    # image.show()
    donut = DonutInference()
    print(donut.run_inference(image, image_name="Testing.png"))
