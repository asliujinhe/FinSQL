# FinSQL: Model-Agnostic LLMs-based Text-to-SQL Framework for Financial Analysis
<div style="text-align: center;">
<img src="resources/BULL_ICON.png" alt="bull_icon" style="width:200px;" />
</div>
This repository contains the code and dataset for the paper FinSQL: Model-Agnostic LLMs-based Text-to-SQL Framework for Financial Analysis.

Before we start, we need to download the dataset and the database from [Google Drive](https://drive.google.com/file/d/1OtyFdH9cs-6bEVj8yKK4Zt53N52L_dBH/view?usp=sharing) and put them in the directory `dataset/`

Then the file structure should be like this:
```shell
. tree           
├── BULL-cn
├── BULL-en
├── README.md
├── database_cn
├── database_en
└── get_dev.py

```

Later, we need to preprocess the dataset.

启动之前，先创建一个虚拟环境.
在WSL中，可以使用以下命令创建一个虚拟环境：
```shell
python3 -m venv venv
```
如果报错，可以尝试以下命令（或根据提示安装相应的包比如python3.10-venv）：
```text
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.10-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.
```
```shell
sudo apt-get install python3-venv
```

然后激活虚拟环境：
```shell
source venv/bin/activate
```

确保终端显示(venv)：
```shell
(venv) user@host:~$
```
然后安装依赖包：requirements.txt，pycharm应该会有提示，直接安装即可。
如果没有提示，可以使用以下命令安装依赖包：
```shell
pip install -r requirements.txt
```

安装完依赖包之后，我们cd到Parallel_Cross_Encoder目录下：
```shell
cd Parallel_Cross_Encoder
```

确保在Parallel_Cross_Encoder目录下，然后运行以下命令：
```shell
bash scripts/preprocessing_finsql.sh
```

然后我们开始训练模型：这个会下载很久的模型，需要耐心等待，不需要fq。
（就目前的训练脚本，只支持英语，如果要支持中文，需要解除脚本注释）
```shell
bash scripts/train_text2sql_schema_item_classifier_finsql.sh
```

最后，使用Cross-Encoder模型来预测dev集：

```shell
bash scripts/generate_text2sql_dataset_finsql.sh
```

After we preprossing the dataset, we perform hybrid data augmentation: 

```shell
bash scripts/hybrid_augmentation.sh 
```

Then we start to train the LLM model: 

```shell
bash ds_sft.sh  
```

