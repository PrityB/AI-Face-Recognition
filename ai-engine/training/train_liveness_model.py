import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.liveness_detection.model import LivenessNet
from data_pipeline import get_data_loaders

def setup_distributed():
    """Setup PyTorch Distributed Data Parallel (DDP)."""
    dist.init_process_group(backend='nccl' if torch.cuda.is_available() else 'gloo')
    local_rank = int(os.environ.get("LOCAL_RANK", 0))
    if torch.cuda.is_available():
        torch.cuda.set_device(local_rank)
    return local_rank

def cleanup_distributed():
    dist.destroy_process_group()

def train(epochs=10, batch_size=32, learning_rate=1e-4, data_dir="data"):
    # 1. Setup Environment
    is_distributed = int(os.environ.get("WORLD_SIZE", 1)) > 1
    local_rank = setup_distributed() if is_distributed else 0
    device = torch.device(f'cuda:{local_rank}' if torch.cuda.is_available() else 'cpu')
    
    # 2. Setup Data
    train_loader, val_loader, train_sampler = get_data_loaders(
        data_dir, batch_size, distributed=is_distributed
    )
    
    # 3. Setup Model
    model = LivenessNet().to(device)
    if is_distributed:
        model = DDP(model, device_ids=[local_rank] if torch.cuda.is_available() else None)
        
    # 4. Setup Loss & Optimizer
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # 5. Training Loop
    if local_rank == 0:
        print(f"Starting training on {device} (Distributed: {is_distributed})")
        
    for epoch in range(epochs):
        if is_distributed and train_sampler is not None:
            train_sampler.set_epoch(epoch)
            
        model.train()
        running_loss = 0.0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            
        # Validation Loop
        model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                # Accuracy calculation
                predicted = (outputs > 0.5).float()
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
                
        if local_rank == 0:
            print(f"Epoch {epoch+1}/{epochs}")
            print(f"Train Loss: {running_loss/len(train_loader):.4f}")
            print(f"Val Loss: {val_loss/len(val_loader):.4f} | Val Acc: {100.*correct/total:.2f}%")
            print("-" * 30)
            
    # 6. Save Model (Rank 0 only)
    if local_rank == 0:
        os.makedirs("checkpoints", exist_ok=True)
        # Unwrap DDP module if distributed
        model_state = model.module.state_dict() if is_distributed else model.state_dict()
        torch.save(model_state, "checkpoints/liveness_model_final.pth")
        print("Model saved successfully.")
        
    if is_distributed:
        cleanup_distributed()

if __name__ == "__main__":
    # Example usage. In practice run via: torchrun --nproc_per_node=2 train_liveness_model.py
    # Fallback to single CPU/GPU for script execution
    try:
        # Fails gracefully if 'data' dir doesn't exist
        if os.path.exists("data/train"):
            train()
        else:
            print("To run training, place image data in 'ai-engine/data/train/live' and 'ai-engine/data/train/spoof'")
    except Exception as e:
        print(f"Training script ready, but couldn't execute: {e}")
