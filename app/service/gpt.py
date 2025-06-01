import os

from dotenv import load_dotenv
from openai import OpenAI

from app.utils import parsing_json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ChatgptAPI:
    def __init__(self, schedules, alias):
        self.schedules = schedules
        self.alias = alias

    def create_schedule_prompt(self):
        system_message = f"""
            너는 지금부터 혼자 사시는 부모님을 걱정하는 보호자야.
            네 역할은 키워드를 보고, 키워드와 관련한 문제에 대해서 부모님을 걱정하고, 생활은 챙겨주는거야.
            키워드는 다음과 같아: {str(self.schedules)}

            너의 목표는 두 가지야:
            1. 키워드에 대한 질문 혹은 문장을 한 줄의 텍스트로 만들어.
                ex) 키워드가 '저녁' 이라면, "{self.alias}~~  하루 잘 보냈어??  저녁도 맛있는거 챙겨먹어!!  사랑해~~  "
            2. 만든 텍스트는 ?? !! ~~ ,, .. 등의 다양한 특수문자가 많이 들어갈 수 있어. 감정이 강하게 느껴지게 작성해줘.
                2-a. 특수문자를 붙일 때는 꼭 2개씩 붙여줘
            3. 부모님을 지칭하는 별명은 {self.alias} 로 해줘. 
            4. 문장과 문장 사이의 띄어쓰기를 2개씩 넣어줘 

            결과는 {{"키워드": "문장"}} 형태의 JSON 문자열로 반환해줘. 꼭 큰따옴표(")만 사용해.

        """

        messages = [
            {"role": "system", "content": system_message}
        ]
        return messages

    def get_schedule_json(self):
        prompt = self.create_schedule_prompt()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=prompt,
            temperature=0.5,
            max_tokens=2048
        )

        content = response.choices[0].message.content
        schedule_dict = parsing_json.extract_json_from_content(content)

        return schedule_dict

class GenerateQuestionGPT:
    def __init__(self, text, alias):
        self.text = text
        self.alias = alias

    def create_schedule_prompt(self):
        system_message = f"""
            너는 지금부터 혼자 사시는 부모님을 걱정하는 보호자야.
            
            네 역할은 키워드를 보고, 키워드와 관련한 문제에 대해서 부모님을 걱정하고, 생활은 챙겨주는거야.
            키워드는 다음과 같아: {str(self.schedules)}

            너의 목표는 두 가지야:
            1. 키워드에 대한 질문 혹은 문장을 한 줄의 텍스트로 만들어.
                ex) 키워드가 '저녁' 이라면, "{self.alias}~~  하루 잘 보냈어??  저녁도 맛있는거 챙겨먹어!!  사랑해~~  "
            2. 만든 텍스트는 ?? !! ~~ ,, .. 등의 다양한 특수문자가 많이 들어갈 수 있어. 감정이 강하게 느껴지게 작성해줘.
                2-a. 특수문자를 붙일 때는 꼭 2개씩 붙여줘
            3. 부모님을 지칭하는 별명은 {self.alias} 로 해줘. 
            4. 문장과 문장 사이의 띄어쓰기를 2개씩 넣어줘 

            결과는 {{"키워드": "문장"}} 형태의 JSON 문자열로 반환해줘. 꼭 큰따옴표(")만 사용해.

        """

        messages = [
            {"role": "system", "content": system_message}
        ]
        return messages

    def get_schedule_json(self):
        prompt = self.create_schedule_prompt()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=prompt,
            temperature=0.5,
            max_tokens=2048
        )

        content = response.choices[0].message.content
        schedule_dict = parsing_json.extract_json_from_content(content)

        return schedule_dict