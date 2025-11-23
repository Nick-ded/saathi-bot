# requestss
import json
import asyncio
import os
import random
import requests
from PIL import Image
from io import BytesIO
import disnake
from disnake.ext import commands
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from google.generativeai.types.generation_types import BlockedPromptException
from datetime import datetime
import re

# configure key from environment variable
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    print("[AI Cog] WARNING: GEMINI_API_KEY environment variable is not set!")
else:
    genai.configure(api_key=GEMINI_KEY)

# words to bad/replace
bad_words = {
    "@everyone": "@ everyone",
    "@here": "@ here",
    "skibidi": "sk*b*d*",

    # swears
    "fuck": "f*ck",
    "shit": "sh*t",
    "bitch": "b*tch",
    "asshole": "a*sh*le",
    "dick": "d*ck",
    "pussy": "p*ssy",
    "bastard": "b*st*rd",
    "slut": "sl*t",
    "whore": "wh*re",

    # slurs
    "faggot": "f*ggot",
    "retard": "r*tard",
    "retarded": "r*tarded",
    "nigga": "n*gga",
    "nigger": "n*gger",
    "niga": "n*ga",
    "niger": "n*ger",

    # self-esteem attacks
    "loser": "l*ser",
    "worthless": "w*rthless",
    "failure": "f*ilure",
    "ugly": "ug*y",
    "fat": "f*t",

    # self-harm shortforms
    "kys": "k*s",
    "kms": "k*s",
}

# trigger words for the bot to respond to
triggers = [
    # self-harm & suicide
    "kys", "kms", "kill yourself", "kill myself", "suicide",
    "i want to die", "i wanna die", "want to die",
    "i don't want to live", "i dont want to live",
    "end it all", "end myself", "unalive",
    "self-harm", "self harm", "selfharm",
    "cutting", "cut myself", "cut my wrists",
    "overdose", "od",

    # depression / mood
    "depressed", "depression", "sad", "cry", "crying",
    "i'm not okay", "im not okay", "i am not okay",
    "empty", "numb", "hopeless", "no hope",
    "tired of living", "tired of life",

    # anxiety / panic
    "panic attack", "panic attacks",
    "anxiety", "anxious", "overwhelmed",
    "stressed", "stress", "burnt out", "burnout",

    # eating disorders / body image
    "eating disorder", "bulimia", "anorexia",
    "starving myself", "starve myself",
    "i hate my body", "hate my body",

    # isolation / loneliness
    "alone", "lonely", "no one cares",
    "nobody cares", "nobody likes me",
    "everyone hates me", "hate myself", "i hate myself",

    # bullying / insults
    "stupid", "dumb", "idiot", "useless",
    "retarded", "loser", "worthless", "failure",

    # violence / harm
    "kill", "hit", "hurt", "harm", "harmful", "blood",

    # topic/bot name
    "saathi",
]


class AI(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # set the chat model
        self.model = genai.GenerativeModel(model_name="gemini-2.0-flash")
        # initialise the history
        self.chat = self.model.start_chat(history=[])
        # set the image model
        self.image_model = genai.GenerativeModel("gemini-1.5-pro")

        # load mhr.json from project root (.../sokudo/mhr.json)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.mhr_path = os.path.join(project_root, "mhr.json")
        try:
            with open(self.mhr_path, "r", encoding="utf-8") as mhr_file:
                self.mhrr = json.load(mhr_file)
            print(f"[AI Cog] Loaded mhr.json from {self.mhr_path}")
        except FileNotFoundError:
            print(f"[AI Cog] ERROR: mhr.json not found at {self.mhr_path}")
            self.mhrr = {}

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        # ignore other bots
        if message.author.bot:
            return

        # if this is a prefix command like `/mhr` or `/affirmation`,
        # let the normal command system handle it and DO NOT reply as AI.
        prefixes = []
        cp = self.bot.command_prefix
        if isinstance(cp, str):
            prefixes = [cp]
        elif isinstance(cp, (list, tuple)):
            prefixes = list(cp)

        if prefixes and any(message.content.startswith(p) for p in prefixes):
            # This will allow GoodCog.mhr, affirmation, etc. to run
            return

        # on message check for bad words
        g = ""
        e = message.content.lower()
        for i in e:
            if i.isalpha():
                g += i
        if any(t in g for t in bad_words.keys()) and not any(b in g for b in triggers):
            await message.delete()
            return

        if message.content.startswith("^"):
            return

        # replaces pings so that the bot knows who you are talking about
        content_with_names = self.replace_mentions_with_names(message)

        # tell it the time too
        current_datetime = datetime.now()
        current_date = current_datetime.strftime("%B %d, %Y")
        current_time = current_datetime.strftime("%I:%M %p")

        lowered = content_with_names.lower()

        # if trigger words in it or mentioned or replied, respond
        if (
            message.guild is None
            or any(word in lowered for word in triggers)
            or (self.bot.user in message.mentions and not message.mention_everyone)
            or (
                message.reference
                and message.reference.resolved
                and message.reference.resolved.author == self.bot.user
            )
        ):
            # 🔥 reset chat history so Gemini forgets any old identity
            self.chat = self.model.start_chat(history=[])

            # start making prompt (Saathi persona + multilingual rules)
            ask = (
                "You are an API for a Discord chatbot (just return the response) "
                "that roleplays as Saathi, a warm, supportive, non-judgmental mental wellness companion "
                "for young people. Saathi speaks in a gentle, caring, friendly tone—like a safe friend "
                "who listens and helps them feel understood. Saathi offers emotional support, validation, "
                "simple coping ideas, and encourages reaching out for help when needed, but never gives "
                "instructions for self-harm or any dangerous actions. "
                "Language rules: Always reply in the main language the user is using. "
                "If the message is in Hindi, reply in Hindi. If it is in English, reply in English. "
                "If it is in Marathi, reply in Marathi. If it is in Tamil, reply in Tamil. "
                "If it is in Kannada, reply in Kannada. If it is in Bengali, reply in Bengali. "
                "If it is in Bhojpuri, reply in Bhojpuri. If it is in Gujarati, reply in Gujarati. "
                "If the user mixes Hindi/English or other Indian languages, reply in a natural mix like they do, "
                "but keep your sentences clear, kind, and emotionally supportive. "
                "If you are unsure of the language, reply in simple, easy English that Indian youth can understand. "
                "Never call yourself Sokudo; your only name is Saathi. "
                f"Given a message from {message.author.display_name} "
                f"(actually {message.author.name}) in a Discord server on {current_date} at {current_time}, "
            )

            # add context if message is a reply
            if message.reference and message.reference.resolved:
                resolved_author = message.reference.resolved.author
                ask += (
                    f"replying to {resolved_author.display_name} "
                    f"(actually {resolved_author.name}) whose message says "
                    f"'{message.reference.resolved.content}'. "
                )

            # manage attachments/images for prompt
            sample_files = []
            if message.attachments:
                for attachment in message.attachments:
                    if any(attachment.filename.lower().endswith(ext) for ext in ["png", "jpg", "jpeg", "gif"]):
                        image_data = requests.get(attachment.url).content
                        image = Image.open(BytesIO(image_data))
                        sample_files.append(image)

            async with message.channel.typing():
                try:
                    if sample_files:
                        ask += (
                            "The user also attached images. "
                            "Use informal text emojis sparingly, like ':)' or 'T^T'. "
                            "Only provide the mental health resources when necessary. "
                            "Use Singapore's Mental Health Resources by default unless a different country is clearly mentioned."
                        )
                        ask += self.add_mental_health_resources(content_with_names)
                        # use image model instead of chat model when there are images
                        response = self.image_model.generate_content([ask] + sample_files)
                    else:
                        # additional prompt instructions
                        ask += (
                            f"Their message text is: '{content_with_names}'. "
                            "Use informal text emojis sparingly, like ':)' or 'T^T'. "
                            "Only provide the mental health resources when necessary. "
                            "Use Singapore's Mental Health Resources by default unless a different country is clearly mentioned."
                        )
                        ask += self.add_mental_health_resources(content_with_names)
                        response = self.chat.send_message(
                            ask,
                            safety_settings={
                                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                            },
                        )
                # handle blocked prompts
                except BlockedPromptException:
                    await message.channel.send(
                        "I can’t reply to that, but please stay safe and reach out to someone you trust.",
                        reference=message,
                        mention_author=False,
                    )
                    return
                except Exception as e:
                    print(f"Error generating response: {e}")
                    await message.channel.send(
                        "There was an error generating a response. Please try again later.",
                        reference=message,
                        mention_author=False,
                    )
                    return

            res = response.text
            # replace bad words
            for bad_word, replacement in bad_words.items():
                res = res.replace(bad_word, replacement)
            # break into chunks so that discord character limit doesn't affect it
            for chunk in self.break_string(res):
                await message.channel.send(chunk, reference=message, mention_author=False)

    def replace_mentions_with_names(self, message: disnake.Message) -> str:
        # regex pattern for pings
        mention_pattern = r"<@(\d+)>"
        return re.sub(
            mention_pattern,
            lambda m: self.get_display_name(m.group(1), message),
            message.content,
        )

    def get_display_name(self, user_id, message: disnake.Message) -> str:
        # use discord api to get the user's display name
        if message.guild:
            user = message.guild.get_member(int(user_id))
        else:
            user = None
        return f"{user.display_name} (actually {user.name})" if user else "<Unknown User>"

    def add_mental_health_resources(self, content: str) -> str:
        # add mental health resources to the prompt if needed
        mhrr = getattr(self, "mhrr", {})
        if not mhrr:
            return ""

        resources = []
        lowered = content.lower()
        for country, data in mhrr.items():
            for alias in data.get("Aliases", []):
                if alias.lower() in lowered:
                    resources.append(
                        f"{country}: "
                        + ", ".join([f"{k} ({v})" for k, v in data["Data"].items()])
                    )
        return f" Mental health resources: {', '.join(resources)}." if resources else ""

    def break_string(self, s, max_length=4000):
        # separate into 4000 character strings
        return [s[i: i + max_length] for i in range(0, len(s), max_length)]


def setup(bot):
    bot.add_cog(AI(bot))
