#Re:Ka B:ot GOLD 1.0.0
import discord
import openai
from discord.ext import commands
import os

# .env 파일 로드
load_dotenv() #.env.example 과 같은 형식으로 .env 파일을 만들어야 됩니다.

TOKEN = os.getenv("DISCORD_TOKEN") #.env.example 에서 디스코드 토큰을 가지고 옵니다.
openai.api_key = os.getenv("OPENAI_API_KEY")#.env.example 에서 openAI API를 가지고 옵니다.

# 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/ ', intents=discord.Intents.all(), help_command=None)

# 사용자별 대화 기록 저장
user_conversations = {}

# 봇 가동
@bot.event
async def on_ready():
    print(f'Re:Ka B:ot-{bot.user} 가동!')
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("현재 하고 있는 활동"))
    await bot.tree.sync()

# GPT 응답 생성 함수
async def get_gpt_response(message, user_id):
    try:
        # 사용자별 대화 기록 초기화
        if user_id not in user_conversations:
            user_conversations[user_id] = []

        # 대화 기록에 사용자 메시지 추가
        user_conversations[user_id].append({"role": "user", "content": message})

        recent_conversation = user_conversations[user_id][-15:] #이 코드로 봇의 기억력(봇이 기억하는 메세지의 개수)를 정할 수 있습니다. PRESET : 15 봇이 재부팅 될 때, 봇의 기억은 초기화됩니다.

        prompt = f"봇에게 자신이 누구인지 알려주는 말투의 봇에 대한 설명\n\n{conversation}\nGPT의 대답:" #자세히 적으세요.

        # GPT 응답 받기 (ChatCompletion API로 변경)
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini", #GPT 모델입니다. 1분당 감당할 수 있는 openAI 토큰이 많은 gpt-4o-mini를 추천드립니다.
            messages=[
                {
                    "role": "system",
                    "content": (
                      #이 부분에는 위 40번 째 줄 prompt에 적은 내용을 자세하게 적어주세요
                        "아주 자세한 봇에 대한 설명 1"
                        "아주 자세한 봇에 대한 설명 2"
                        "아주 자세한 봇에 대한 설명 3"
                        "아주 자세한 봇에 대한 설명 4"
                        "아주 자세한 봇에 대한 설명 1"
                        "아주 자세한 봇에 대한 설명 5"
                        "..."
                    )
                }
            ] + recent_conversation,
            max_tokens=2000, #봇이 한 번에 몇 글자만큼 대답할 수 있는지 조절합니다. 2000을 추천드립니다.
            temperature=0.5  #봇의 창의성을 조절하는 부분입니다. 형식적인 봇은 0.5, 유쾌한 봇은 0.8~1.0을 추천드립니다.
        )
        

        gpt_response = response['choices'][0]['message']['content'].strip()

        # 대화 기록에 봇 응답 추가
        user_conversations[user_id].append({"role": "assistant", "content": gpt_response})

        return f'"{message}"에 대한 답변:\n{gpt_response}'
    except Exception as e:
        print(f"Error occurred: {e}")  # 에러 출력
        return f"에러 발생: {str(e)}"  # 에러 메시지 반환

# Slash Command 등록하기
@bot.tree.command(name="대화하기", description="(봇 이름)와 대화하기")
async def conversation(interaction: discord.Interaction, message: str):
    # GPT로부터 응답 받기
    response = await get_gpt_response(message, interaction.user.id)
    
    # 사용자에게 응답 보내기
    await interaction.response.send_message(response, ephemeral=True)
    
@bot.tree.command(name="정보", description="(봇 이름)(Re:Ka B:ot)의 정보 보기")
async def info(interaction: discord.Interaction):  
    try:
        # 엔진 정보 임베드 생성                                                                #건드리지 마세요 (엔진 개발자 명시는 필수입니다!)
        engine_embed = discord.Embed                                                          #건드리지 마세요
            title="엔진 정보",                                                                #건드리지 마세요
            description="(봇 이름)의 기반이 되는 엔진의 정보입니다.",                           
            color=discord.Color.gold()                                                        #건드리지 마세요
        )
        engine_embed.add_field(name="엔진", value="Re:Ka B:ot", inline=False)                  #건드리지 마세요 
        engine_embed.add_field(name="버전", value="GOLD 1.0.0", inline=False)                 #건드리지 마세요
        engine_embed.add_field(name="제작자", value="poshil(GREENPOEM)", inline=False)           #건드리지 마세요

        # 봇 정보 임베드 생성
        bot_embed = discord.Embed(
            title="(봇 이름)의 정보",
            description="(봇 이름)(봇)의 정보입니다.",
            color=discord.Color.blue()
        )
        bot_embed.add_field(name="이름", value="(봇 이름)", inline=False)  #아래 내용은 원하시는 대로 변경하세요
        bot_embed.add_field(name="나이", value="(값)", inline=False)
        bot_embed.add_field(name="성별", value="(값)", inline=False)
        bot_embed.add_field(name="...", value="...", inline=False)

        # 초대 버튼 생성
        view = discord.ui.View()
        button = discord.ui.Button(
            label="(봇 이름) 내 서버에 초대하기",
            url="디스코드 developer portal에서 발급받은 초대링크",
            style=discord.ButtonStyle.link
        )
        view.add_item(button)

        # 응답으로 임베드와 버튼 전송
        await interaction.response.send_message(embed=engine_embed, ephemeral=True)
        await interaction.followup.send(embed=bot_embed, view=view, ephemeral=True)
    except Exception as e:
        # 예외 발생 시 오류 메시지 출력 및 사용자 알림
        print(f"Error in /정보 command: {e}")
        await interaction.response.send_message(
            "에러가 발생했습니다. 다시 시도해주세요.",
            ephemeral=True
        )
    
# 봇 실행
bot.run('TOKEN') #건드리지 마세요 (여기에 자신의 디스코드 토큰을 넣지 마세요. .env 파일에 넣으세요)
