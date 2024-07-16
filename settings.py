# ----------
# Imports
# ----------
import asyncio
import colorsys
import hashlib
import math
import os
import random
import re
import string
import sys
import threading
import traceback
import warnings
from pathlib import Path

import PIL
import requests
import ujson
from colorama import Fore, init
from discord.ext import commands
from dotenv import load_dotenv
from PIL import (
    GifImagePlugin,
    Image,
    ImageColor,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageOps,
    ImageSequence,
)

# ----------
# Variables, Please follow the naming scheme across all (CONFIG) variables for clarity and consistency sake. Idgaf what you do for the functions.
# ----------

# Bot configuration
PREFIXES = {"d.", "#", "D.", "ratio + "}
TOKEN = os.getenv("TOKEN")
TEAM_IDS = {
    343224184110841856,
    158418656861093888,
    249411048518451200,
}  # User IDs for people with unrestricted bot access
DENIAL_RATIO = (
    250  # (1/X) Chance to deny a command from going through, where X is the variable
)
DENIAL_RESPONSES = {"no", "nah", "nope", "no thanks"}
CURRENT_DIR = os.getcwd()
CACHE_CLEAR_ON_LAUNCH = True  # If true, the bots cache will clear on launch
CLEAN_POOTER_ON_LAUNCH = (
    True  # If true, Pooter will go through and delete any duplicates on launch
)
ACCEPTED_FILES = {"png", "jpg", "jpeg", "gif", "webp", "mp4", "webm", "mov"}
CMD_BLACKLIST = ["0"]

# Server whitelist
WHITELIST = {779136383033147403}

# Image manipulation configuration, these are typically only used for commands that generate text, as its easier to get it looking right if we limit the possible range of resolution
IMAGE_LOWER = 250  # The lower limit for the dimensions of an image, will scale to this size if below
IMAGE_UPPER = 1500  # The upper limit for the dimensions of an image, will scale to this size if above

# Channel configurations
BOOKMARKS_CHANNEL = int(os.getenv("BOOKMARKS"))
LOGS_CHANNEL = int(os.getenv("LOGS"))

# API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
TENOR_API_KEY = os.getenv("TENOR_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("AV_API_KEY")

# Internal paths
YTDL_COOKIES_PATH = f"{CURRENT_DIR}\\assets\\cookies.txt"

# 8ball responses
BALL_RESPONSES = {
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes - definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful.",
    "yeah",
    "nah",
}

# Logo list for the logo command
LOGO_LIST = {
    "clan",
    "neon",
    "fluffy",
    "water",
    "smurfs",
    "style",
    "runner",
    "blackbird",
    "fabulous",
    "glow",
    "chrominium",
    "amped",
    "supermarket",
    "crafts",
    "fire",
    "steel",
    "glossy",
    "fifties",
    "retro",
    "beauty",
    "birdy",
    "inferno",
    "winner",
    "uprise",
    "global",
    "silver",
    "minions",
    "magic",
    "fancy",
    "orlando",
    "fortune",
    "swordfire",
    "roman",
    "golden",
    "outline",
    "funtime",
}

# Characters for the undertext command
DELTARUNE_CHARACTERS = {
    "ralsei",
    "lancer",
    "king",
    "jevil",
    "queen",
    "spamton",
    "clyde",
    "lori",
    "rhombo",
}

# ----------
# Functions
# ----------


def generate_id():
    """
    Generates a random ID within a really fucking big range so we don't get a duplicate.

    Returns:
        int: A randomly generated ID.
    """
    return random.randint(0, 9999999999999)


def unpack_gif(file, id):
    """
    This function unpacks each frame of a provided GIF file and saves them as PNG images
    in a directory specified by a unique ID.

    Parameters:
    file (str): The file path of the GIF to be unpacked.
    id (int): A unique identifier used to create the directory for storing the unpacked frames.
    """
    print(
        Fore.LIGHTMAGENTA_EX + "unpacking gif..." + Fore.RESET
    )  # Display message indicating the start of the unpacking process

    # We make the directory we're going to unpack to here
    directory = f"{CURRENT_DIR}/cache/ffmpeg/{id}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # FFMPEG command to unpack the frames into the directory
    os.system(f'ffmpeg -i "{file}" -vf fps=25 -vsync 0 "{directory}/temp%04d.png" -y')
    return


def repack_gif(id):
    """
    This function repacks the unpacked frames into a GIF file using a palette generated from the images.

    Parameters:
    id (int): A unique identifier used to locate the directory containing the unpacked frames.
    """
    print(
        Fore.LIGHTMAGENTA_EX + "generating palette..." + Fore.RESET
    )  # Display message indicating the palette generation

    # We're setting up all of our directories here
    directory = f"{CURRENT_DIR}/cache/ffmpeg/{id}"
    palette_path = f"{directory}/palette.png"
    output_gif = f"{CURRENT_DIR}/cache/ffmpeg_output{id}.gif"

    # FFMPEG command to generate an optimal paletee based on the frames
    os.system(
        f'ffmpeg -i "{directory}/temp%04d.png" -lavfi "scale=256x256,fps=25,palettegen=max_colors=256:stats_mode=diff" "{palette_path}" -y'
    )
    print(
        Fore.LIGHTMAGENTA_EX + "repacking gif..." + Fore.RESET
    )  # Display message indicating the start of the repacking process

    # FFMPEG command to repack the frames into a GIF
    os.system(
        f'ffmpeg -i "{directory}/temp%04d.png" -i "{palette_path}" -lavfi "fps=25,mpdecimate,paletteuse=dither=none" -fs 99M "{output_gif}" -y'
    )
    shutil.rmtree(directory)  # Delete the unpacked frames as we no longer need them
    print(Fore.LIGHTMAGENTA_EX + f"Deleted directory {directory}" + Fore.RESET)
    return


def randhex(bits):
    """
    Generates a random hexadecimal string of specified length in bits.

    Args:
        bits (int): Number of bits for the hexadecimal string.

    Returns:
        str: A random hexadecimal string.
    """
    num_bytes = (bits + 3) // 4  # Calculate number of bytes needed
    random_number = random.getrandbits(
        bits
    )  # Generate random number with the passed arg as the length
    random_hex = hex(random_number)[2:].zfill(
        num_bytes
    )  # Convert to hexadecimal string
    return random_hex


def clear_cache():
    """
    Clears the cache folder of all files and subdirectories using threading.
    """
    cache_folder = Path(f"{CURRENT_DIR}/cache")

    def clear_files(folder):
        """
        Recursively clears files and subdirectories within the given folder.
        """
        for file_path in folder.glob("*"):
            try:
                if file_path.is_file():
                    os.remove(file_path)  # Delete the file
                    print(
                        Fore.LIGHTMAGENTA_EX + f"Deleted file: {file_path}" + Fore.RESET
                    )
                elif file_path.is_dir():
                    for sub_file in file_path.glob("**/*"):
                        if sub_file.is_file():
                            os.remove(sub_file)  # Delete each file in subdirectory
                            print(
                                Fore.LIGHTMAGENTA_EX
                                + f"Deleted file: {sub_file}"
                                + Fore.RESET
                            )
                    os.rmdir(file_path)  # Remove the directory itself
                    print(
                        Fore.LIGHTMAGENTA_EX
                        + f"Deleted folder: {file_path}"
                        + Fore.RESET
                    )
            except OSError as e:
                print(Fore.YELLOW + f"Failed to delete {file_path}: {e}" + Fore.RESET)
                continue

    # Using threading for potentially large directories
    thread = threading.Thread(target=clear_files, args=(cache_folder,))
    thread.start()
    thread.join()

    print(Fore.BLUE + "Cache cleared." + Fore.RESET)


def is_float(value):
    """
    Checks if a given value can be converted to a float. This seems fucking stupid to me and it probably is.

    Args:
        value (any): The value to be checked.
    """
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_folder_size(folder):
    """
    Calculates the total size of all files in a folder.

    Args:
        folder (str): The path to the folder.

    Returns:
        str: A string representing the total size with appropriate units (bytes, KB, MB, GB, TB).
    """
    total_size = 0

    # Walk through all directories and files in the given folder
    for root, _, filenames in os.walk(folder, topdown=False):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            # Calculate the total size by summing up each file's size
            total_size += os.path.getsize(file_path)

    # Define units for displaying file size
    units = ["bytes", "KB", "MB", "GB", "TB"]

    # Determine the appropriate unit to use based on the total size
    unit_index = min(len(units) - 1, int(math.floor(math.log(total_size, 1024))))
    total_size /= 1024**unit_index

    # Format the output string with two decimal places
    return f"{total_size:.2f} {units[unit_index]}"


def undertext(name, text, isAnimated):
    """
    Format the URL for our Undertale text box generator and inject custom sprites or styles as needed.

    Args:
    - name (str): The character name or link.
    - text (str): The text associated with the character.
    - isAnimated (bool): Indicates if the text is animated.
    """
    # animated override: if the name contains "animated-", remove it and set isAnimated to True
    if text.endswith("True"):
        text = text[:-4]
        isAnimated = True

    # AU style overrides: if the name contains a valid AU, add the AU style to the name and text
    if "uf" in name:  # underfell
        name = f"{name}&boxcolor=b93b3c&asterisk=b93b3c&charcolor=b93b3c"
        text = f"color=%23b93b3c%20{text}"
    if name in deltarune_dw:  # deltarune
        name = f"{name}&box=deltarune&mode=darkworld"

    # character overrides: replace underscores with dashes, then use the dictionary to replace the name with the link
    character_links = {
        "danny": "https://cdn.discordapp.com/attachments/560608550850789377/1005989141768585276/dannyportrait1.png",
        "danny-funny": "https://cdn.discordapp.com/attachments/560608550850789377/1005999509496660060/dannyportrait3.png",
        "danny-angry": "https://cdn.discordapp.com/attachments/560608550850789377/1005989142825553971/dannyportrait4.png",
        "danny-pissed": "https://cdn.discordapp.com/attachments/560608550850789377/1005989142083145828/dannyportrait2.png",
        "crackhead": "https://cdn.discordapp.com/attachments/1063552619110477844/1076067803649556480/image.png",
        "pizzi": "https://cdn.discordapp.com/attachments/1063552619110477844/1082228005256044575/pizziportrait1.png",
        "pizzi-stare": "https://cdn.discordapp.com/attachments/1063552619110477844/1082228014856814612/pizziportrait2.png",
        "pizzi-scream": "https://cdn.discordapp.com/attachments/1063552619110477844/1082228022796615720/pizziportrait3.png",
        "sam": "https://cdn.discordapp.com/attachments/1063552619110477844/1082220603387428894/samportrait1.png",
        "flashlight": "https://cdn.discordapp.com/attachments/1063552619110477844/1068251386430619758/image.png",
        "ezo": "https://cdn.discordapp.com/attachments/1063552619110477844/1068251386430619758/image.png",
        "ezogaming": "https://cdn.discordapp.com/attachments/1063552619110477844/1068251386430619758/image.png",
        "incine": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552737435992084/FIncine.png",
        "cris": "https://cdn.discordapp.com/attachments/1063552619110477844/1063552816397951037/FCris.png",
        "seki": "https://cdn.discordapp.com/attachments/1063552619110477844/1063738177212399658/sekiportrait1.png",
        "seki-eyes": "https://cdn.discordapp.com/attachments/560608550850789377/1075684786489798696/sekiportrait2.png",
        "seki-evil": "https://cdn.discordapp.com/attachments/1063552619110477844/1075687740793946122/sekiportrait3.png",
        "leffrey": "https://cdn.discordapp.com/attachments/886788323648094219/1068253912919982100/image.png",
        "reimu-fumo": "https://cdn.discordapp.com/attachments/1063552619110477844/1082233613040504892/image.png",
        "suggagugga": "https://cdn.discordapp.com/attachments/1063552619110477844/1068248384164614154/mcflurger.png",
    }

    name = character_links.get(name, name)

    # link overrides: if the name starts with "https://", add "custom&url=" to the beginning of the name
    if name.startswith("http"):
        name = f"custom&url={name}"

    # text overrides: modify the box and text display based on passed parameters
    if "font=wingdings" in text:
        name = f"{name}&asterisk=null"

    # finalizing: set the name and text to the name and text, then return the name, text, and isAnimated
    name = name
    # replacing the discord double underscore shit with spaces
    text = text.replace("_ _", "%20")
    return name, text, isAnimated


def gettenor(gifid=None):
    """
    Retrieve the GIF URL from Tenor API based on the provided GIF ID.

    Parameters:
    gifid (str): The ID of the GIF to fetch from Tenor.

    Raises:
    KeyError: If the expected data structure from Tenor API is not found.
    """
    # get the api key from the config file
    apikey = tenor_apikey

    # make a GET request to Tenor API to fetch GIFs
    r = requests.get(
        "https://api.tenor.com/v1/gifs?ids=%s&key=%s&media_filter=minimal"
        % (gifid, apikey)
    )

    # check if the request was successful (status code 200)
    if r.status_code == 200:
        # parse the JSON response
        gifs = ujson.loads(r.content)
    else:
        gifs = None

    # return the URL of the first GIF in the results
    return gifs["results"][0]["media"][0]["gif"]["url"]


# this was brought directly over from the old dannybot, i will make no effort to explain, comment, or docstring it,
# because its a fucking mess and i forgot some of it, but it works as intended
async def resolve_args(ctx, args, attachments, type="image"):
    url = None
    tenor = False
    avatar = False
    text = " ".join(args)
    print(Fore.LIGHTMAGENTA_EX + "Resolving URL and arguments..." + Fore.RESET)

    extensions = {
        "image": ("png", "jpg", "jpeg", "gif", "bmp", "webp"),
        "audio": ("wav", "ogg", "mp3", "flac", "aiff", "opus", "m4a", "oga"),
        "midi": ("mid", "midi", "smf"),
        "video": ("mp4", "avi", "mpeg", "mpg", "webm", "mov", "mkv"),
        "3d": ("obj", "fbx", "stl", "dae"),
        "office": ("doc", "docx", "xls", "xlsx", "ppt", "pptx"),
        "text": ("txt", "rtf", "json"),
        "code": ("py", "java", "cpp", "c", "h", "html", "css", "js", "php", "cs", "rb"),
    }
    extension_list = [ext.lower() for ext in extensions.get(type, ())]

    # Helper function to ensure proper URL combination
    def combine_url(url_parts):
        return "?".join(filter(None, url_parts))

    # Grab a URL if the command is a reply to an image
    if ctx.message.reference:
        referenced_message = await ctx.fetch_message(ctx.message.reference.message_id)
        if "https://tenor.com/view/" in referenced_message.content and type == "image":
            tenor = True
            tenor_id = re.search(
                r"tenor\.com/view/.*-(\d+)", referenced_message.content
            ).group(1)
            url = gettenor(tenor_id)
            print(Fore.BLUE + f"URL from Tenor: {url}" + Fore.RESET)
        elif referenced_message.attachments:
            for attachment in referenced_message.attachments:
                if attachment.content_type.startswith(type):
                    url_parts = attachment.url.split("?")
                    url = combine_url(url_parts)
                    print(Fore.BLUE + f"URL from reply: {url}" + Fore.RESET)
                    break
        else:
            http_urls = re.findall(r"http\S+", referenced_message.content)
            if http_urls:
                http_url_parts = http_urls[0].split("?")
                ext = http_url_parts[0].split(".")[-1]
                if ext.lower() in extension_list:
                    url = combine_url(http_url_parts)
                    print(Fore.BLUE + f"URL from reply: {url}" + Fore.RESET)

    # Grab a URL if the command has an attachment
    if not url and attachments:
        for attachment in attachments:
            if attachment.content_type.startswith(type):
                url_parts = attachment.url.split("?")
                url = combine_url(url_parts)
                print(Fore.BLUE + f"URL from attachment: {url}" + Fore.RESET)
                break

    # Grab a URL passed from args
    if not url:
        if args and args[0].startswith("http"):
            if "https://tenor.com/view/" in args[0]:
                tenor = True
                tenor_id = re.search(r"tenor\.com/view/.*-(\d+)", args[0]).group(1)
                url = gettenor(tenor_id)
                print(Fore.BLUE + f"URL from Tenor: {url}" + Fore.RESET)
            else:
                url_parts = args[0].split("?")
                url = combine_url(url_parts)
                text = " ".join(args[1:])
                print(Fore.BLUE + f"URL from argument: {url}" + Fore.RESET)

        # Grab a URL from mentioned user's avatar
        if ctx.message.mentions:
            mentioned_member = ctx.message.mentions[0]

            if mentioned_member.guild_avatar:
                url = str(mentioned_member.guild_avatar.url)
                print(
                    Fore.BLUE + f"URL from avatar of mentioned user: {url}" + Fore.RESET
                )
                avatar = True
            else:
                url = str(mentioned_member.avatar.url)
                print(
                    Fore.BLUE + f"URL from avatar of mentioned user: {url}" + Fore.RESET
                )
                avatar = True

    # Message content iteration
    if not url:
        channel = ctx.message.channel
        async for msg in channel.history(limit=500):
            content = msg.content

            # Grab the URL from the last sent message's attachment
            for attachment in msg.attachments:
                attch_url_parts = attachment.url.split("?")
                ext = attch_url_parts[0].split(".")[-1]
                if ext.lower() in extension_list:
                    url = combine_url(attch_url_parts)
                    print(Fore.BLUE + f"URL from attachment: {url}" + Fore.RESET)
                    break
            if url:
                break

            # Grab the URL (tenor) from the last sent message
            if "https://tenor.com/view/" in content and type == "image":
                tenor = True
                tenor_id = re.search(r"tenor\.com/view/.*-(\d+)", content).group(1)
                url = gettenor(tenor_id)
                print(Fore.BLUE + f"URL from Tenor: {url}" + Fore.RESET)
                break

            # Grab the URL from the last sent message
            if type == "image":
                http_urls = re.findall(r"http\S+", content)
                if http_urls:
                    http_url_parts = http_urls[0].split("?")
                    ext = http_url_parts[0].split(".")[-1]
                    if ext.lower() in extension_list:
                        url = combine_url(http_url_parts)
                        print(
                            Fore.BLUE + f"URL from message content: {url}" + Fore.RESET
                        )
                        break

            # Generic URL extraction
            http_urls = re.findall(r"http\S+", content)
            if http_urls:
                http_url_parts = http_urls[0].split("?")[0]
                ext = http_url_parts.split(".")[-1]
                if ext.lower() in extension_list:
                    url = combine_url(http_url_parts)
                    print(Fore.BLUE + f"URL from message content: {url}" + Fore.RESET)
                    break

    try:
        if not avatar and isinstance(url, list):
            url = combine_url(url)
        text = re.sub(r"<@[^>]+>\s*", "", text)
    except Exception as e:
        # Handle any exceptions in URL processing
        print(Fore.RED + f"Error combining URL: {e}" + Fore.RESET)
    finally:
        print(Fore.CYAN + f"Arguments: {url}, {text}" + Fore.RESET)
        return [url, text]


def sanitize_filename(filename):
    """
    Sanitizes a filename to only contain valid characters for Windows file names.

    Args:
    - filename (str): The filename to sanitize.
    """
    valid_chars = string.ascii_letters + string.digits + "._- "
    sanitized_filename = "".join(char for char in filename if char in valid_chars)
    return sanitized_filename


def listgen(directory):
    """
    Generates a comma-separated string of filenames in a directory.
    This is carried over from when we had stable diffusion support, but I intended on bringing it back at some point, so it stays here.

    Args:
    - directory (str): The path to the directory.
    """
    files_list = os.listdir(directory)
    files_string = ", ".join(files_list)
    return files_string


def uwuify(input_text):
    """
    Converts input text into 'uwu' speak with some randomness and emoticons.
    This function applies a series of text transformations including case-insensitive
    replacements of specific substrings and occasional emoticon insertion.

    Args:
    - input_text (str): The text to 'uwuify'.
    """

    def case_agnostic_replace(text, old, new):
        result = ""
        i = 0
        while i < len(text):
            if text[i : i + len(old)].lower() == old.lower():
                result += text[i : i + len(old)].replace(old, new, 1)
                i += len(old)
            else:
                result += text[i]
                i += 1
        return result

    # Step-wise replacements
    modified_text1 = case_agnostic_replace(input_text, "l", "w")
    modified_text2 = case_agnostic_replace(modified_text1, "u", "uu")
    modified_text3 = case_agnostic_replace(modified_text2, "r", "w")
    modified_text4 = case_agnostic_replace(modified_text3, "the", "de")
    modified_text5 = case_agnostic_replace(modified_text4, "to", "tu")

    # Emoticons and additional replacements
    emoticons = ["^_^", ">w<", "x3", "^.^", "^-^", "(・ˋω´・)", "x3", ";;w;;"]
    words = modified_text5.split()
    output_text = []
    for i, word in enumerate(words):
        output_text.append(word)
        if i < len(words) - 1 and random.random() < 0.1:
            output_text.append(random.choice(emoticons))
    modified_text6 = " ".join(output_text)
    modified_text7 = case_agnostic_replace(modified_text6, "~", "")
    modified_text = case_agnostic_replace(modified_text7, "!", " !~ ")

    return modified_text


def clean_pooter():
    """
    Cleans up files in then Pooter directory by removing duplicates based on MD5 hash.

    This function iterates through files in the Pooter directory, calculates each file's MD5 hash,
    and deletes files that have identical hashes, keeping only one copy of each unique file.

    Raises:
        FileNotFoundError: If the Pooter directory does not exist.
    """
    directory_path = os.path.join(CURRENT_DIR, "database", "Pooter")

    # Check if directory exists
    if not os.path.exists(directory_path):
        logging.error(Fore.RED + "Pooter folder not found. Aborting." + Fore.RESET)
        return

    file_hashes = {}  # Dictionary to store file hashes
    lock = threading.Lock()  # Lock for thread-safe access to shared resources

    def calculate_file_hash(file_path, block_size=65536):
        """
        Calculates the MD5 hash of a given file.
        """
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(block_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def clean_file(file):
        """
        Cleans a file by checking its MD5 hash and deleting it if a duplicate is found.
        """
        nonlocal file_hashes
        file_path = os.path.join(directory_path, file)

        # Check if file has an extension (not a folder)
        if "." not in file:
            os.remove(file_path)  # Delete the file
            with lock:
                print(Fore.LIGHTMAGENTA_EX + f"Deleted: {file}" + Fore.RESET)
            return

        file_hash = calculate_file_hash(file_path)

        with lock:
            if file_hash in file_hashes:
                os.remove(file_path)  # Delete the file if duplicate hash found
                print(Fore.LIGHTMAGENTA_EX + f"Deleted: {file}" + Fore.RESET)
            else:
                file_hashes[file_hash] = file_path  # Store hash for future comparison

    # Get list of files in directory
    files_to_clean = [
        file
        for file in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, file))
    ]

    threads = []

    # Start a thread for each file cleaning task
    for file in files_to_clean:
        thread = threading.Thread(target=clean_file, args=(file,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # All files cleaned
    print(Fore.BLUE + "No more files to clean." + Fore.RESET)


def change_hue(img, target_hue):
    """
    Change the hue of an RGB image.

    Args:
    - img (PIL.Image): Input image to modify.
    - target_hue (float): Target hue shift in range [0, 1).

    """
    # Ensure image is RGB (so that i can convert it to hsv lmfao)
    img = img.convert("RGB")

    new_pixels = []

    # Loop through each pixel in the image
    for r, g, b in img.getdata():
        # Convert RGB to HSV
        h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)

        # Adjust hue by adding target_hue and modulo 1.0 to wrap around
        h = (h + target_hue) % 1.0

        # Convert HSV back to RGB
        r, g, b = colorsys.hsv_to_rgb(h, s, v)

        # Append the new RGB values to the list of pixels
        new_pixels.append((int(r * 255), int(g * 255), int(b * 255)))

    # Update image with the new pixel values
    img.putdata(new_pixels)

    return img


def imagebounds(path):
    """
    Resize an image to fit within specified width bounds, maintaining aspect ratio.

    Args:
    - path (str): Path to the image file.

    Raises:
    - FileNotFoundError: If the image file at `path` does not exist.
    - ValueError: If `imageLower` or `imageUpper` are not defined or are invalid.

    The function opens an image file specified by `path`, calculates its current width and height,
    and determines if resizing is necessary based on `imageLower` and `imageUpper` bounds. If resizing
    is required, it resizes the image while maintaining its aspect ratio using Lanczos resampling,
    and saves the resized image back to the original path.
    """
    # Open image and get size
    image = PIL.Image.open(path)
    width, height = image.size

    # Calculate the aspect ratio
    aspect_ratio = height / width

    # Check if image width is smaller than the lower bound
    if width < imageLower:
        new_width = imageLower
        new_height = int(new_width * aspect_ratio)
    # Check if image width is larger than the upper bound
    elif width > imageUpper:
        new_width = imageUpper
        new_height = int(new_width * aspect_ratio)
    else:
        # No need to resize the image
        return

    # Resize the image and save it
    resized_image = image.resize((new_width, new_height), PIL.Image.LANCZOS)
    resized_image.save(path)
