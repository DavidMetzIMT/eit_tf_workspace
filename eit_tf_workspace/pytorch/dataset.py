from typing import Union
import numpy as np
import random
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import os
import sys
sys.path.append('./')

from eit_tf_workspace.train_utils.dataset import Datasets, XYSet, scale_prepocess

from eit_tf_workspace.train_utils.metadata import MetaData
from logging import getLogger

logger = getLogger(__name__)

# # class StdPytorchDataset(Datasets):
   
# #     def get_X(self, part:str='train'):
# #         return getattr(self._pytorch_dataset, part)[0]

# #     def get_Y(self, part:str='train'):
# #         return getattr(self, part).get_set()[1]

# #     def get_samples(self, part: str):
# #         return getattr(self, part).get_set()

# #     def _preprocess(
# #         self,
# #         X:np.ndarray,
# #         Y:np.ndarray,
# #         metadata:MetaData)->tuple[Union[np.ndarray,None],Union[np.ndarray,None]]:
# #         """return X, Y preprocessed"""
# #         self._pytorch_dataset=
# #         X=scale_prepocess(X, metadata.normalize[0])
# #         Y=scale_prepocess(Y, metadata.normalize[1])
# #         if Y is not None:
# #             logger.debug(f'Size of X and Y (after preprocess): {X.shape=}, {Y.shape=}')     
# #         else:
# #             logger.debug(f'Size of X (after preprocess): {X.shape=}')
# #         return X, Y

#     def _mk_dataset(self, X:np.ndarray, Y:np.ndarray, metadata:MetaData)-> None:
#         """build the dataset"""
        
        
#         idx=np.reshape(range(X.shape[0]),(X.shape[0],1))
#         X= np.concatenate(( X, idx ), axis=1)
#         x_tmp, x_test, y_tmp, y_test = sklearn.model_selection.train_test_split(X, Y,test_size=self._test_ratio)
#         x_train, x_val, y_train, y_val = sklearn.model_selection.train_test_split(x_tmp, y_tmp, test_size=self._val_ratio)
        
#         self._idx_train= x_train[:,-1].tolist()
#         self._idx_val= x_val[:,-1].tolist()
#         self._idx_test= x_test[:,-1].tolist()
#         metadata.set_idx_samples(self._idx_train, self._idx_val, self._idx_test)

#         self.train=XYSet(x=x_train[:,:-1], y=y_train)
#         self.val=XYSet(x=x_val[:,:-1], y=y_val)
#         self.test=XYSet(x=x_test[:,:-1], y=y_test)

#     def _mk_dataset_from_indexes(self, X:np.ndarray, Y:np.ndarray, metadata:MetaData)-> None:
#         """rebuild the dataset with the indexes """
#         self._idx_train= convert_vec_to_int(metadata.idx_samples['idx_train'])
#         self._idx_val= convert_vec_to_int(metadata.idx_samples['idx_val'])
#         self._idx_test= convert_vec_to_int(metadata.idx_samples['idx_test'])   
#         self.train=XYSet(x=X[self._idx_train,:], y=Y[self._idx_train,:])
#         self.val=XYSet(x=X[self._idx_val,:], y=Y[self._idx_val,:])
#         self.test=XYSet(x=X[self._idx_test,:], y=Y[self._idx_test,:])


class torchDataset(Dataset):

    def __init__(self, loaded_data):
        # loaded_data is np.array
        self.data = loaded_data
        self.X = torch.Tensor(loaded_data[:, :-1]).float()
        self.Y = torch.Tensor(loaded_data[:, [-1]]).float()
        # self.X = loaded_data[:, :-1]
        # self.Y = loaded_data[:,[-1]]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.X[index], self.Y[index]

def normalization(data):
    return (data - data.mean()) / data.std()


def _mk_Dataloader(loaded_data, dataset_type):
    loaded_data = torchDataset(loaded_data)
    train_size = int(len(loaded_data) * 0.6)
    val_size = int(len(loaded_data) * 0.2)
    test_size = int(len(loaded_data) * 0.2)

    train_set, val_set, test_set = torch.utils.data.random_split(loaded_data, [train_size, val_size, test_size])
   
    if(dataset_type == 'train_set'):
        return DataLoader(train_set, batch_size=5, shuffle=True, num_workers=0)
    if(dataset_type == 'val_set'):
         return DataLoader(val_set, batch_size=5, shuffle=False, num_workers=0)
    if(dataset_type == 'test_set'):
         return DataLoader(test_set, batch_size=5, shuffle=False, num_workers=0)
        
    


    
    
    

if __name__ == "__main__":
    from eit_tf_workspace.utils.log import change_level, main_log
    import logging
    main_log()
    change_level(logging.DEBUG)

    # X = np.array([[random.randint(0, 100) for _ in range(4)] for _ in range(100)])
    # Y = np.array([random.randint(0, 100) for _ in range(100)])
    # print(f'{X}; {X.shape}\n; {Y}; {Y.shape}')
    
    X = np.random.randn(100, 4)
    Y = np.random.randn(100)

    XY = np.concatenate((X, Y[:, np.newaxis]), axis=1)

    # create the normalized dataset

    XY_normal = normalization(XY)
#     rdn_dataset = torchDataset(XY_normal)

#     for i in range(len(rdn_dataset)):
#         print(rdn_dataset[i])

# train_size = int(len(rdn_dataset) * 0.6)
# val_size = int(len(rdn_dataset) * 0.2)
# test_size = int(len(rdn_dataset) * 0.2)

# train_set, val_set, test_set = torch.utils.data.random_split(rdn_dataset, [train_size, val_size, test_size])

# train_loader = DataLoader(train_set, batch_size=5, shuffle=True, num_workers=0)

    train_loader = _mk_Dataloader(XY_normal, 'train_set')

    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = nn.Sequential(nn.Linear(4, 3),
                                        nn.BatchNorm1d(3),
                                        nn.ReLU(),
                                        nn.Linear(3, 1)
            )
            

        def forward(self, x):
        
            return self.layers(x)


    net = Model()

    loss_mse = nn.MSELoss()
    optimizer = torch.optim.Adam(net.parameters(), lr=0.001)

    for epoch in range(10):
        for i, data in enumerate(train_loader, 0):
            inputs, labels = data

            y_pred = net(inputs)
            loss = loss_mse(y_pred, labels)
            print(epoch, i, loss.item())

            optimizer.zero_grad()
            loss.backward()

            optimizer.step()
        