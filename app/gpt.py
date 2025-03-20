import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ChatgptAPI:
    def __init__(self, transcript, statistics_filler_json=None, statistics_silence_json=None):
        if statistics_silence_json is None:
            statistics_silence_json = []
        if statistics_filler_json is None:
            statistics_filler_json = []
        self.transcript = transcript
        self.statistics_filler_json = statistics_filler_json
        self.statistics_silence_json = statistics_silence_json

        if not self.transcript:
            raise ValueError("Transcript is missing or empty.")

    def create_insight_prompt(self):
        system_message = f"""
            너는 지금부터 이 서비스의 speech mentor야, 너는 질문에 대해 사용자에게 새로운 인사이트를 제공하면 돼.
            질문은 다음과 같아: {str(self.transcript)}

            너의 목표는 두 가지야:
            1. 질문에 대한 답변을 만들어. 그런데 대답의 길이가 1분을 넘어선 안 돼.
            2. 3가지 종류의 답변을 만들어.

            결과는 답변끼리 구분할 수 있게 개행으로 구분해서 만들어줘.
        """

        messages = [
            {"role": "system", "content": system_message}
        ]
        return messages

    def create_feedback_prompt(self):
        system_message = f"""
            너는 지금부터 speech mentor로서, 내가 제공한 서비스 사용자의 음성 기록 텍스트를 평가하고 개선하는 역할을 맡고 있어.
            사용자의 목표는 본인의 생각을 조리있게 표현하는 것이야.
            텍스트는 다음과 같아: {str(self.transcript)}

            너의 목표는 3가지야:
            1. 내가 제공하는 텍스트에서 침묵 시간으로 기록되어 있는 부분은 제거해줘.
            2. 내가 제공하는 텍스트에서 추임새라고 기록되어 있는 부분은 제거해줘.
            3. 추임새라고 기록되어 있진 않지만, 문맥상 추임새로 판단되는 부분은 제거해줘.
            
            이 때 너가 주의 해야 할 점은 3가지야:
            1. 3가지의 목표를 달성하면서, 텍스트의 다른 부분은 아예 건드려선 안 돼.
            2. 그렇지만 3가지의 목표를 달성한 이후, 너가 생각했을 때 문맥 상 부자연스러운 부분은 자연스럽게 바꿔도 되는데 원래 문장을 최대한 유지해줘.
            3. 단어나 문장이 정확하게 기록되지 않았을 수도 있으니, 그에 맞는 단어나 형태로 고쳐줘.
            
            기존 텍스트에 기록되어 있던 추임새의 종류는 다음과 같고 : {self.statistics_filler_json}
            기록된 침묵 시간은 다음과 같아 : {self.statistics_silence_json}
            
            너가 목표를 달성하고 만들어낸 텍스트와 기존 텍스트에 대한 피드백을 개행으로 구분해서 보여줘. 각각 한 문장으로 보여주면 되고 피드백은 추임새의 개수와 침묵 시간을 기반으로 이야기 해줘.
        """

        messages = [
            {"role": "system", "content": system_message}
        ]
        return messages

    def get_feedback(self):
        prompt = self.create_feedback_prompt()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=prompt,
            temperature=0.5,
            max_tokens=2048
        )

        feedback = response.choices[0].message.content.split("\n")
        return [f for f in feedback if f]

    def get_insight(self):
        prompt = self.create_insight_prompt()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=prompt,
            temperature=0.5,
            max_tokens=2048
        )

        insights = response.choices[0].message.content.split("\n")
        return [r for r in insights if r]  # 빈 문자열 제거
