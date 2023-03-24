import datetime
import torch
import torchvision.transforms as transforms

from django.conf import settings
from PIL import Image
import pickle
import math
import io
import os

#models
import torch.nn as nn
from torchvision import models
from torch.nn.utils.rnn import pack_padded_sequence

class EncoderCNN(nn.Module):
    instance = None
    init_flag = False
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, EMBEDDING_DIM):
        if EncoderCNN.init_flag:
            return
        print("init")
        EncoderCNN.init_flag = True
        # Load the pretrained ResNet-152 and replace top fc layer.
        super(EncoderCNN, self).__init__()
        resnet = models.resnet152()
        # Delete the last fc layer
        modules = list(resnet.children())[:-1]
        self.resnet = nn.Sequential(*modules)
        self.linear = nn.Linear(resnet.fc.in_features, EMBEDDING_DIM)
        self.bn = nn.BatchNorm1d(EMBEDDING_DIM, momentum=0.01)

    def forward(self, images):
        # Extract feature vectors from input images.
        with torch.no_grad():
            features = self.resnet(images)
        features = features.reshape(features.size(0), -1)
        features = self.bn(self.linear(features))
        return features


class DecoderRNN(nn.Module):
    instance = None
    init_flag = False
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance
    def __init__(self, EMBEDDING_DIM, HIDDEN_DIM, VOCAB_SIZE, num_layers, MAX_SEG_LENGTH=20):
        if DecoderRNN.init_flag:
            return
        DecoderRNN.init_flag = True
        # Set the hyper-parameters and build the layers.
        super(DecoderRNN, self).__init__()
        self.embed = nn.Embedding(VOCAB_SIZE, EMBEDDING_DIM)
        self.lstm = nn.LSTM(EMBEDDING_DIM, HIDDEN_DIM, num_layers, batch_first=True)
        self.linear = nn.Linear(HIDDEN_DIM, VOCAB_SIZE)
        self.logsoftmax = nn.LogSoftmax(dim=1)
        self.MAX_SEG_LENGTH = MAX_SEG_LENGTH
        self.VOCAB_SIZE = VOCAB_SIZE

    def forward(self, features, captions, lengths):
        # Decode image feature vectors and generates captions.
        embeddings = self.embed(captions)
        embeddings = torch.cat((features.unsqueeze(1), embeddings), 1)
        packed = pack_padded_sequence(embeddings, lengths, batch_first=True)
        hiddens, _ = self.lstm(packed)
        outputs = self.linear(hiddens[0])
        return outputs

    def beam_search(self, features, BEAM_SIZE, END_ID, states=None):
        # Generate captions for given image features using beam search.
        device = features.device
        inputs = features.unsqueeze(1)
        VOCAB_SIZE = self.VOCAB_SIZE

        # Prepare the first beam
        # We expect the first token is <start>, so we choose only the one with the highest probability (it should be <start>)
        hiddens, states = self.lstm(inputs, states)                                 # hiddens: (1, 1, HIDDEN_DIM)
        outputs = self.linear(hiddens.squeeze(1))                                   # outputs: (1, VOCAB_SIZE)
        outputs = self.logsoftmax(outputs)
        prob, predicted = outputs.max(1)                                            # predicted: (1)
        sampled_ids = [(predicted, prob)]
        beam = [(self.embed(s).unsqueeze(1), states) for s, _ in sampled_ids]       # beam: [(inputs, states)]
        for _ in range(self.MAX_SEG_LENGTH-1):
            states_list = []
            prob_list = torch.tensor([]).to(device)
            idx_list = []
            for i, (inputs, states) in enumerate(beam):
                # If the last word is end, skip infering
                if sampled_ids[i][0][-1] == END_ID:
                    states_list.append(states)
                    prob_list = torch.cat((prob_list, sampled_ids[i][1][None]))
                    idx_list.extend([(i, END_ID)])
                else:
                    hiddens, states = self.lstm(inputs, states)                     # hiddens: (1, 1, HIDDEN_DIM)
                    outputs = self.linear(hiddens.squeeze(1))                       # outputs: (1, VOCAB_SIZE)
                    outputs = self.logsoftmax(outputs) + sampled_ids[i][1]
                    states_list.append(states)

                    idxs = zip([i] * VOCAB_SIZE, list(range(VOCAB_SIZE)))           # idx: [(beam_idx, vocab_idx)] * (VOCAB_SIZE)
                    idx_list.extend(idxs)                                           # idx_list: [(beam_idx, vocab_idx)] * (all inferred results of this layer)
                    prob_list = torch.cat((prob_list, outputs[0]))                  # prob_list: [prob] * (all inferred results of this layer)
            sorted, indices = torch.sort(prob_list, descending=True)                # sorted: sorted probabilities in the descending order, indices: idx of the sorted probabilities in the descending order
            prob = sorted[:BEAM_SIZE]
            beam_idx, vocab_idx = zip(*[idx_list[i] for i in indices[:BEAM_SIZE]])

            beam = []
            tmp_sampled_ids = []
            for i in range(BEAM_SIZE):
                word_id = torch.Tensor([vocab_idx[i]]).to(device).long()
                tmp_sampled_ids.append((torch.cat((sampled_ids[beam_idx[i]][0], word_id),0), prob[i]))
                inputs = self.embed(word_id)                                        # inputs: (1, EMBEDDING_DIM)
                inputs = inputs.unsqueeze(1)                                        # inputs: (1, 1, EMBEDDING_DIM)
                beam.append((inputs, states_list[beam_idx[i]]))                     # beam: [(inputs, states)] * (BEAM_SIZE)
            sampled_ids = tmp_sampled_ids

        return sampled_ids

#-models-


#hyperparameters
EMBEDDING_DIM = 256
HIDDEN_DIM = 512
NUM_LAYERS = 2
BEAM_SIZE = 5
MAX_SEG_LENGTH = 20
ID_TO_WORD_PATH = os.path.join(settings.STATIC_ROOT, 'vocab/id_to_word.pkl')
with open(ID_TO_WORD_PATH, 'rb') as f:
        ID_TO_WORD = pickle.load(f)
END_ID = [k for k, v in ID_TO_WORD.items() if v == '<end>'][0]
VOCAB_SIZE = len(ID_TO_WORD)
ENCODER_PATH =  os.path.join(settings.STATIC_ROOT, 'model/encoder.pth')
DECODER_PATH = os.path.join(settings.STATIC_ROOT, 'model/decoder.pth')

# load models only once
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print("Running in %s." % device)
encoder = EncoderCNN(EMBEDDING_DIM)
encoder = encoder.to(device).eval()

decoder = DecoderRNN(EMBEDDING_DIM, HIDDEN_DIM, VOCAB_SIZE, NUM_LAYERS, MAX_SEG_LENGTH)
decoder = decoder.to(device).eval()

# Load the trained model parameters
# encoder.linear.load_state_dict(torch.load(ENCODER_LINEAR_PATH))
# encoder.bn.load_state_dict(torch.load(ENCODER_BN_PATH))
encoder.load_state_dict(torch.load(ENCODER_PATH))
decoder.load_state_dict(torch.load(DECODER_PATH))

def transform_image(image_bytes):
    """
    Transform image into required DenseNet format: 224x224 with 3 RGB channels and normalized.
    Return the corresponding tensor.
    """
    my_transforms = transforms.Compose([transforms.Resize([224, 224], Image.LANCZOS),
                                        transforms.ToTensor(),
                                        transforms.Normalize(
                                            [0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    return my_transforms(image).unsqueeze(0)

def inference(image_bytes):
    """For given image bytes, output the cations and probilities using the EncoderCNN and DecoderRNN"""
    # Choose Device
    
    # Prepare an image
    image = transform_image(image_bytes).to(device)

    # Generate an caption from the image
    with torch.no_grad():
        feature = encoder(image)
        sampled_ids = decoder.beam_search(feature, BEAM_SIZE, END_ID)
    res=[]
    # Convert word_ids to words
    for i, (sampled_id, prob) in enumerate(sampled_ids):
        sampled_id = sampled_id.cpu().numpy()
        sampled_caption = []
        for word_id in sampled_id:
            word = ID_TO_WORD[word_id]
            if word != '<end>' and word != '<start>':
                sampled_caption.append(word)
            if word == '<end>':
                break
        sentence = ' '.join(sampled_caption)
        res.append((sentence, math.exp(prob.item()/len(sampled_id))*100))
    return res