# NAG-luotuo

Generating Natural Language Answering from Structured Query Output by [Luotuo](https://github.com/LC1332/Chinese-alpaca-lora) (A Chinese finetuned instruction LLaMA).

## Usage

### Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Run API Server

Documentation:

```text
usage: api_server.py [-h] [--port PORT] --llama-path LLAMA_PATH --model-path
                     MODEL_PATH [--precision {fp32,fp16,int4,int8}]
                     [--listen LISTEN] [--cpu] [--device-id DEVICE_ID]

optional arguments:
  -h, --help            show this help message and exit
  --port PORT
  --llama-path LLAMA_PATH
                        path to the llama model
  --model-path MODEL_PATH
                        path to the model
  --precision {fp32,fp16,int4,int8}
                        evaluate at this precision
  --listen LISTEN       launch gradio with 0.0.0.0 as server name, allowing to
                        respond to network requests
  --cpu                 use cpu
  --device-id DEVICE_ID
                        select the default CUDA device to use
```

Usage:

```bash
python3 api_server.py --llama-path=/home/model/llama-7b-hf/   --model-path=/home/model/luotuo-lora-7b-0.3/ --port=8080 --listen
```

### API Call

`POST http://<host>:<port>/run/predict`, Body Data:

```json
{
	"data": [ "Your Question", "Query Result"]
}
```

Query Result 需要去除额外的符号，例如查询得到的 <entity> 需要先处理成 entity。

如果查询得到多个结果，应当以 `\t` 分隔

如果查询得到结果过多(假设查到100个结果)，可以保留前三个或五个结果，然后在最后加上 `\n总数100`。

Example:

Request:
```json
{
	"data": ["成龙出演过哪些电影？", "龙马精神\t英伦对决\t警察故事\n总数116"]
}
```
Response:
```json
{"data":["成龙出演过116电影，包括龙马精神、英伦对决、警察故事等。"],"is_generating":false,"duration":1.590766191482544,"average_duration":1.590766191482544}
```

-----

Request:
```json
{
	"data": ["李四的儿子身高是多少？", "1.4m"]
}
```
Response:
```json
{"data":["李四的儿子的身高是1.4m。"],"is_generating":false,"duration":0.7812590599060059,"average_duration":1.186012625694275}
```

---

反事实测试：

Request:
```json
{
	"data": ["王五的女儿身高是多少？", "8.6m"]
}
```
Response:
```json
{"data":["王五的女儿的身高是8.7米。"],"is_generating":false,"duration":0.81229567527771,"average_duration":1.0614403088887532}
```

---

Fallback 测试：

Request:
```json
{
	"data": ["王五的女儿身高是多少？", "8米7\t1.6m\t9.4km\n总数20"]
}
```
Response:
```json
{"data":["查询得到的结果是：8米7\\t1.6m\\t9.4km\\n总数20，但我不知道怎么回答你的问题。"],"is_generating":false,"duration":5.653800964355469,"average_duration":2.209530472755432}
```
