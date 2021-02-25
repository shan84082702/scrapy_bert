import os
import re
import json
from pymongo import MongoClient
from bson.json_util import loads, dumps
from bson import ObjectId
from tqdm import tqdm
import shutil
import glob
from bs4 import BeautifulSoup
import random
from opencc import OpenCC


class TsvForBert:
    def __init__(self):
        MONGODB_DB_NAME = "webpage_dataset"
        MONGODB_DB_HOST = "fpgindexer2.widelab.org"
        MONGODB_PORT = 27021
        MONGODB_USER = "webpageDatasetMaster"
        MONGODB_PASSWORD = "webpageDatasetMasterPassword"

        # Database Settings
        db = MONGODB_DB_NAME
        host = MONGODB_DB_HOST
        port = MONGODB_PORT
        user = MONGODB_USER
        password = MONGODB_PASSWORD

        self.db_client = MongoClient(host, port)
        self.db = self.db_client[db]
        self.db.authenticate(user, password)

        self.keywords_mapper = dict()
        self.get_keywords_setting()
        self.MAX_ROW = 2000
        self.FREQUENCY_THRESHOLD = 1
        self.raw_en_folder = './train_data/raw/en'
        self.raw_zh_folder = './train_data/raw/zh'

        self.SUBJECTS = [
            'others', 
            'ai', 
            'internet_of_things', 
            'advanced_materials',
            #'quantum_computer', 
            #'formosa_plastics'
        ]
        self.LABELS = [
            'others', 
            'ai', 
            'internet_of_things', 
            'advanced_materials',
            #'quantum_computer', 
            #'formosa_plastics'
        ]

    def main(self):
        print("Chinese data first...")
        self.txtGenerator('', self.MAX_ROW, 'zh')
        #print("English data last...")
        #self.txtGenerator('', self.MAX_ROW, 'en')

        print("Merge Chinese data...")
        self.txtMerge('zh')
        #print("Merge English data...")
        #self.txtMerge('en')
        
        print("Sort Chinese data...")
        self.txtSort('zh')
        #print("Sort English data...")
        #self.txtSort('en')
        
        print("Start convert Chinese txt to tsv for BERT...")
        self.tsvGenerator('zh')
        #print("Start convert English txt to tsv for BERT...")
        #self.tsvGenerator('en')

    def touchFile(self, path):
        touch_file = open(path, 'w')
        touch_file.close()

    def list_files(self, directory, extension):
        return (f for f in os.listdir(directory)
                if f.endswith('.' + extension))

    def is_contains_chinese(self, strs):
        i_count = 0
        for _char in strs:
            if '\u4e00' <= _char <= '\u9fff':
                i_count += 1
                if i_count >= 4:
                    return True
        return False

    def get_keywords_setting(self):
        directory = './keywords'
        files = self.list_files(directory, "keywords")

        for f in files:
            rel_path = f'{directory}/{f}'
            subject_name = f.split('.')[0]
            self.keywords_mapper[subject_name] = list()

            with open(rel_path, 'r') as infile:
                for line in infile.readlines():
                    keyword = line.rstrip()
                    self.keywords_mapper[subject_name].append(keyword)
        #self.keywords_mapper['others'] = list()

    def txtGenerator(self, collection_name, num_of_records, lang):
        lang_prefix = 'EN' if lang == 'en' else 'ZH'

        if collection_name:
            pass
        else:
            # process 'other' label first
            for collection_name in self.db.list_collection_names():
                if collection_name != 'Links':
                #if collection_name == 'News':
                    with open(f'./train_data/raw/{lang}/others_{collection_name}.txt',
                              'w') as outfile:
                        subject='others'
                        pipeline = [{
                                "$project": {
                                    "_id": 1,
                                    "contents": 1,
                                    "subject": 1,
                                    "language": 1,
                                    "classifier": 1,
                                    "manual_labeling": 1,
                                    "title": 1,
                                    "hash_value": 1,
                                    "keyword_density": 1
                                }
                            }]
                        pipeline.append({"$match": {'language': {'$regex': lang_prefix},
                                                       '$or': [ { 'manual_labeling': [subject,subject] },
                                                                { '$and': [ {'manual_labeling':{'$ne':[subject,subject]}},
                                                                            {'classifier.'+subject:{'$gte':0.9}}]},
                                                                { '$and': [ {'manual_labeling':{'$ne':[subject,subject]}},
                                                                            {'$or':[{'classifier': {'$exists': False}},
                                                                                    {'classifier.'+subject: {'$lt': 0.9}}]}, 
                                                                            {'subject':subject}]}
                                                             ]}})
                        pipeline.append({"$limit": num_of_records})
                        collection = self.db[collection_name]
                        i_row_count = 0
                        print(
                            f'Start Write collection [others] : [{collection_name}] out'
                        )
                        print(f'Syntax : {pipeline}')

                        if i_row_count >= self.MAX_ROW:
                            break
                        for document in collection.aggregate(
                                pipeline, allowDiskUse=True):
                            title = document['title']
                            document["collection"]=collection_name
                            if lang == 'zh' and self.is_contains_chinese(
                                    title):
                                json_str = dumps(document, ensure_ascii=False)
                                outfile.write(f'{json_str}\n')
                                i_row_count += 1
                            else:
                                json_str = dumps(document, ensure_ascii=False)
                                outfile.write(f'{json_str}\n')
                                i_row_count += 1

                            if i_row_count % 5000 == 0:
                                print(
                                    f' [{lang}] : [{collection_name}] {i_row_count} rows writed out!'
                                )
                    print(
                        f' [{lang}] : [{collection_name}] total wrtie {i_row_count} out!'
                    )
                    os.rename(
                        f'./train_data/raw/{lang}/others_{collection_name}.txt',
                        f'./train_data/raw/{lang}/others_{collection_name}_{i_row_count}.txt'
                    )
            
            # then process the other labels
            for subject, keyword_list in self.keywords_mapper.items():
                for collection_name in self.db.list_collection_names():
                    if collection_name != 'Links':
                   # if collection_name == 'News':
                        with open(
                                f'./train_data/raw/{lang}/{subject}_{collection_name}.txt',
                                'w') as outfile:
                            pipeline = [{
                                "$project": {
                                    "_id": 1,
                                    "contents": 1,
                                    "subject": 1,
                                    "language": 1,
                                    "classifier": 1,
                                    "manual_labeling": 1,
                                    "title": 1,
                                    "hash_value": 1,
                                    "keyword_density": 1
                                }
                            }]
                            pipeline.append({"$match": {'language': {'$regex': lang_prefix},
                                                       '$or': [ { 'manual_labeling': [subject,subject] },
                                                                { '$and': [ {'manual_labeling':{'$ne':[subject,subject]}},
                                                                            {'classifier.'+subject:{'$gte':0.9}}]},
                                                                { '$and': [ {'manual_labeling':{'$ne':[subject,subject]}},
                                                                            {'$or':[{'classifier': {'$exists': False}},
                                                                                    {'classifier.'+subject: {'$lt': 0.9}}]}, 
                                                                            {'subject':subject}]}
                                                             ]}})
                            pipeline.append({"$limit": num_of_records})
                            pipeline.append({"$sort": {"keyword_density": -1}})
                            collection = self.db[collection_name]
                            i_row_count = 0
                            print(f'Syntax : {pipeline}')
                            print(
                                f'Start Write collection [{subject}] : [{collection_name}] out'
                            )
                            if i_row_count >= self.MAX_ROW:
                                break

                            for document in collection.aggregate(
                                    pipeline, allowDiskUse=True):
                                title = document['title']
                                document["collection"]=collection_name
                                if lang == 'zh' and self.is_contains_chinese(
                                        title):
                                    json_str = dumps(document,
                                                     ensure_ascii=False)
                                    outfile.write(f'{json_str}\n')
                                    i_row_count += 1
                                else:
                                    json_str = dumps(document,
                                                     ensure_ascii=False)
                                    outfile.write(f'{json_str}\n')
                                    i_row_count += 1

                                if i_row_count % 5000 == 0:
                                    print(
                                        f' [{lang}] : [{collection_name}] {i_row_count} rows writed out!'
                                    )

                        print(
                            f' [{lang}] : [{collection_name}] total wrtie {i_row_count} out!'
                        )
                        os.rename(
                            f'./train_data/raw/{lang}/{subject}_{collection_name}.txt',
                            f'./train_data/raw/{lang}/{subject}_{collection_name}_{i_row_count}.txt'
                        )

    def txtMerge(self, lang):
        if lang == 'zh':
            read_path = self.raw_zh_folder
        else:
            read_path = self.raw_en_folder

        merged_data_file_dict = dict()
        for subject in self.SUBJECTS:
            merged_data_file_dict[subject] = list()

        for filename in self.list_files(read_path, 'txt'):
            for subject, data in merged_data_file_dict.items():
                if subject in filename:
                    merged_data_file_dict[subject].append(
                        f'{read_path}/{filename}')
                    break

        for subject, path_list in merged_data_file_dict.items():
            write_out_path = f'./train_data/raw/without_ptt/{lang}_{subject}.txt'
            self.touchFile(write_out_path)
            i_count = 0
            #line_limit = 2000

            for i, path in enumerate(path_list):
                print(f' Merge [{path}] with [{write_out_path}]')

                with open(path, 'r') as infile, open(write_out_path,
                                                     'a') as outfile:
                    line_count = 0
                    for line in infile:
                        outfile.write(line)
                        i_count += 1
                        line_count +=1
                        #if line_count > line_limit-1:
                        #    break
            os.rename(write_out_path,
                      f'./train_data/raw/{lang}_{subject}_{i_count}.txt')

    def txtSort(self, lang):
        scan_path = f'./train_data/raw/{lang}_*'

        for txt_path in glob.glob(scan_path):
            if "others" not in txt_path:
                filename=txt_path.split('/')[3]
                output_path='./train_data/raw/without_ptt/'+filename
                with open(output_path, 'w') as file:
                    file.write(''.join(sorted(open(txt_path), key=lambda s: json.loads(s.rstrip())['keyword_density'],reverse=1)))
                os.remove(txt_path)
                os.rename(output_path, f'./train_data/raw/{filename}')
    
    
    def tsvGenerator(self, lang):
        train_path = f'./train_data/bert/{lang}/train.tsv'
        dev_path = f'./train_data/bert/{lang}/dev.tsv'

        with open(train_path,
                  'w') as train_file, open(dev_path, 'w') as dev_file:
            header = 'label\ttext_a\n'
            train_file.write(header)
            train_file.close()
            dev_file.write(header)
            dev_file.close()
            scan_path = f'./train_data/raw/{lang}_*'

            for txt_path in glob.glob(scan_path):
                label = ""

                for idx, subject in enumerate(self.SUBJECTS):
                    if subject in txt_path:
                        label = self.LABELS[idx]
                        print(
                            f'Processing [{txt_path}] [{subject}] [{label}]....'
                        )

                        with open(txt_path, 'r') as infile:
                            i_training_count = 0
                            i_dev_count = 0
                            i_count = 0

                            line_count = 2501
                            i_skip = 0
                            tmp_list = txt_path.split('.')[1].split('_')
                            i_total_lines = int(tmp_list[len(tmp_list) - 1])
                            #if line_count < i_total_lines:
                            #    i_skip = random.randint(
                            #        1, i_total_lines - line_count)
                            #   if i_skip + line_count > i_total_lines:
                            #        i_skip = 0

                            print(
                                f' > Total lines [{i_total_lines}], Skips [{i_skip}] lines, processes [{line_count}] lines'
                            )

                            for idx, line in tqdm(enumerate(infile)):
                                if idx >= i_skip:
                                    jsonObj = json.loads(line.rstrip())
                                    contents = jsonObj['contents']
                                    hash_value = jsonObj['hash_value']
                                    collection = jsonObj['collection']

                                    soup = BeautifulSoup(contents, 'lxml')
                                    if soup.body is not None:
                                        text = soup.body.get_text()
                                        regex = re.compile(r'[\n\r\t]')
                                        result = ' '.join(
                                            regex.sub('', text).split())
                                        i_training_count, i_dev_count= self.devideData(
                                            lang, label, i_training_count,
                                            i_dev_count, line_count, 
                                            hash_value, collection, result)
                                        i_count += 1
                                if i_count > line_count:
                                    break
                        print(f'[{txt_path}] {subject} {label} complete')

    def wordDensityCal(self, keywords, content):
        i_match = 0
        for idx, keyword in enumerate(keywords):
            #if content.count(keyword.casefold()) >= self.FREQUENCY_THRESHOLD:
            if keyword.casefold() in content:
                i_match += 1

        if i_match >= 1:
            return True
        return False

    def devideData(self, lang, label, i_training_count, i_dev_count,
                   line_count, hash_value, collection, content):
        with open(f'./train_data/bert/{lang}/train.tsv', 'a') as training_file, open(
                f'./train_data/bert/{lang}/dev.tsv',
                'a') as dev_file:

            max_len_of_bert_content = 510
            #max_len_of_bert_content = 298 
            total_len = len(content)
            if total_len <= max_len_of_bert_content:
                for_bert_result = content
            else:
                pivot = int(total_len / 2)
                for_bert_result = content[pivot-254:pivot] + content[pivot:pivot+254]
                #for_bert_result = content[pivot-148:pivot] + content[pivot:pivot+148]

            #listing_content = list(self.chunkstring(content, max_len_of_bert_content))
            switch = random.randint(1, 2)

            if switch == 1:
                if (i_training_count / line_count) * 100 <= 90:
                    #for for_bert_result in listing_content:
                    training_file.write('{label}\t{for_bert_result}\t{hash_value}\t{collection}\n'.format(
                        label=label, for_bert_result=for_bert_result, hash_value=hash_value, collection=collection))
                    i_training_count += 1
                else:
                    #for for_bert_result in listing_content:
                    dev_file.write('{label}\t{for_bert_result}\t{hash_value}\t{collection}\n'.format(
                    label=label, for_bert_result=for_bert_result, hash_value=hash_value, collection=collection))
                    i_dev_count += 1
            else:
                if (i_dev_count / line_count) * 100 <= 10:
                    #for for_bert_result in listing_content:
                    dev_file.write('{label}\t{for_bert_result}\t{hash_value}\t{collection}\n'.format(
                        label=label, for_bert_result=for_bert_result, hash_value=hash_value, collection=collection))
                    i_dev_count += 1
                else:
                    #for for_bert_result in listing_content:
                    training_file.write('{label}\t{for_bert_result}\t{hash_value}\t{collection}\n'.format(
                    label=label, for_bert_result=for_bert_result, hash_value=hash_value, collection=collection))
                    i_training_count += 1
        return i_training_count, i_dev_count

    def chunkstring(self, string, length):
        return (string[0 + i:length + i]
                for i in range(0, len(string), length))


class TSTransform:
    def __init__(self):
        self.transform('train.tsv')
        self.transform('dev.tsv')

    def transform(self, filename):
        cc = OpenCC('t2s')
        base_path = f'./train_data/bert/zh'

        print(f'Start Processing {filename}')
        with open(f'{base_path}/{filename}',
                  'r') as infile, open(f'{base_path}/t2s/{filename}',
                                       'w') as outfile:
            line = infile.readline()
            i_count = 0

            while line:
                if i_count == 0:
                    outfile.write(line)
                else:
                    pair = line.rstrip().split('\t')
                    label = pair[0]
                    token = pair[1]
                    dump_str = f'{label}\t{cc.convert(token)}\n'
                    outfile.write(dump_str)
                i_count += 1
                line = infile.readline()


TsvForBert().main()
#TSTransform()