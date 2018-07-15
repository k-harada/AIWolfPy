from .tensor5460 import Tensor5460
import numpy as np
import os

import tensorflow as tf
from keras import backend as K
config = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1, \
                        allow_soft_placement=True, device_count = {'CPU': 1})
session = tf.Session(config=config)
K.set_session(session)
from keras.models import load_model


class Predictor_15(object):
    
    def __init__(self):
        
        # load model
        model2 = load_model(os.path.dirname(__file__)+"data/model20170819_180715_10epochs.h5")
        self.get_5460 = K.function([model2.layers[0].input, model2.layers[2].input],[model2.layers[12].output])
        
        # num of param
        self.n_para_3d = 12
        self.n_para_2d = 8
        
        self.x_3d = np.zeros((15, 15, self.n_para_3d), dtype='float32')
        self.x_2d = np.zeros((15, self.n_para_2d), dtype='float32')
        
        self.case15 = Tensor5460()
        self.t3d = self.case15.tensor5460_3d
        self.t2d = self.case15.tensor5460_2d
        
        self.t3d_mat = self.t3d.reshape(5460, 15*15*3*3)
        self.t2d_mat = self.t2d.reshape(5460, 15*3)
        
        self.watshi_ningen = np.ones(5460)
        
                
    def initialize(self, base_info, game_setting):
        # game_setting
        self.game_setting = game_setting
        
        # base_info
        self.base_info = base_info
        
        # initialize watashi_ningen
        self.watshi_ningen = np.ones(5460)
        xv = self.case15.get_case5460_df()["agent_"+str(self.base_info['agentIdx'])].values
        self.watshi_ningen[xv != 0] = 0.0
        
        # initialize x_3d, x_2d
        self.x_3d = np.zeros((15, 15, self.n_para_3d), dtype='float32')
        self.x_2d = np.zeros((15, self.n_para_2d), dtype='float32')
        
        
        """
        X_3d
        [i, j, 0] : agent i voted agent j (not in talk, action)
        [i, j, 1] : agent i divined agent j HUMAN
        [i, j, 2] : agent i divined agent j WEREWOLF
        [i, j, 3] : agent i inquested agent j HUMAN
        [i, j, 4] : agent i inquested agent j WEREWOLF
        [i, j, 5] : agent i managed to guard agent j
        [i, j, 6] : agent i says he/she will divine agent j
        [i, j, 7] : agent i says he/she will guard agent j
        [i, j, 8] : agent i says he/she will vote agent j
        [i, j, 9] : agent i estimates agent j is villager side
        [i, j,10] : agent i estimates agent j is WEREWOLF
        [i, j,11] : agent i estimates agent j is POSSESSED
        
        
        X_2d
        [i, 0] : agent i is executed
        [i, 1] : agent i is attacked
        [i, 2] : agent i comingout himself/herself SEER
        [i, 3] : agent i comingout himself/herself MEDIUM
        [i, 4] : agent i comingout himself/herself BODYGUARD
        [i, 5] : agent i comingout himself/herself VILLAGER
        [i, 6] : agent i comingout himself/herself WEREWOLF
        [i, 7] : agent i comingout himself/herself POSSESSED
        """
        
        
    def update(self, gamedf):
        # read log
        for i in range(gamedf.shape[0]):
            # vote
            if gamedf.type[i] == 'vote' and gamedf.turn[i] == 0:
                self.x_3d[gamedf.idx[i] - 1, gamedf.agent[i] - 1, 0] += 1
            # execute
            elif gamedf.type[i] == 'execute':
                self.x_2d[gamedf.agent[i] - 1, 0] = 1
            # attacked
            elif gamedf.type[i] == 'dead':
                self.x_2d[gamedf.agent[i] - 1, 1] = 1
            # talk
            elif gamedf.type[i] == 'talk':
                content = gamedf.text[i].split()
                # comingout
                if content[0] == 'COMINGOUT':
                    # self
                    if int(content[1][6:8]) == gamedf.agent[i]:
                        if content[2] == 'SEER':
                            self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                            self.x_2d[gamedf.agent[i] - 1, 2] = 1
                        elif content[2] == 'MEDIUM':
                            self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                            self.x_2d[gamedf.agent[i] - 1, 3] = 1
                        elif content[2] == 'BODYGUARD':
                            self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                            self.x_2d[gamedf.agent[i] - 1, 4] = 1
                        elif content[2] == 'VILLAGER':
                            self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                            self.x_2d[gamedf.agent[i] - 1, 5] = 1
                        elif content[2] == 'WEREWOLF':
                            self.x_2d[gamedf.agent[i] - 1, 7] = 0
                            self.x_2d[gamedf.agent[i] - 1, 6] = 1
                        elif content[2] == 'POSSESSED':
                            self.x_2d[gamedf.agent[i] - 1, 6] = 0
                            self.x_2d[gamedf.agent[i] - 1, 7] = 1
                # divined
                elif content[0] == 'DIVINED':
                    # 1, 2
                    # regard comingout
                    self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                    self.x_2d[gamedf.agent[i] - 1, 2] = 1
                    # result
                    if content[2] == 'HUMAN':
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 1] = 1
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 2] = 0
                    elif content[2] == 'WEREWOLF':
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 2] = 1
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 1] = 0
                elif content[0] == 'DIVINATION':
                    # 6
                    # regard comingout
                    self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                    self.x_2d[gamedf.agent[i] - 1, 2] = 1
                    # result
                    self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 6] = 1
                # identified
                elif content[0] == 'IDENTIFIED':
                    # 3, 4
                    # regard comingout
                    self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                    self.x_2d[gamedf.agent[i] - 1, 3] = 1
                    # result
                    if content[2] == 'HUMAN':
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 3] = 1
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 4] = 0
                    elif content[2] == 'WEREWOLF':
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 4] = 1
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 3] = 0
                # guarded
                elif content[0] == 'GUARDED':
                    # 5
                    # regard comingout
                    self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                    self.x_2d[gamedf.agent[i] - 1, 4] = 1
                    # result
                    self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 5] = 1
                elif content[0] == 'GUARD':
                    # 7
                    # regard comingout
                    self.x_2d[gamedf.agent[i] - 1, 2:6] = 0
                    self.x_2d[gamedf.agent[i] - 1, 4] = 1
                    # result
                    self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 7] = 1
                # vote 
                elif content[0] == 'VOTE':
                    # 8
                    # keep recent
                    self.x_3d[gamedf.agent[i] - 1, :, 8] = 0
                    self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 8] = 1
                # estimate
                elif content[0] == 'ESTIMATE':
                    # 9-11
                    # keep recent
                    self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 9:12] = 0
                    if content[2] == 'POSSESSED':
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 11] = 1
                    elif content[2] == 'WEREWOLF':
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 10] = 1
                    else:
                        self.x_3d[gamedf.agent[i] - 1, int(content[1][6:8])-1, 9] = 1
        
    def pred_5460(self):
        
        out = self.get_5460([self.x_3d.reshape((1, 15, 15, 12)), self.x_2d.reshape((1, 15, 8))])[0].reshape((5460,))
        
        return out
        
    def ret_pred(self):
        p = self.pred_5460()
        return np.tensordot(self.t2d, p / p.sum(), axes = [0, 0]).transpose()
        
    def ret_pred_wn(self):
        p = self.pred_5460() * self.watshi_ningen
        return np.tensordot(self.t2d, p / p.sum(), axes = [0, 0]).transpose()


        