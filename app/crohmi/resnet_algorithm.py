import numpy as np
import pandas as pd
import os
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from io import open
from PIL import Image
from torch.autograd import Variable

from torchvision import datasets, models, transforms
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import DataLoader
from torchvision.models import resnet18, resnet50

import matplotlib.pyplot as plt
#from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, plot_confusion_matrix
#import seaborn as sns
print("Done")
print(__file__)

model = torch.load("/app/crohmi/resnet_test_model_new.pt",map_location=torch.device('cpu'))
model.eval()

torch.manual_seed(159)
dataset_path = "/"

def test_model(testloader, model, loss_fn):
    print("Testing {} model".format(model.__class__.__name__))
    test_metrics = {'labels' : [], 
                    'predictions' :[]}
    test_loss = 0.
    correct = 0.
    total = 0.
    model.eval()
    for batch_idx, (images, target) in enumerate(testloader):
        if (torch.cuda.is_available()):
            images = images.cuda()
            target = target.cuda()
        test_metrics['labels'] += list(target)
        outputs = model(images)
        loss = loss_fn(outputs, target)
        # update average test loss
        test_loss = test_loss + ((1 / (batch_idx + 1)) * (loss.data - test_loss))
        # convert output probabilities to predicted class
        pred = outputs.data.max(1, keepdim=True)[1]
        
        test_metrics['predictions'] += list(pred)
        # compare predictions to true label
        correct += np.sum(np.squeeze(pred.eq(target.data.view_as(pred))).cpu().numpy())
        total += images.size(0)
    print('Test Loss: {:.6f}\n'.format(test_loss))
    print('\nTest Accuracy: %.3f%% (%2d/%2d)' % (100. * correct / total, correct, total))
    return test_metrics
train_transform = transforms.Compose([
    transforms.Resize(size=(224,224)),
    transforms.RandomHorizontalFlip(), 
    transforms.ToTensor(), 
    transforms.Normalize(mean = [0.485, 0.456, 0.406],
                                    std = [0.229, 0.224, 0.225]) #Normalizing the data to the data that the ResNet18 was trained on
    
])
test_transform = transforms.Compose([
    transforms.Resize(size=(224,224)),
    transforms.ToTensor(), 
    transforms.Normalize(mean = [0.485, 0.456, 0.406],
                                    std = [0.229, 0.224, 0.225]) #Normalizing the data to the data that the ResNet18 was trained on
    
])

train_test_transform = {'train' : train_transform, 'test': test_transform}

testset = datasets.ImageFolder(dataset_path,       
                    transform=train_test_transform['test'])

def split_image_data(data_path, transform_dict):
    trainset = datasets.ImageFolder(data_path,       
                    transform=transform_dict['train'])
    testset = datasets.ImageFolder(data_path,       
                    transform=transform_dict['test'])
    
    num_test_imgs = int(np.floor(0.20 * len(trainset)))
    idx = list(range(len(trainset)))
    np.random.shuffle(idx)
    
    train_sampler = SubsetRandomSampler(idx[num_test_imgs:])
    test_sampler = SubsetRandomSampler(idx[:num_test_imgs])
    
    trainloader = DataLoader(trainset, sampler=train_sampler, batch_size=5)
    testloader = DataLoader(testset, sampler=test_sampler, batch_size=5)
    
    return trainloader, testloader

test_image1 = "/home/pi/Documents/resnet/image12345.png"
# test_image1 = "/home/pi/Documents/resnet/Crop_image_Captured.png"

imsize = 224
Test_data_transforms = transforms.Compose([ transforms.Resize(size=(224,224)),
     transforms.RandomHorizontalFlip(), transforms.ToTensor(),transforms.Normalize(mean = [0.485, 0.456, 0.406],
                                     std = [0.229, 0.224, 0.225])]) #Normalizing the data to the data that the ResNet18 was trained on])
loss_fn = torch.nn.CrossEntropyLoss()

def image_loader(image_name):
    """load image"""
    image = Image.open(image_name).convert('RGB')
    image = Test_data_transforms(image).float()
    image = Variable(image, requires_grad=True)
    image = image.unsqueeze(0)  
    return image

image = image_loader(test_image1)
predict = model(image)
print(predict.shape)
print(predict)
_,index = torch.max(predict,1)
pred = torch.max(predict.data,1)
values,indices = pred
print(indices)

if indices == 0:
    a = "HEALTHY"
elif indices == 1:
    a = "RESISTANT"
elif indices == 2:
    a = "SUSCEPTIBLE"
print (a)




