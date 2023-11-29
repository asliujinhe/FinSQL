import json
from torch.utils.data import Dataset
from utils.extra import get_logger

logger = get_logger(__name__)

class ColumnAndTableClassifierDataset(Dataset):
    def __init__(
            self,
            dir_: str = None,
            use_contents: bool = True,
            add_fk_info: bool = True,
    ):
        super(ColumnAndTableClassifierDataset, self).__init__()

        self.questions: list[str] = []

        self.all_column_infos: list[list[list[str]]] = []
        self.all_column_labels: list[list[list[int]]] = []

        self.all_table_names: list[list[str]] = []
        self.all_table_labels: list[list[int]] = []

        with open(dir_, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        for data in dataset:
            column_names_in_one_db = []
            column_names_original_in_one_db = []
            extra_column_info_in_one_db = []
            column_labels_in_one_db = []

            table_names_in_one_db = []
            table_names_original_in_one_db = []
            table_labels_in_one_db = []

            for table_id in range(len(data["db_schema"])):
                column_names_original_in_one_db.append(data["db_schema"][table_id]["column_names_original"])
                table_names_original_in_one_db.append(data["db_schema"][table_id]["table_name_original"])

                table_names_in_one_db.append(data["db_schema"][table_id]["table_name"])
                table_labels_in_one_db.append(data["table_labels"][table_id])

                column_names_in_one_db.append(data["db_schema"][table_id]["column_names"])
                column_labels_in_one_db += data["column_labels"][table_id]

                extra_column_info = ["" for _ in range(len(data["db_schema"][table_id]["column_names"]))]
                if use_contents:
                    contents = data["db_schema"][table_id]["db_contents"]
                    for column_id, content in enumerate(contents):
                        if len(content) != 0:
                            extra_column_info[column_id] += " , ".join(content)
                extra_column_info_in_one_db.append(extra_column_info)

            if add_fk_info:
                table_column_id_list = []
                # add a [FK] identifier to foreign keys
                for fk in data["fk"]:
                    source_table_name_original = fk["source_table_name_original"]
                    source_column_name_original = fk["source_column_name_original"]
                    target_table_name_original = fk["target_table_name_original"]
                    target_column_name_original = fk["target_column_name_original"]

                    if source_table_name_original in table_names_original_in_one_db:
                        source_table_id = table_names_original_in_one_db.index(source_table_name_original)
                        source_column_id = column_names_original_in_one_db[source_table_id].index(
                            source_column_name_original)
                        if [source_table_id, source_column_id] not in table_column_id_list:
                            table_column_id_list.append([source_table_id, source_column_id])

                    if target_table_name_original in table_names_original_in_one_db:
                        target_table_id = table_names_original_in_one_db.index(target_table_name_original)
                        target_column_id = column_names_original_in_one_db[target_table_id].index(
                            target_column_name_original)
                        if [target_table_id, target_column_id] not in table_column_id_list:
                            table_column_id_list.append([target_table_id, target_column_id])

                for table_id, column_id in table_column_id_list:
                    if extra_column_info_in_one_db[table_id][column_id] != "":
                        extra_column_info_in_one_db[table_id][column_id] += " , [FK]"
                    else:
                        extra_column_info_in_one_db[table_id][column_id] += "[FK]"

            # column_info = column name + extra column info
            column_infos_in_one_db = []
            for table_id in range(len(table_names_in_one_db)):
                column_infos_in_one_table = []
                for column_name, extra_column_info in zip(column_names_in_one_db[table_id],
                                                          extra_column_info_in_one_db[table_id]):
                    if len(extra_column_info) != 0:
                        column_infos_in_one_table.append(column_name + " ( " + extra_column_info + " ) ")
                    else:
                        column_infos_in_one_table.append(column_name)
                column_infos_in_one_db.append(column_infos_in_one_table)

            # print(f"question: {data['question']}")
            # print(f"table_names_in_one_db: {table_names_in_one_db}")
            # print(f"table_labels_in_one_db: {table_labels_in_one_db}")
            # print(f"column_infos_in_one_db: {column_infos_in_one_db}")
            # print(f"column_labels_in_one_db: {column_labels_in_one_db}")
            # exit()

            self.questions.append(data["question"])

            self.all_table_names.append(table_names_in_one_db)
            self.all_table_labels.append(table_labels_in_one_db)

            self.all_column_infos.append(column_infos_in_one_db)
            self.all_column_labels.append(column_labels_in_one_db)

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, index):
        question = self.questions[index]

        table_names_in_one_db = self.all_table_names[index]
        table_labels_in_one_db = self.all_table_labels[index]

        column_infos_in_one_db = self.all_column_infos[index]
        column_labels_in_one_db = self.all_column_labels[index]

        return question, table_names_in_one_db, table_labels_in_one_db, column_infos_in_one_db, column_labels_in_one_db


class ColumnAndTableClassifierDatasetOneByOne(Dataset):
    def __init__(
            self,
            dir_: str = None,
    ):
        super(ColumnAndTableClassifierDatasetOneByOne, self).__init__()
        self.questions: list[str] = []

        self.all_column_infos: list[list[list[str]]] = []
        self.all_column_labels: list[list[list[int]]] = []

        self.all_table_names: list[list[str]] = []
        self.all_table_labels: list[list[int]] = []

        self.all_table_infos: list[list[str]] = []
        self.all_table_info_labels: list[list[int]] = []

        with open(dir_, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        for data in dataset:
            column_names_in_one_db = []
            extra_column_info_in_one_db = []
            column_labels_in_one_db = []

            table_names_in_one_db = []
            table_labels_in_one_db = []

            for table_id in range(len(data["db_schema"])):
                table_name = data["db_schema"][table_id]["table_name"]
                table_label = data["table_labels"][table_id]
                column_names_in_one_table = data["db_schema"][table_id]["column_names"]
                column_labels_in_one_table = data["column_labels"][table_id]

                self.all_table_infos.append([table_name] + column_names_in_one_table)
                self.all_table_info_labels.append([table_label] + column_labels_in_one_table)
                self.questions.append(data["question"])

                table_names_in_one_db.append(table_name)
                table_labels_in_one_db.append(table_label)
                column_names_in_one_db.append(column_names_in_one_table)
                column_labels_in_one_db.append(column_labels_in_one_table)

                extra_column_info = ["" for _ in range(len(data["db_schema"][table_id]["column_names"]))]
                extra_column_info_in_one_db.append(extra_column_info)

                self.all_table_names.append([table_name])
                self.all_table_labels.append([table_label])
                self.all_column_infos.append([column_names_in_one_table])
                self.all_column_labels.append(column_labels_in_one_table)

                # print(f"question: {data['question']}")
                # print(f"table_names_in_one_db: {[table_name]}")
                # print(f"table_labels_in_one_db: {[table_label]}")
                # print(f"column_infos_in_one_db: {[column_names_in_one_table]}")
                # print(f"column_labels_in_one_db: {column_labels_in_one_table}")
                # exit()

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, index):
        # question = self.questions[index]
        # table_infos_in_one_table = self.all_table_infos[index]
        # table_info_labels_in_one_table = self.all_table_info_labels[index]
        # return question, table_infos_in_one_table, table_info_labels_in_one_table
        question = self.questions[index]

        table_names_in_one_db = self.all_table_names[index]
        table_labels_in_one_db = self.all_table_labels[index]

        column_infos_in_one_db = self.all_column_infos[index]
        column_labels_in_one_db = self.all_column_labels[index]

        return question, table_names_in_one_db, table_labels_in_one_db, column_infos_in_one_db, column_labels_in_one_db


class ColumnAndTableClassifierDatasetOnePerbatch(Dataset):
    def __init__(
            self,
            dir_: str = None
    ):
        super(ColumnAndTableClassifierDatasetOnePerbatch, self).__init__()
        self.questions: list[str] = []

        self.all_batch_column_infos: list[list[list[str]]] = []
        self.all_batch_column_labels: list[list[list[int]]] = []
        self.all_batch_table_names: list[list[list[str]]] = []
        self.all_batch_table_labels: list[list[list[int]]] = []


        with open(dir_, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        for data in dataset:

            table_names = []
            table_labels = []
            column_infos = []
            column_labels = []
            for table_id in range(len(data["db_schema"])):
                table_name = data["db_schema"][table_id]["table_name"]
                table_label = data["table_labels"][table_id]
                column_names_in_one_table = data["db_schema"][table_id]["column_names"]
                column_labels_in_one_table = data["column_labels"][table_id]

                table_names.append([table_name])
                table_labels.append([table_label])
                column_infos.append([column_names_in_one_table])
                column_labels.append(column_labels_in_one_table)

            self.questions.append(data["question"])
            self.all_batch_table_names.append(table_names)
            self.all_batch_table_labels.append(table_labels)
            self.all_batch_column_infos.append(column_infos)
            self.all_batch_column_labels.append(column_labels)


        # logger.info(f"{len(self.questions)} {len(self.all_batch_table_names)} {len(self.all_batch_table_labels)} {len(self.all_batch_column_infos)} {len(self.all_batch_column_labels)}")

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, idx):
        question = self.questions[idx]

        table_names = self.all_batch_table_names[idx]
        table_labels = self.all_batch_table_labels[idx]

        column_infos = self.all_batch_column_infos[idx]
        column_labels = self.all_batch_column_labels[idx]

        return question, table_names, table_labels, column_infos, column_labels



class RerankerDataset(Dataset):
    def __init__(
            self,
            dir_: str = None,
            use_contents: bool = True,
            add_fk_info: bool = True,
            remove_repeated=True,
            label_soft=0
    ):
        super(RerankerDataset, self).__init__()

        self.questions: list[str] = []
        self.all_candidate_sqls: list[list[str]] = []
        self.all_candidate_labels: list[list[float]] = []

        blocks = []
        with open(dir_, "r") as f:
            dataset = f.readlines()
        start_ids = []
        for id, line in enumerate(dataset):
            if line[:8] == "Correct:":
                start_ids.append(id)
        start_ids.append(len(dataset))
        for i in range(len(start_ids) - 1):
            be_id, ed_id = start_ids[i], start_ids[i + 1]
            blocks.append(dataset[be_id: ed_id - 1])
        # print(blocks[0])
        # print(blocks[-1])
        # print(len(blocks))
        for block in blocks:
            question = block[1][:-1]
            sqls = block[3:]
            labels = []
            if remove_repeated:
                sqls_filter = []
                for sql in sqls:
                    if sql not in sqls_filter:
                        sqls_filter.append(sql)
            else:
                sqls_filter = sqls

            # if len(sqls_filter) == 1:
            #     continue

            for id, sql in enumerate(sqls_filter):
                if sql[0] == "1":
                    labels.append(1)
                    sqls_filter[id] = sql[2:].strip('\n')
                elif sql[0] == "0":
                    labels.append(0)
                    sqls_filter[id] = sql[2:].strip('\n')
                else:
                    labels.append(0)
                    sqls_filter[id] = sql[3:-1].strip('\n')
            # print(sqls_filter)
            # print(labels)
            # if 1 not in labels:
            #     continue
            self.questions.append(question)
            self.all_candidate_sqls.append(sqls_filter)
            self.all_candidate_labels.append(labels)
            # print(labels, label_soft)
        print(f'data_size = {len(self.all_candidate_labels)}')

    def save_dataset(self, saved_dir):
        with open(saved_dir, 'w') as f:
            for i in range(len(self.questions)):
                question = self.questions[i]
                candidate_sqls = self.all_candidate_sqls[i]
                candidate_labels = self.all_candidate_labels[i]
                f.write(question + '\n')
                for sql, label in zip(candidate_sqls, candidate_labels):
                    f.write(f'{label} {sql}\n')
                f.write('\n')

        print(f'data has been saved to {saved_dir}')

    def __len__(self):
        return len(self.questions)

    def __getitem__(self, index):
        question = self.questions[index]
        candidate_sqls = self.all_candidate_sqls[index]
        candidate_labels = self.all_candidate_labels[index]

        return question, candidate_sqls, candidate_labels


class Text2SQLDataset(Dataset):
    def __init__(
            self,
            dir_: str,
            mode: str
    ):
        super(Text2SQLDataset).__init__()

        self.mode = mode

        self.input_sequences: list[str] = []
        self.output_sequences: list[str] = []
        self.db_ids: list[str] = []
        self.all_tc_original: list[list[str]] = []

        with open(dir_, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        for data in dataset:
            self.input_sequences.append(data["input_sequence"])
            self.db_ids.append(data["db_id"])
            self.all_tc_original.append(data["tc_original"])

            if self.mode == "train":
                self.output_sequences.append(data["output_sequence"])
            elif self.mode in ["eval", "test"]:
                pass
            else:
                raise ValueError("Invalid mode. Please choose from ``train``, ``eval`, and ``test``")

    def __len__(self):
        return len(self.input_sequences)

    def __getitem__(self, index):
        if self.mode == "train":
            return self.input_sequences[index], self.output_sequences[index], self.db_ids[index], self.all_tc_original[
                index]
        elif self.mode in ['eval', "test"]:
            return self.input_sequences[index], self.db_ids[index], self.all_tc_original[index]
