#import argparse
import torch
from PIL import Image
import numpy as np
from io import BytesIO

from donut import DonutModel
import donut

from mongoDB import MongoDBHandler

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

    def run_inference(self, image, image_name):
         # Ensure image is in PIL.Image.Image format
        if isinstance(image, str):  
            image = Image.open(image).convert("RGB")
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        elif isinstance(image, BytesIO):
            image = Image.open(image).convert("RGB")

        output = self.pretrained_model.inference(image=image, prompt=self.task_prompt)["predictions"][0]
        self.db_handler.save_inference_result(image_name, self.task_name, output) 

        return output
    

if  __name__ == "__main__":
    print(torch.__version__)
    image = Image.open("C:/Users/user/Documents/testing.jpg")
    # image.show()
    donut = DonutInference()
    print(donut.run_inference(image, image_name="testing.jpg"))

{'menu': [{'nm': '0571-1854 BLUS WANITA', 'unitprice': '@120,000', 'cnt': '1', 'price': '120,000'}, {'nm': '1002-0060 SHOPPING BAG', 'cnt': '1', 'price': '0'}], 'total': {'total_price': '120,000', 'changeprice': '0', 'creditcardprice': '120,000', 'menuqty_cnt': '1'}}