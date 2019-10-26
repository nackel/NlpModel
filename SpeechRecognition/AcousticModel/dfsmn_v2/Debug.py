# coding=utf-8

# 引入外部库
import os
import tensorflow as tf
import json

# 引入内部库
from SpeechRecognition.AcousticModel.dfsmn_v2.utils import get_online_data, decode_ctc
from SpeechRecognition.AcousticModel.dfsmn_v2.Model.cnn_dfsmn_ctc import Am, am_hparams


def dfsmn_model_train (data_path, label_path):
	# 0.准备训练所需语料------------------------------
	with open('./lang/pinyin_dict.json', 'r', encoding='utf-8') as fo:
		pinyin_dict = json.load(fo)
	pinyin_dict['_'] = len(pinyin_dict)

	# 1.语言模型训练-----------------------------------
	am_args = am_hparams()
	am_args.data_path = data_path
	am_args.label_path = label_path
	am_args.thchs30 = True
	am_args.aishell = True
	am_args.prime = False
	am_args.stcmd = False
	am_args.vocab_dict = pinyin_dict
	am_args.bsz = 32
	am_args.epoch = 50
	am_args.lr = 1e-4
	am_args.dropout = 0.5
	am_args.d_input = 384
	am_args.d_model = 1024
	am_args.l_mem = 20
	am_args.r_mem = 20
	am_args.stride = 2
	am_args.n_init_filters = 32
	am_args.n_conv = 2
	am_args.n_cnn_layers = 4
	am_args.n_dfsmn_layers = 6
	am_args.init_range = 1
	am_args.init_std = 0
	am_args.is_training = True
	am_args.save_path = './ModelMemory/cnn_dfsmn_ctc/'
	am = Am(am_args)

	am.train_gpu(gpu_nums=4)


def dfsmn_model_decode (wav_file_path):
	# 1.语料加载-----------------------------------
	print('loading lang...')
	with open('./lang/pinyin_dict.json', 'r', encoding='utf-8') as fo:
		pinyin_dict = json.load(fo)
	pinyin_dict['_'] = len(pinyin_dict)

	# 2.声学模型加载-----------------------------------
	print('loading acoustic model...')
	am_args = am_hparams()
	am_args.vocab_dict = pinyin_dict
	am_args.d_input = 384
	am_args.d_model = 1024
	am_args.l_mem = 20
	am_args.r_mem = 20
	am_args.stride = 2
	am_args.n_init_filters = 32
	am_args.n_conv = 2
	am_args.n_cnn_layers = 4
	am_args.n_dfsmn_layers = 6
	am_args.init_range = 1
	am_args.init_std = 0
	am_args.is_training = False
	am_args.save_path = './ModelMemory/cnn_dfsmn_ctc/'
	am = Am(am_args)
	am.start_session()

	# 3. 启动在线识别-------------------------------------------
	print('start online decode...')
	x = get_online_data(wav_file_path)
	pinyin_id = am.predict(x)
	_, pinyin = decode_ctc(pinyin_id, list(pinyin_dict.keys()))