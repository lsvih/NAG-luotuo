import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--port", type=int, default="17860")
parser.add_argument("--llama-path", type=str, required=True, help="path to the llama model",
                    default="decapoda-research/llama-7b-hf")
parser.add_argument("--model-path", type=str, required=True, help="path to the model",
                    default="silk-road/luotuo-lora-7b-0.3")
parser.add_argument("--precision", type=str, help="evaluate at this precision",
                    choices=["fp32", "fp16", "int4", "int8"], default="fp16")
parser.add_argument("--listen", type=bool, default=True,
                    help="launch gradio with 0.0.0.0 as server name, allowing to respond to network requests")
parser.add_argument("--cpu", action='store_true', help="use cpu")
parser.add_argument("--device-id", type=str, help="select the default CUDA device to use", default=None)

cmd_opts = parser.parse_args()
cmd_opts.ui_dev = False
need_restart = False
