"""
EfficientNet-based Deepfake Video Detection Model
Supports video frame extraction and training on video datasets
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import efficientnet_b0, efficientnet_b4
from PIL import Image
import cv2
import os
import yaml
import argparse
from tqdm import tqdm
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import logging
from pathlib import Path
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VideoFrameExtractor:
    """Extract frames from video files"""
    
    @staticmethod
    def extract_frames(video_path, num_frames=16, fps_based=False):
        """
        Extract evenly-spaced frames from video
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to extract
            fps_based: If True, extract based on FPS; else based on frame count
            
        Returns:
            List of PIL Images
        """
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.warning(f"Could not open video: {video_path}")
                return frames
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames < num_frames:
                # If video has fewer frames than requested, extract all
                indices = list(range(total_frames))
            else:
                # Extract evenly-spaced frames
                indices = [int(i * total_frames / num_frames) for i in range(num_frames)]
            
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    # Convert BGR to RGB
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(Image.fromarray(rgb_frame))
            
            cap.release()
        except Exception as e:
            logger.error(f"Error extracting frames from {video_path}: {e}")
        
        return frames


class VideoDeepfakeDataset(Dataset):
    """Dataset for video-based deepfake detection"""
    
    def __init__(self, root_dir, split='train', transform=None, frames_per_video=16, 
                 video_extensions=None, sampling_strategy='uniform'):
        """
        Args:
            root_dir: Root directory containing Real Videos/ and Fake Videos/ folders
            split: 'train', 'val', or 'test'
            transform: Image transforms
            frames_per_video: Number of frames to extract from each video
            video_extensions: List of video file extensions to look for
            sampling_strategy: 'uniform' (evenly-spaced) or 'random'
        """
        self.root_dir = root_dir
        self.transform = transform or transforms.ToTensor()
        self.frames_per_video = frames_per_video
        self.video_extensions = video_extensions or ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.sampling_strategy = sampling_strategy
        self.samples = []
        
        # Convert extensions to lowercase for comparison
        self.video_extensions = [ext.lower() for ext in self.video_extensions]
        
        # Load video samples
        self._load_samples(split)
        
        logger.info(f"Loaded {len(self.samples)} videos for {split} split")
    
    def _load_samples(self, split):
        """Load video samples from directory structure"""
        all_samples = []
        
        # Real Videos (Label 0)
        real_dir = os.path.join(self.root_dir, 'Real Videos')
        if os.path.exists(real_dir):
            for video_file in os.listdir(real_dir):
                if any(video_file.lower().endswith(ext) for ext in self.video_extensions):
                    all_samples.append((os.path.join(real_dir, video_file), 0, 'Real'))
        else:
            logger.warning(f"Real Videos directory not found: {real_dir}")
        
        # Fake Videos (Label 1)
        fake_dir = os.path.join(self.root_dir, 'Fake Vedios')  # Note: typo in original folder name
        if not os.path.exists(fake_dir):
            fake_dir = os.path.join(self.root_dir, 'Fake Videos')  # Fallback to correct spelling
        
        if os.path.exists(fake_dir):
            for video_file in os.listdir(fake_dir):
                if any(video_file.lower().endswith(ext) for ext in self.video_extensions):
                    all_samples.append((os.path.join(fake_dir, video_file), 1, 'Fake'))
        else:
            logger.warning(f"Fake Videos directory not found (tried both spellings)")
        
        if not all_samples:
            logger.error("No video samples found! Check dataset paths.")
            return
        
        # Shuffle and split (80% train, 20% val/test)
        import random
        random.seed(42)
        random.shuffle(all_samples)
        
        split_1 = int(0.8 * len(all_samples))
        split_2 = int(0.9 * len(all_samples))
        
        if split == 'train':
            self.samples = all_samples[:split_1]
        elif split == 'val':
            self.samples = all_samples[split_1:split_2]
        else:  # test
            self.samples = all_samples[split_2:]
        
        # Log class distribution
        real_count = sum(1 for _, label, _ in self.samples if label == 0)
        fake_count = sum(1 for _, label, _ in self.samples if label == 1)
        logger.info(f"{split.upper()} split - Real: {real_count}, Fake: {fake_count}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        video_path, label, video_type = self.samples[idx]
        
        # Extract frames from video
        frames = VideoFrameExtractor.extract_frames(video_path, self.frames_per_video)
        
        if not frames:
            # Return dummy black frames if extraction failed
            logger.warning(f"No frames extracted from {video_path}, using fallback")
            frames = [Image.new('RGB', (384, 384), color='black') for _ in range(self.frames_per_video)]
        
        # Pad or truncate to exact number of frames needed
        if len(frames) < self.frames_per_video:
            # Repeat last frame if not enough frames
            frames.extend([frames[-1]] * (self.frames_per_video - len(frames)))
        else:
            frames = frames[:self.frames_per_video]
        
        # Apply transforms and stack frames
        transformed_frames = []
        for frame in frames:
            try:
                if self.transform:
                    frame = self.transform(frame)
                transformed_frames.append(frame)
            except Exception as e:
                logger.error(f"Error transforming frame: {e}")
                # Return black frame
                transformed_frames.append(torch.zeros(3, 384, 384))
        
        frames_tensor = torch.stack(transformed_frames)  # Shape: (T, C, H, W)
        
        return frames_tensor, torch.tensor(label, dtype=torch.float32)


class EfficientNetVideoModel(nn.Module):
    """EfficientNet-based model for video deepfake detection"""
    
    def __init__(self, model_type='efficientnet_b0', pretrained=True, num_frames=16):
        """
        Args:
            model_type: 'efficientnet_b0' or 'efficientnet_b4'
            pretrained: Use ImageNet pretrained weights
            num_frames: Number of frames in input sequence
        """
        super(EfficientNetVideoModel, self).__init__()
        
        # Load base EfficientNet model
        if model_type == 'efficientnet_b0':
            self.backbone = efficientnet_b0(pretrained=pretrained)
            feature_dim = 1280
        elif model_type == 'efficientnet_b4':
            self.backbone = efficientnet_b4(pretrained=pretrained)
            feature_dim = 1792
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Remove classification head
        self.backbone = nn.Sequential(*list(self.backbone.children())[:-1])
        
        # Temporal aggregation
        self.lstm = nn.LSTM(
            input_size=feature_dim,
            hidden_size=512,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=0.3
        )
        
        # Classification head
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(512 * 2, 256)  # 512*2 for bidirectional LSTM
        self.relu = nn.ReLU()
        self.output = nn.Linear(256, 1)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (B, T, C, H, W)
            
        Returns:
            Logits of shape (B, 1)
        """
        B, T, C, H, W = x.shape
        
        # Extract features frame-by-frame
        x = x.view(B * T, C, H, W)
        features = self.backbone(x)
        features = features.view(B * T, -1)
        
        # Reshape back to sequence
        features = features.view(B, T, -1)
        
        # Temporal modeling with LSTM
        lstm_out, (hn, cn) = self.lstm(features)
        
        # Use final hidden state from both directions of last layer
        # hn shape: (num_layers * num_directions, batch, hidden_size)
        # For bidirectional: last layer forward + backward = hn[-2:] concatenated
        forward_hidden = hn[-2, :, :]  # Last layer, forward direction
        backward_hidden = hn[-1, :, :]  # Last layer, backward direction
        lstm_out = torch.cat((forward_hidden, backward_hidden), dim=1)  # (B, 1024)
        
        # Classification
        x = self.dropout(lstm_out)
        x = self.fc(x)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.output(x)
        return self.sigmoid(x)


def get_transforms(config, split='train'):
    """Create data transforms"""
    aug_config = config.get('augmentation', {})
    
    if split == 'train':
        transforms_list = [
            transforms.Resize((aug_config.get('resize', 384), aug_config.get('resize', 384))),
        ]
        
        if aug_config.get('random_horizontal_flip', True):
            transforms_list.append(transforms.RandomHorizontalFlip())
        
        if aug_config.get('random_vertical_flip', False):
            transforms_list.append(transforms.RandomVerticalFlip())
        
        if aug_config.get('random_rotation', 0) > 0:
            transforms_list.append(
                transforms.RandomRotation(aug_config.get('random_rotation', 15))
            )
        
        if aug_config.get('color_jitter', True):
            transforms_list.append(
                transforms.ColorJitter(
                    brightness=aug_config.get('color_brightness', 0.2),
                    contrast=aug_config.get('color_contrast', 0.2),
                    saturation=aug_config.get('color_saturation', 0.2),
                    hue=aug_config.get('color_hue', 0.1)
                )
            )
    else:
        transforms_list = [
            transforms.Resize((aug_config.get('resize', 384), aug_config.get('resize', 384))),
        ]
    
    transforms_list.extend([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=aug_config.get('normalize_mean', [0.485, 0.456, 0.406]),
            std=aug_config.get('normalize_std', [0.229, 0.224, 0.225])
        )
    ])
    
    return transforms.Compose(transforms_list)


def train_epoch(model, loader, criterion, optimizer, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0.0
    all_preds = []
    all_labels = []
    
    pbar = tqdm(loader, desc='Training')
    for frames, labels in pbar:
        frames, labels = frames.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(frames).squeeze(1)
        loss = criterion(outputs, labels)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        total_loss += loss.item()
        all_preds.extend((outputs > 0.5).cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
        
        pbar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    avg_loss = total_loss / len(loader)
    accuracy = accuracy_score(all_labels, all_preds)
    
    return avg_loss, accuracy


def validate_epoch(model, loader, criterion, device):
    """Validate for one epoch"""
    model.eval()
    total_loss = 0.0
    all_preds = []
    all_probs = []
    all_labels = []
    
    with torch.no_grad():
        pbar = tqdm(loader, desc='Validation')
        for frames, labels in pbar:
            frames, labels = frames.to(device), labels.to(device)
            
            outputs = model(frames).squeeze(1)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            all_preds.extend((outputs > 0.5).cpu().numpy())
            all_probs.extend(outputs.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
            pbar.set_postfix({'loss': f'{loss.item():.4f}'})
    
    avg_loss = total_loss / len(loader)
    accuracy = accuracy_score(all_labels, all_preds)
    precision = precision_score(all_labels, all_preds, zero_division=0)
    recall = recall_score(all_labels, all_preds, zero_division=0)
    f1 = f1_score(all_labels, all_preds, zero_division=0)
    
    try:
        auc = roc_auc_score(all_labels, all_probs)
    except:
        auc = 0.0
    
    return avg_loss, accuracy, precision, recall, f1, auc


def train_model(config):
    """Main training function"""
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logger.info(f"Using device: {device}")
    
    # Create checkpoint directory
    checkpoint_dir = config.get('checkpoint_dir', '../../checkpoints')
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # Load datasets
    logger.info("Loading datasets...")
    train_transform = get_transforms(config, split='train')
    val_transform = get_transforms(config, split='val')
    
    train_dataset = VideoDeepfakeDataset(
        config['train_data_path'],
        split='train',
        transform=train_transform,
        frames_per_video=config.get('frames_per_video', 16),
        video_extensions=config.get('video_extensions', ['.mp4'])
    )
    
    val_dataset = VideoDeepfakeDataset(
        config['val_data_path'],
        split='val',
        transform=val_transform,
        frames_per_video=config.get('frames_per_video', 16),
        video_extensions=config.get('video_extensions', ['.mp4'])
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=config.get('num_workers', 0),
        pin_memory=False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=config.get('num_workers', 0),
        pin_memory=False
    )
    
    # Initialize model
    logger.info(f"Initializing {config['model_type']} model...")
    model = EfficientNetVideoModel(
        model_type=config.get('model_type', 'efficientnet_b0'),
        pretrained=config.get('pretrained', True),
        num_frames=config.get('frames_per_video', 16)
    )
    model.to(device)
    
    # Loss, optimizer, and scheduler
    criterion = nn.BCELoss()
    
    # Convert weight_decay to float if it's a string from YAML
    weight_decay = config.get('weight_decay', 1e-4)
    if isinstance(weight_decay, str):
        weight_decay = float(weight_decay)
    
    if config.get('optimizer', 'adamw').lower() == 'adamw':
        optimizer = optim.AdamW(
            model.parameters(),
            lr=config['learning_rate'],
            weight_decay=weight_decay
        )
    else:
        optimizer = optim.Adam(
            model.parameters(),
            lr=config['learning_rate']
        )
    
    # Learning rate scheduler
    scheduler_type = config.get('scheduler', 'cosine')
    num_epochs = config['num_epochs']
    
    if scheduler_type == 'cosine':
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=num_epochs)
    elif scheduler_type == 'step':
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
    else:
        scheduler = optim.lr_scheduler.LinearLR(optimizer, total_iters=num_epochs)
    
    # Training loop
    best_val_accuracy = 0.0
    best_val_f1 = 0.0
    patience = config.get('early_stopping_patience', 5)
    patience_counter = 0
    
    training_history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': [],
        'val_precision': [],
        'val_recall': [],
        'val_f1': [],
        'val_auc': []
    }
    
    for epoch in range(num_epochs):
        logger.info(f"\n{'='*60}")
        logger.info(f"Epoch {epoch+1}/{num_epochs}")
        logger.info(f"{'='*60}")
        
        # Training
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        
        # Validation
        val_loss, val_acc, val_prec, val_rec, val_f1, val_auc = validate_epoch(
            model, val_loader, criterion, device
        )
        
        # Log metrics
        logger.info(
            f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}, "
            f"Precision: {val_prec:.4f}, Recall: {val_rec:.4f}, "
            f"F1: {val_f1:.4f}, AUC: {val_auc:.4f}"
        )
        
        # Record history
        training_history['train_loss'].append(float(train_loss))
        training_history['train_acc'].append(float(train_acc))
        training_history['val_loss'].append(float(val_loss))
        training_history['val_acc'].append(float(val_acc))
        training_history['val_precision'].append(float(val_prec))
        training_history['val_recall'].append(float(val_rec))
        training_history['val_f1'].append(float(val_f1))
        training_history['val_auc'].append(float(val_auc))
        
        # Save best model
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_val_accuracy = val_acc
            patience_counter = 0
            
            model_path = config['model_save_path']
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            torch.save(model.state_dict(), model_path)
            logger.info(f"✓ Best model saved: {model_path} (F1: {best_val_f1:.4f})")
        else:
            patience_counter += 1
        
        # Early stopping
        if patience_counter >= patience:
            logger.info(f"Early stopping triggered after {epoch+1} epochs")
            break
        
        scheduler.step()
    
    # Save training history
    history_path = os.path.join(
        checkpoint_dir,
        f"training_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(history_path, 'w') as f:
        json.dump(training_history, f, indent=2)
    logger.info(f"Training history saved to {history_path}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Training completed!")
    logger.info(f"Best validation accuracy: {best_val_accuracy:.4f}")
    logger.info(f"Best validation F1 score: {best_val_f1:.4f}")
    logger.info(f"Model saved to: {config['model_save_path']}")
    logger.info(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Train EfficientNet Video Deepfake Detector')
    parser.add_argument('--config', type=str, default='efficientnet_video_training_config.yaml', help='Path to config file')
    parser.add_argument('--model-type', type=str, default=None, help='Override model type')
    parser.add_argument('--batch-size', type=int, default=None, help='Override batch size')
    args = parser.parse_args()
    
    # Validate config path
    config_path = os.path.realpath(args.config)
    allowed_base = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    if not config_path.startswith(allowed_base):
        raise ValueError(f"Config path is outside allowed directory")
    
    # Load config
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with command-line arguments
    if args.model_type:
        config['model_type'] = args.model_type
    if args.batch_size:
        config['batch_size'] = args.batch_size
    
    logger.info("Configuration:")
    logger.info(json.dumps(config, indent=2))
    
    # Train model
    train_model(config)


if __name__ == '__main__':
    main()
