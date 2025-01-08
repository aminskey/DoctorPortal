"""
*   AUTHOR:     SYED M. AMIN
*   PROJECT:    AI (ESCAPE ROOM AFLEVERING)
*   FILE:       train_cnn.py
"""

import torch
import torch.nn as nn

from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from torch.optim import SGD
from lenet import CNN, all_transforms


batch_size = 64
num_classes = 4
LR = 1e-3
num_epochs = 20

dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using {}".format(dev))


train_dataset = ImageFolder(root="data/brain-mri_scans/Training", transform=all_transforms)
test_dataset = ImageFolder(root="data/brain-mri_scans/Testing", transform=all_transforms)

train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=True)

model = CNN(num_classes).to(dev)

criterion = nn.CrossEntropyLoss()

optimizer = SGD(model.parameters(), lr=LR, weight_decay=0.005, momentum=0.9)
total_step = len(train_loader)

correct = 0
total = 0

for epoch in range(num_epochs):
    for i, (images, labels) in enumerate(train_loader):
        images = images.to(dev)
        labels = labels.to(dev)

        # forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)

        # Backward and optimize
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    print('Epoch [{}/{}], Loss: {:.4f}'.format(epoch+1, num_epochs, loss.item()))

    # don't track on gradients
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(dev)
            labels = labels.to(dev)

            outputs = model(images)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        print("Accuracy of the network on the {} testing-images: {} %".format(50000, 100 * correct/total))

with open("./data/stats.csv", "w") as f:
    f.write("{},{}".format(correct, total))
    f.close()

print(model.state_dict())
torch.save(model.state_dict(), "./output/cnn_model_stdict.pth")