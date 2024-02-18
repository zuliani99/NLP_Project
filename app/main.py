# -*- coding: utf-8 -*-

from datetime import datetime

from BaseEmbedding import BaseEmbedding
from utils import accuracy_score, create_ts_dir_res, get_datasets
from TextDataset import get_dsname_dataloaders

from Approaches import MainApproch, LayerWise, LayerAggregation
from Competitors import BertLinears, BertLSTMGRU
from Baselines import Baselines

import torch
import torch.nn as nn
from transformers import DistilBertTokenizer, DistilBertModel, BertTokenizer, BertModel


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

choosen_model_embedding = 'DISTILBERT'
bool_ablations = False

bert_models = {
	'BERT': {
		'model': BertModel.from_pretrained("bert-base-uncased"),
		'tokenizer': BertTokenizer.from_pretrained('bert-base-uncased'),
		'n_layers': 12
	},
	'DISTILBERT': {
		'model': DistilBertModel.from_pretrained("distilbert-base-uncased"),
		'tokenizer': DistilBertTokenizer.from_pretrained('distilbert-base-uncased'),
		'n_layers': 6
	}
}


def run_methods(methods):
 
	for method in methods: method.run()
 
	if bool_ablations:
		# run ablations
		for ablation in methods[:4]:
			ablation.bool_ablations = True
			ablation.run()
  
 
def main():
    	
	batch_size = 128
	epochs = 100
	patience = 10

	tokenizer = bert_models[choosen_model_embedding]['tokenizer']
	model = bert_models[choosen_model_embedding]['model']
	model_hidden_size = model.config.hidden_size
 
	print('=> Getting data')
	ds_name_dataloaders = get_dsname_dataloaders(get_datasets(), tokenizer, batch_size)
	datasets_name = list(ds_name_dataloaders.keys())
	print(' DONE\n')
 
	timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	create_ts_dir_res(timestamp)
 
	#print(f'=> Obtaining Pretrained {choosen_model_embedding} Embeddings')
	#be = BaseEmbedding(model, device, ds_name_dataloaders, bert_models[choosen_model_embedding]['n_layers'])
	#be.save_base_embeddings(choosen_model_embedding)
	#print(' DONE\n')
 
	training_params = {
		'device': device,
		'batch_size': batch_size,
  		'model': model,
	  	'loss_fn': nn.CrossEntropyLoss(),
		'score_fn': accuracy_score,
		'patience': patience,
		'epochs': epochs,
	}
 
	common_parmas = {
		'datasets_name': datasets_name, 
		'timestamp': timestamp,
		'choosen_model_embedding': choosen_model_embedding
	}

	# our approaches
	main_approach = MainApproch(common_parmas, bool_ablations)
	layer_wise_all = LayerWise(common_parmas, bert_models[choosen_model_embedding]['n_layers'] * 768, bool_ablations)
	layer_wise_mean = LayerWise(common_parmas, 768, bool_ablations)
	layer_aggregation = LayerAggregation(training_params, common_parmas, bert_models[choosen_model_embedding]['n_layers'], 768, bool_ablations)
 
	
	# competitors
	bert_linears = BertLinears(training_params, common_parmas, model_hidden_size)
	bert_lstm = BertLSTMGRU(training_params, common_parmas, model_hidden_size, 'LSTM', bidirectional=False)
	bert_lstm_bi = BertLSTMGRU(training_params, common_parmas, model_hidden_size, 'LSTM', bidirectional=True)
	bert_gru = BertLSTMGRU(training_params, common_parmas, model_hidden_size, 'GRU', bidirectional=False)
	bert_gru_bi = BertLSTMGRU(training_params, common_parmas, model_hidden_size, 'GRU', bidirectional=True)
 
 
	# baselines
	baselines = Baselines(common_parmas)
	
	print('Starting running strategies...')
 
	methods = [
		# our approaches
		main_approach, layer_wise_all, layer_wise_mean, 
		#layer_aggregation,

		# competitors
		#bert_linears, bert_lstm, bert_lstm_bi, bert_gru, bert_gru_bi,
  
		# baselines
		#baselines
	]
 
	run_methods(methods)

if __name__ == "__main__":
	print(f'Running Application on {device}\n')
	main()
	

