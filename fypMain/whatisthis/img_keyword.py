from torchvision import models
from torchvision import transforms
from django.conf import settings
import json, io
import PIL.Image #can't iuse Image as it will conflict with Image(object) used for upload_image
import os
import cv2

#model_DenseNet = models.densenet121(pretrained=True) #depreciated
weights = models.ResNet152_Weights.DEFAULT
model_ResNet = models.resnet152(weights='ResNet152_Weights.DEFAULT')
model_ResNet.eval()
#get imagenet natural language text mappings
json_path = os.path.join(settings.STATIC_ROOT, "imagenet_class_index.json")
imagenet_mapping = json.load(open(json_path))

from torchvision import transforms

def resnet_transform_image(image_bytes):
    """
    Transforms image into required resnet format: 224x224 with 3 RGB channels and normalized.
    And returns the corresponding tensor.
    """
    my_transforms = transforms.Compose([transforms.Resize(232),#resize
                                        transforms.CenterCrop(224),#crop size
                                        transforms.ToTensor(),
                                        transforms.Normalize(#rescale to 0 - 1.0
                                            [0.485, 0.456, 0.406],#mean values
                                            [0.229, 0.224, 0.225])])#std dev values
    image = PIL.Image.open(io.BytesIO(image_bytes))
    return my_transforms(image).unsqueeze(0)

#convert image to raw bytes for ML processing (used by both classifier and caption-er)
def img_to_bytes(file):
    # Load image (it is loaded as BGR by default)
    file = '.'+file  # look one folder above to ./media/images
    image = cv2.imread(file)
    # Conver array to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # image encoding
    success, encoded_image = cv2.imencode('.jpeg', image)
    # convert encoded image to bytearray
    return encoded_image.tobytes()
    
def get_resnet_classification(file):
    """For given image bytes, predict the classification label using the pretrained DenseNet"""
    # convert encoded image to bytearray
    content_bytes = img_to_bytes(file)
    #print(content_bytes) #debug print raw data
    tensor = resnet_transform_image(content_bytes)
    prediction = model_ResNet(tensor).squeeze(0).softmax(0)
    class_id = prediction.argmax().item()
    score = prediction[class_id].item()
    category_name = weights.meta["categories"][class_id]
    print(f"{category_name}: {100 * score:.1f}%")
    return category_name