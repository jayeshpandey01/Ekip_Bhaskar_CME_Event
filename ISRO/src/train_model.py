import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import spacepy.pycdf as pycdf
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Define the LSTM Model
class CMEDetectorLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout=0.2, output_size=1):
        super(CMEDetectorLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])  # Last time step
        out = self.sigmoid(out)       # Binary classification output
        return out

# Custom Dataset
class CMEDataset(Dataset):
    def __init__(self, data, labels, sequence_length=50):
        self.sequence_length = sequence_length
        self.scaler = StandardScaler()
        self.data = self.scaler.fit_transform(data)
        min_len = len(self.data) - self.sequence_length + 1
        self.data = self.data[:min_len + self.sequence_length - 1]
        self.labels = labels[:min_len + self.sequence_length - 1]

    def __len__(self):
        return len(self.data) - self.sequence_length + 1

    def __getitem__(self, idx):
        sequence = self.data[idx:idx + self.sequence_length]
        label = self.labels[idx + self.sequence_length - 1]  # Label for the last time step
        return torch.FloatTensor(sequence), torch.FloatTensor([label])

# Load and Prepare Data from CDF Files
def prepare_data(file_paths):
    dfs = []
    for file_path in file_paths:
        cdf = pycdf.CDF(file_path)
        if 'L2_BLK' in str(file_path):
            df = pd.DataFrame({
                'time': pd.to_datetime(cdf['epoch_for_cdf_mod'][:]),
                'proton_bulk_speed': cdf['proton_bulk_speed'][:],
                'proton_density': cdf['proton_density'][:],
                'alpha_density': cdf['alpha_density'][:],
                'spacecraft_xpos': cdf['spacecraft_xpos'][:],
                'spacecraft_ypos': cdf['spacecraft_ypos'][:],
                'spacecraft_zpos': cdf['spacecraft_zpos'][:]
            })
            dfs.append(df)
        elif 'L1_AUX' in str(file_path):
            df = pd.DataFrame({
                'spacecraft_xpos': cdf['spacecraft_xpos'][:],
                'spacecraft_ypos': cdf['spacecraft_ypos'][:],
                'spacecraft_zpos': cdf['spacecraft_zpos'][:]
            })
            dfs.append(df)
    combined_df = pd.concat(dfs, axis=1, join='outer').ffill().bfill()

    # ✅ Remove duplicated column names
    combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]

    return combined_df


# Generate Labels
def generate_labels(df):
    df['alpha_to_proton_ratio'] = df['alpha_density'] / df['proton_density']
    
    # Convert both to boolean (avoid float before using `&`)
    condition1 = (df['alpha_to_proton_ratio'] > 0.08)
    condition2 = (df['proton_bulk_speed'] > 500).rolling(window=10, min_periods=1).mean() > 0.5
    
    # Combine both conditions
    df['cme_label'] = (condition1 & condition2).astype(float)
    return df['cme_label'].values


# Training Function
def train_model(model, train_loader, val_loader, num_epochs, device):
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    best_val_loss = float('inf')
    train_losses = []
    val_losses = []

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0
        for sequences, labels in train_loader:
            sequences, labels = sequences.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(sequences)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for sequences, labels in val_loader:
                sequences, labels = sequences.to(device), labels.to(device)
                outputs = model(sequences)
                val_loss += criterion(outputs, labels).item()

        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        scheduler.step(avg_val_loss)
        train_losses.append(avg_train_loss)
        val_losses.append(avg_val_loss)

        print(f'Epoch [{epoch+1}/{num_epochs}], Train Loss: {avg_train_loss:.4f}, Val Loss: {avg_val_loss:.4f}')

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save(model.state_dict(), 'best_cme_model.pth')

    return train_losses, val_losses

# Main Execution
if __name__ == "__main__":
    # File paths
    file_paths = [
        'cdf_data/20250621/AL1_ASW91_L1_AUX_20250621_UNP_9999_999999_V01.cdf',
        'cdf_data/20250621/AL1_ASW91_L1_TH1_20250621_UNP_9999_999999_V01.cdf',
        'cdf_data/20250621/AL1_ASW91_L1_TH2_20250621_UNP_9999_999999_V01.cdf',
        'cdf_data/20250621/AL1_ASW91_L2_BLK_20250621_UNP_9999_999999_V02.cdf',
        'cdf_data/20250621/AL1_ASW91_L2_TH1_20250621_UNP_9999_999999_V02.cdf',
        'cdf_data/20250621/AL1_ASW91_L2_TH2_20250621_UNP_9999_999999_V02.cdf'
    ]

    # Load and prepare raw dataframe
    df = prepare_data(file_paths)

    # Generate binary labels
    labels = generate_labels(df)

    # ✅ Only these 6 features are used by the LSTM
    selected_features = ['proton_bulk_speed', 'proton_density', 'alpha_density',
                         'spacecraft_xpos', 'spacecraft_ypos', 'spacecraft_zpos']

    # Print for debugging
    print("All DataFrame columns:", list(df.columns))
    print("Shape before feature selection:", df.shape)
    print("Final feature columns:", df.columns.tolist())
    print("Unique column count:", len(df.columns.unique()))


    features = df[selected_features].values

    print("Shape after selecting correct features:", features.shape)

    # Split into train and validation sets
    train_size = int(0.8 * len(features))
    train_features, val_features = features[:train_size], features[train_size:]
    train_labels, val_labels = labels[:train_size], labels[train_size:]

    # Create Datasets and DataLoaders
    train_dataset = CMEDataset(train_features, train_labels)
    val_dataset = CMEDataset(val_features, val_labels)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)

    # Initialize model and device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CMEDetectorLSTM(input_size=6, hidden_size=64, num_layers=2, dropout=0.2).to(device)

    # Train model
    train_losses, val_losses = train_model(model, train_loader, val_loader, num_epochs=50, device=device)

    # Plot losses
    plt.plot(range(1, 51), train_losses, label='Train Loss')
    plt.plot(range(1, 51), val_losses, label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training vs Validation Loss')
    plt.legend()
    plt.savefig('training_loss.png')
    plt.close()
