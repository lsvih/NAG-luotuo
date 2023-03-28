import gradio as gr

from modules.model import infer, validate_answer


def predict(q, res):
    instruction = """现在起你是一个将结构化输出转换为回复的机器人，根据用户的提问以及给出的结构化的答案，不要复述问题、不要质疑、不要试图交互、不要试图纠正用户。
    根据下面的问题和查询结果生成正确、简洁、客观、流畅的自然语言回复。"""
    query = f'{q}\n查询结果:{res}'

    max_query = 5
    query_cnt = 0
    print(query)
    while query_cnt <= max_query:
        query_cnt += 1
        answer = infer(instruction, query=query)
        print('生成次数：' + str(query_cnt) + '\t' + answer)
        if validate_answer(answer, res):
            return answer
    # Fallback:
    return "查询得到的结果是：" + res + "，但我不知道怎么回答你的问题。"


def create_api():
    interface = gr.Interface(fn=predict, inputs=["text", "text"], outputs="text")
    return interface
