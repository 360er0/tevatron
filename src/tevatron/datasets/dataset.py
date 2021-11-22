from datasets import load_dataset
from .preprocessor import TrainPreProcessor, QueryPreProcessor, CorpusPreProcessor
from ..arguments import DataArguments

DEFAULT_PROCESSORS = [TrainPreProcessor, QueryPreProcessor, CorpusPreProcessor]
PROCESSOR_INFO = {
    'Tevatron/wikipedia-nq': DEFAULT_PROCESSORS,
    'Tevatron/wikipedia-trivia': DEFAULT_PROCESSORS,
    'Tevatron/wikipedia-curated': DEFAULT_PROCESSORS,
    'Tevatron/wikipedia-wq': DEFAULT_PROCESSORS,
    'Tevatron/wikipedia-squad': DEFAULT_PROCESSORS,
    'Tevatron/scifact': DEFAULT_PROCESSORS,
    'Tevatron/msmarco-passage': DEFAULT_PROCESSORS,
    'json': [None, None, None]
}


class HFTrainDataset:
    def __init__(self, tokenizer, data_args: DataArguments):
        data_files = data_args.train_path
        if data_files:
            data_files = {'split_name': data_files}
        self.dataset = load_dataset(data_args.dataset_name,
                                    data_args.dataset_language,
                                    data_files=data_files)[data_args.dataset_split]
        self.preprocessor = PROCESSOR_INFO[data_args.dataset_name][0] if data_args.dataset_name in PROCESSOR_INFO\
            else DEFAULT_PROCESSORS[0]
        self.tokenizer = tokenizer
        self.q_max_len = data_args.q_max_len
        self.p_max_len = data_args.p_max_len
        self.proc_num = data_args.dataset_proc_num

    def process(self):
        if self.preprocessor is None:
            return self.dataset
        self.dataset = self.dataset.map(
            self.preprocessor(self.tokenizer, self.q_max_len, self.p_max_len),
            batched=False,
            num_proc=self.proc_num,
            remove_columns=self.dataset,
            desc="Running tokenizer on train dataset",
        )
        return self.dataset


class HFQueryDataset:
    def __init__(self, tokenizer, data_args: DataArguments):
        data_files = data_args.encode_in_path
        if data_files:
            data_files = {'split_name': data_files}
        self.dataset = load_dataset(data_args.dataset_name,
                                    data_args.dataset_language,
                                    data_files=data_files)[data_args.dataset_split]
        self.preprocessor = PROCESSOR_INFO[data_args.dataset_name][1] if data_args.dataset_name in PROCESSOR_INFO \
            else DEFAULT_PROCESSORS[1]
        self.tokenizer = tokenizer
        self.q_max_len = data_args.q_max_len
        self.proc_num = data_args.dataset_proc_num

    def process(self):
        if self.preprocessor is None:
            return self.dataset
        self.dataset = self.dataset.map(
            self.preprocessor(self.tokenizer, self.q_max_len),
            batched=False,
            num_proc=self.proc_num,
            remove_columns=self.dataset,
            desc="Running tokenization",
        )
        return self.dataset


class HFCorpusDataset:
    def __init__(self, tokenizer, data_args: DataArguments):
        data_files = data_args.encode_in_path
        if data_files:
            data_files = {'split_name': data_files}
        self.dataset = load_dataset(data_args.dataset_name,
                                    data_args.dataset_language,
                                    data_files=data_files)[data_args.dataset_split]
        script_prefix = data_args.dataset_name
        if script_prefix.endswith('-corpus'):
            script_prefix = script_prefix[:-7]
        self.preprocessor = PROCESSOR_INFO[script_prefix][2] \
            if script_prefix in PROCESSOR_INFO else DEFAULT_PROCESSORS[2]
        self.tokenizer = tokenizer
        self.p_max_len = data_args.p_max_len
        self.proc_num = data_args.dataset_proc_num

    def process(self):
        if self.preprocessor is None:
            return self.dataset
        self.dataset = self.dataset.map(
            self.preprocessor(self.tokenizer, self.p_max_len),
            batched=False,
            num_proc=self.proc_num,
            remove_columns=self.dataset,
            desc="Running tokenization",
        )
        return self.dataset

