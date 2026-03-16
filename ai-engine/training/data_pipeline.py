import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import os
import glob

class LivenessDataset(Dataset):
    """,
    Dataset for anti-spoofing / liveness detection.
    Expects folder structure:
    data/live/img1.jpg
    data/spoof/img1.jpg
    """,
    def __init__(self, root_dir, is_train=True):
        self.root_dir = root_dir
        self.is_train = is_train
        
        # Load image paths
        self.live_paths = glob.glob(os.path.join(root_dir, 'live', '*.jpg')) + \
                          glob.glob(os.path.join(root_dir, 'live', '*.png'))
        self.spoof_paths = glob.glob(os.path.join(root_dir, 'spoof', '*.jpg')) + \
                           glob.glob(os.path.join(root_dir, 'spoof', '*.png'))
                           
        self.all_paths = self.live_paths + self.spoof_paths
        
        # Labels: 1 for Live, 0 for Spoof
        self.labels = [1] * len(self.live_paths) + [0] * len(self.spoof_paths)
        
        # Transforms (Augmentation for training)
        if self.is_train:
            self.transform = transforms.Compose([
                transforms.Resize((256, 256)),
                transforms.RandomCrop(224),
                transforms.RandomHorizontalFlip(),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])
        else:
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ])

    def __len__(self):
        return len(self.all_paths)

    def __getitem__(self, idx):
        img_path = self.all_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
            
        return image, torch.tensor([float(label)], dtype=torch.float32)

def get_data_loaders(data_dir, batch_size=32, num_workers=4, distributed=False):
    """
    Returns configured train and val dataloaders.
    Supports PyTorch DistributedDataParallel (DDP) sampling.
    """
    train_dir = os.path.join(data_dir, 'train')
    val_dir = os.path.join(data_dir, 'val')
    
    train_dataset = LivenessDataset(train_dir, is_train=True)
    val_dataset = LivenessDataset(val_dir, is_train=False)
    
    if distributed:
        train_sampler = torch.utils.data.distributed.DistributedSampler(train_dataset)
        val_sampler = torch.utils.data.distributed.DistributedSampler(val_dataset, shuffle=False)
        shuffle = False
    else:
        train_sampler = None
        val_sampler = None
        shuffle = True
        
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, 
        shuffle=shuffle, num_workers=num_workers, 
        sampler=train_sampler, pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, 
        shuffle=False, num_workers=num_workers, 
        sampler=val_sampler, pin_memory=True
    )
    
    return train_loader, val_loader, train_sampler
