import re

from modules.device import torch_gc
from modules.options import cmd_opts

tokenizer = None
model = None
generation_config = None


def prepare_model():
    global model
    if cmd_opts.cpu:
        if cmd_opts.precision == "fp32":
            model = model.float()
        elif cmd_opts.precision == "bf16":
            model = model.bfloat16()
        else:
            model = model.float()
    else:
        if cmd_opts.precision == "fp16":
            model = model.half().cuda()
        elif cmd_opts.precision == "int4":
            model = model.half().quantize(4).cuda()
        elif cmd_opts.precision == "int8":
            model = model.half().quantize(8).cuda()
        elif cmd_opts.precision == "fp32":
            model = model.float()

    model = model.eval()


def load_model():
    from transformers import LlamaForCausalLM, LlamaTokenizer, GenerationConfig
    from peft import PeftModel
    global tokenizer, model, generation_config

    generation_config = GenerationConfig(
        temperature=0.2,
        top_p=0.75,
        num_beams=5,
    )

    tokenizer = LlamaTokenizer.from_pretrained(cmd_opts.llama_path)
    model = LlamaForCausalLM.from_pretrained(
        cmd_opts.llama_path
    )
    model = PeftModel.from_pretrained(model, cmd_opts.model_path)
    prepare_model()



def generate_prompt(instruction, input=None):
    if input:
        return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:"""
    else:
        return f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:"""



def infer(prompt, query):
    global generation_config, tokenizer
    if not model:
        raise "Model not loaded"
    if not tokenizer:
        raise "Tokenizer not loaded"
    if not generation_config:
        raise "Generation config not loaded"

    prompt = generate_prompt(prompt, query)
    inputs = tokenizer(prompt, return_tensors="pt")
    input_ids = inputs["input_ids"].cuda()

    try:
        generation_output = model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=256
        )
        for s in generation_output.sequences:
            output = tokenizer.decode(s)
            return output.split("### Response:")[1].strip()
    except Exception as e:
        print(f"回复生成失败: {repr(e)}")
    print("")
    torch_gc()


def validate_answer(answer, response):
    # validate generated by judging is all the character in response are appeared in answer
    # if not, then the answer is not valid
    badcase = ['很抱歉', '非常抱歉']
    if any([bad in answer for bad in badcase]):
        return False

    reg_ch_and_eng = re.compile(r'[\u4e00-\u9fa5a-zA-Z]')
    reg_ch_and_eng_punc = r'[，。？！：；“”‘’《》、,.?!:;\'\"]'

    common_used_redundancy_pattern = [r'非常感谢您的(查询结果|回答)' + reg_ch_and_eng_punc, r'您的(答案|回答|查询结果)(是正确的|非常准确|非常正确)' + reg_ch_and_eng_punc]
    for pattern in common_used_redundancy_pattern:
        response = re.sub(pattern, '', response)

    response = ''.join(reg_ch_and_eng.findall(response))
    err_cnt = 0
    for c in response:
        if c not in answer:
            err_cnt += 1
    if err_cnt < 2 or err_cnt / len(answer) < 0.3:
        return True
    else:
        return False
