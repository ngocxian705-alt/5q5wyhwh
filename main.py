import requests, os, psutil, sys, jwt, pickle, json, binascii, time, urllib3, base64, datetime, re, socket, threading, ssl, pytz, aiohttp, asyncio
from protobuf_decoder.protobuf_decoder import Parser
from CTX import *
from MASRY import *
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Pb2 import DEcwHisPErMsG_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, MajoRLoGinrEq_pb2, sQ_pb2, Team_msg_pb2
from cfonts import render, say

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ADMIN_UID = "14888888686"
online_writer = None
whisper_writer = None
online_writer_lock = None
whisper_writer_lock = None
spam_room = False
spammer_uid = None
spam_chat_id = None
spam_uid = None
Spy = False
lag_task = None
Chat_Leave = False
is_muted = False
mute_until = 0
spam_requests_sent = 0
bot_start_time = time.time()
danger_spam_active = False
evo_cycle_active = False
current_evo_index = 0
evo_emotes = [
    909000063, 909000068, 909000075, 909000081, 909000085, 909000090, 909000098, 909033001, 909035007, 909037011,
    909038010, 909038012, 909039011, 909040010,909041005, 909042008, 909045001, 909051003
]

connection_pool = None
command_cache = {}
last_request_time = {}
RATE_LIMIT_DELAY = 0.1
MAX_CACHE_SIZE = 50
CLEANUP_INTERVAL = 300
command_stats = {}

key = None
iv = None
region = None
bot_connected = False

def cleanup_cache():
    current_time = time.time()
    to_remove = [k for k, v in last_request_time.items()
                 if current_time - v > CLEANUP_INTERVAL]
    for k in to_remove:
        last_request_time.pop(k, None)
    if len(command_cache) > MAX_CACHE_SIZE:
        oldest_keys = sorted(command_cache.keys())[:len(command_cache)//2]
        for key in oldest_keys:
            command_cache.pop(key, None)

def get_rate_limited_response(user_id):
    user_key = str(user_id)
    current_time = time.time()
    if user_key in last_request_time:
        time_since_last = current_time - last_request_time[user_key]
        if time_since_last < RATE_LIMIT_DELAY:
            return False
    last_request_time[user_key] = current_time
    return True

login_url, ob, version = AuToUpDaTE()

Hr = {
    'User-Agent': Uaa(),
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': ob
}

def get_random_color():
    colors = [
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]",
        "[DC143C]", "[00CED1]", "[9400D3]", "[F08080]", "[20B2AA]", "[FF1493]", "[7CFC00]", "[B22222]",
        "[FF4500]", "[DAA520]", "[00BFFF]", "[00FF7F]", "[4682B4]", "[6495ED]", "[DDA0DD]", "[E6E6FA]",
        "[2E8B57]", "[3CB371]", "[6B8E23]", "[808000]", "[B8860B]", "[CD5C5C]", "[8B0000]", "[FF6347]"
    ]
    return random.choice(colors)

def is_admin(uid):
    return str(uid) == ADMIN_UID

def is_bot_muted():
    global is_muted, mute_until
    if is_muted and time.time() < mute_until:
        return True
    elif is_muted and time.time() >= mute_until:
        is_muted = False
        mute_until = 0
        return False
    return False

def update_command_stats(command):
    if command not in command_stats:
        command_stats[command] = 0
    command_stats[command] += 1

async def safe_send_message(chat_type, message, target_uid, chat_id, key, iv, max_retries=3):
    for attempt in range(max_retries):
        try:
            P = await SEndMsG(chat_type, message, target_uid, chat_id, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
            print(f"Message sent successfully on attempt {attempt + 1}")
            return True
        except Exception as e:
            print(f"Failed to send message (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)
    return False

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload

async def GeNeRaTeAccEss(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": (await Ua()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"}
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=Hr, data=data) as response:
            if response.status != 200:
                return (None, None)
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return (open_id, access_token) if open_id and access_token else (None, None)

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = version
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return await encrypted_proto(string)

async def MajorLogin(payload):
    url = f"{login_url}MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization'] = f"Bearer {token}"
    try:
        async with connection_pool.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200:
                return await response.read()
            return None
    except:
        return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto

async def decode_team_packet(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = sQ_pb2.recieved_chat()
    proto.ParseFromString(packet)
    return proto

async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9:
        headers = '0000000'
    elif uid_length == 8:
        headers = '00000000'
    elif uid_length == 10:
        headers = '000000'
    elif uid_length == 7:
        headers = '000000000'
    else:
        print('Unexpected length')
        headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"

async def cHTypE(H):
    if not H:
        return 'Squid'
    elif H == 1:
        return 'CLan'
    elif H == 2:
        return 'PrivaTe'

async def SEndMsG(H, message, Uid, chat_id, key, iv):
    TypE = await cHTypE(H)
    if TypE == 'Squid':
        msg_packet = await xSEndMsgsQ(message, chat_id, key, iv)
    elif TypE == 'CLan':
        msg_packet = await xSEndMsg(message, 1, chat_id, chat_id, key, iv)
    elif TypE == 'PrivaTe':
        msg_packet = await xSEndMsg(message, 2, Uid, Uid, key, iv)
    return msg_packet

async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    global online_writer_lock, whisper_writer_lock
    if TypE == 'ChaT' and ChaT:
        async with whisper_writer_lock:
            whisper_writer.write(PacKeT)
            await whisper_writer.drain()
    elif TypE == 'OnLine':
        async with online_writer_lock:
            online_writer.write(PacKeT)
            await online_writer.drain()
    else:
        return 'UnsoPorTed TypE ! >> ErrrroR (:():)'

async def danger_spam_command(uids, emote_id, key, iv, region):
    global danger_spam_active
    danger_spam_active = True
    count = 0
    while danger_spam_active and count < 20:
        for uid in uids:
            if not danger_spam_active:
                break
            try:
                H = await Emote_k(uid, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except:
                pass
            await asyncio.sleep(0.1)
        count += 1
        await asyncio.sleep(0.5)
    danger_spam_active = False

async def evo_cycle_command(uids, key, iv, region):
    global evo_cycle_active, current_evo_index, evo_emotes
    evo_cycle_active = True
    while evo_cycle_active:
        emote_id = evo_emotes[current_evo_index]
        for uid in uids:
            if not evo_cycle_active:
                break
            try:
                H = await Emote_k(uid, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except:
                pass
            await asyncio.sleep(0.1)
        current_evo_index = (current_evo_index + 1) % len(evo_emotes)
        await asyncio.sleep(8)

async def stop_commands():
    global evo_cycle_active, danger_spam_active
    evo_cycle_active = False
    danger_spam_active = False

def _encrypt_inner_packet(packet_hex: str, key: str, iv: str) -> str:
    k = key if isinstance(key, bytes) else bytes.fromhex(key)
    v = iv if isinstance(iv, bytes) else bytes.fromhex(iv)
    data = bytes.fromhex(packet_hex)
    cipher = AES.new(k, AES.MODE_CBC, v)
    return cipher.encrypt(pad(data, AES.block_size)).hex()

def pkt_skwad_maker(key: str, iv: str) -> bytes:
    fields = {
        1: 1,
        2: {
            2: "\u0001",
            3: 1,
            4: 1,
            5: "en",
            9: 1,
            11: 1,
            13: 1,
            14: {2: 5756, 6: 11, 8: "1.114.8", 9: 3, 10: 2},
        },
    }
    packet = create_protobuf_packet(fields).hex()
    enc_len = len(encrypt_packet(packet, key, iv)) // 2
    head = _dec_to_hex(enc_len)
    if len(head) == 2:
        final = "0515000000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 3:
        final = "051500000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 4:
        final = "05150000" + head + _encrypt_inner_packet(packet, key, iv)
    else:
        final = "0515000" + head + _encrypt_inner_packet(packet, key, iv)
    return bytes.fromhex(final)

def pkt_changes(num: int, key: str, iv: str) -> bytes:
    fields = {
        1: 17,
        2: {1: 12480598706, 2: 1, 3: int(num), 4: 62, 5: "\u001a", 8: 5, 13: 329},
    }
    packet = create_protobuf_packet(fields).hex()
    enc_len = len(encrypt_packet(packet, key, iv)) // 2
    head = _dec_to_hex(enc_len)
    if len(head) == 2:
        final = "0515000000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 3:
        final = "051500000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 4:
        final = "05150000" + head + _encrypt_inner_packet(packet, key, iv)
    else:
        final = "0515000" + head + _encrypt_inner_packet(packet, key, iv)
    return bytes.fromhex(final)

def pkt_invite_skwad(idplayer: str, key: str, iv: str) -> bytes:
    fields = {1: 2, 2: {1: int(idplayer), 2: "ME", 4: 1}}
    packet = create_protobuf_packet(fields).hex()
    enc_len = len(encrypt_packet(packet, key, iv)) // 2
    head = _dec_to_hex(enc_len)
    if len(head) == 2:
        final = "0515000000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 3:
        final = "051500000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 4:
        final = "05150000" + head + _encrypt_inner_packet(packet, key, iv)
    else:
        final = "0515000" + head + _encrypt_inner_packet(packet, key, iv)
    return bytes.fromhex(final)

def pkt_request_skwad(idplayer: str, key: str, iv: str) -> bytes:
    fields = {
        1: 33,
        2: {
            1: int(idplayer),
            2: "ME",
            3: 1,
            4: 1,
            7: 330,
            8: 19459,
            9: 100,
            12: 1,
            16: 1,
            17: {2: 94, 6: 11, 8: "1.114.8", 9: 3, 10: 2},
            18: 201,
            23: {2: 1, 3: 1},
            24: int(get_random_avatar()),
            26: {},
            28: {},
        },
    }
    packet = create_protobuf_packet(fields).hex()
    enc_len = len(encrypt_packet(packet, key, iv)) // 2
    head = _dec_to_hex(enc_len)
    if len(head) == 2:
        final = "0515000000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 3:
        final = "051500000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 4:
        final = "05150000" + head + _encrypt_inner_packet(packet, key, iv)
    else:
        final = "0515000" + head + _encrypt_inner_packet(packet, key, iv)
    return bytes.fromhex(final)

def pkt_leave_s(key: str, iv: str) -> bytes:
    fields = {1: 7, 2: {1: 12480598706}}
    packet = create_protobuf_packet(fields).hex()
    enc_len = len(encrypt_packet(packet, key, iv)) // 2
    head = _dec_to_hex(enc_len)
    if len(head) == 2:
        final = "0515000000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 3:
        final = "051500000" + head + _encrypt_inner_packet(packet, key, iv)
    elif len(head) == 4:
        final = "05150000" + head + _encrypt_inner_packet(packet, key, iv)
    else:
        final = "0515000" + head + _encrypt_inner_packet(packet, key, iv)
    return bytes.fromhex(final)

async def MuTe(Uid, K, V):
    fields = {1: 3, 2: {1: int(Uid), 3: "ar", 4: "1750728024661459697_3qind8eeqs"}}
    return GeneRaTePk(str(CrEaTe_ProTo(fields).hex()), '1201', K, V)

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer, spam_room, whisper_writer, spammer_uid, spam_chat_id, spam_uid, XX, uid, Spy, data2, Chat_Leave, lag_running, lag_task, online_writer_lock
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            online_writer_lock = asyncio.Lock()
            bytes_payload = bytes.fromhex(AutHToKen)
            async with online_writer_lock:
                online_writer.write(bytes_payload)
                await online_writer.drain()
            while True:
                data2 = await reader.read(9999)
                if not data2:
                    break
                if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                    try:
                        packet = await DeCode_PackEt(data2.hex()[10:])
                        packet = json.loads(packet)
                        OwNer_UiD, CHaT_CoDe, SQuAD_CoDe = await GeTSQDaTa(packet)
                        JoinCHaT = await AutH_Chat(3, OwNer_UiD, CHaT_CoDe, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', JoinCHaT)
                        message = f"""
[b]Welcome

{get_random_color()} تم اخَََََتَََََراق الاسكواد بواسطهMASRY 

{get_random_color()} MASRY   ＢＯＴ

- {get_random_color()}To see the commands type => [ff0000]/help[ffffff]

- {get_random_color()}ByMASRY 

تابعني او سيتم تبنيد حسابك 

صاحب وصانع البوت هوه

    CTX    MASRY  

[808080]- Follow Me On my tik tok account => [00ff00] {tok}

[808080]- DmWith Me On my telegram account => [00ff00]{owner_user}

[808080]- Follow Me On my Instagram account => [00ff00] {insta}\n"""
                        P = await SEndMsG(0, message, OwNer_UiD, OwNer_UiD, key, iv)
                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                    except:
                        if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                            try:
                                packet = await DeCode_PackEt(data2.hex()[10:])
                                print()
                                packet = json.loads(packet)
                                OwNer_UiD, CHaT_CoDe, SQuAD_CoDe = await GeTSQDaTa(packet)
                                JoinCHaT = await AutH_Chat(3, OwNer_UiD, CHaT_CoDe, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', JoinCHaT)
                                message = f'[B][C]{get_random_color()}\n- WeLComE To Emote Bot ! \n\n{get_random_color()}- Commands : @a {xMsGFixinG("123456789")} {xMsGFixinG("909000001")}\n\n[00FF00]Dev : @{xMsGFixinG("masry-from-CTX")}'
                                P = await SEndMsG(0, message, OwNer_UiD, OwNer_UiD, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                            except:
                                pass
            online_writer.close()
            await online_writer.wait_closed()
            online_writer = None
        except Exception as e:
            print(f"- ErroR With {ip}:{port} - {e}")
            online_writer = None
        await asyncio.sleep(reconnect_delay)

async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region, reconnect_delay=0.5):
    print(region, 'TCP CHAT')
    global spam_room, whisper_writer, spammer_uid, spam_chat_id, spam_uid, online_writer, chat_id, XX, uid, Spy, data2, Chat_Leave, is_muted, mute_until, lag_running, lag_task, whisper_writer_lock
    while True:
        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            whisper_writer_lock = asyncio.Lock()
            bytes_payload = bytes.fromhex(AutHToKen)
            async with whisper_writer_lock:
                whisper_writer.write(bytes_payload)
                await whisper_writer.drain()
            ready_event.set()
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                print('\n - TarGeT BoT in CLan ! ')
                print(f' - Clan Uid > {clan_id}')
                print(f' - BoT ConnEcTed WiTh CLan ChaT SuccEssFuLy ! ')
                pK = await AuthClan(clan_id, clan_compiled_data, key, iv)
                if whisper_writer:
                    async with whisper_writer_lock:
                        whisper_writer.write(pK)
                        await whisper_writer.drain()
            while True:
                data = await reader.read(9999)
                if not data:
                    break
                if data.hex().startswith("120000"):
                    msg = await DeCode_PackEt(data.hex()[10:])
                    chatdata = json.loads(msg)
                    try:
                        response = await DecodeWhisperMessage(data.hex()[10:])
                        uid = response.Data.uid
                        chat_id = response.Data.Chat_ID
                        XX = response.Data.chat_type
                        inPuTMsG = response.Data.msg.lower()
                    except:
                        response = None

            whisper_writer.close()
            await whisper_writer.wait_closed()
            whisper_writer = None
        except Exception as e:
            print(f"ErroR {ip}:{port} - {e}")
            whisper_writer = None
        await asyncio.sleep(reconnect_delay)

async def MaiiiinE():
    global connection_pool, online_writer_lock, whisper_writer_lock
    global key, iv, region, bot_connected  
    connection_pool = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=20),
        connector=aiohttp.TCPConnector(limit=20, limit_per_host=10)
    )
    Uid, Pw = '4565450573', '5q578i_UNJ4U_BY_SPIDEERIO_GAMING_65VJE'
    open_id, access_token = await GeNeRaTeAccEss(Uid, Pw)
    if not open_id or not access_token:
        print("ErroR - InvaLid AccounT")
        return None
    PyL = await EncRypTMajoRLoGin(open_id, access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE:
        print("TarGeT AccounT => BannEd / NoT ReGisTeReD ! ")
        return None
    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    print(UrL)
    region = MajoRLoGinauTh.region
    ToKen = MajoRLoGinauTh.token
    TarGeT = MajoRLoGinauTh.account_uid
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp

    bot_connected = True

    LoGinDaTa = await GetLoginData(UrL, PyL, ToKen)
    if not LoGinDaTa:
        print("ErroR - GeTinG PorTs From LoGin DaTa !")
        return None
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
    OnLineiP, OnLineporT = OnLinePorTs.split(":")
    ChaTiP, ChaTporT = ChaTPorTs.split(":")
    acc_name = LoGinDaTaUncRypTinG.AccountName
    print(ToKen)
    equie_emote(ToKen, UrL)
    AutHToKen = await xAuThSTarTuP(int(TarGeT), ToKen, int(timestamp), key, iv)
    ready_event = asyncio.Event()
    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region))
    await ready_event.wait()
    await asyncio.sleep(1)
    task2 = asyncio.create_task(TcPOnLine(OnLineiP, OnLineporT, key, iv, AutHToKen))
    os.system('clear')
    print(render('MASRY  BOT', colors=['white', 'green'], align='center'))
    print('')
    print(f" - MASRY BOT STarTinG And OnLine on TarGet : {TarGeT} | BOT NAME : {acc_name}\n")
    print(f" - BoT sTaTus > GooD | OnLinE ! (:")
    print(f" - DEV: masry | Bot Uptime: {time.strftime('%H:%M:%S', time.gmtime(time.time() - bot_start_time))}")
    await asyncio.gather(task1, task2)

async def StarTinG():
    while True:
        try:
            await asyncio.wait_for(MaiiiinE(), timeout=7 * 60 * 60)
        except asyncio.TimeoutError:
            print("Token ExpiRed ! , ResTartinG")
        except Exception as e:
            print(f"ErroR TcP - {e} => ResTarTinG ...")

if __name__ == '__main__':
    asyncio.run(StarTinG())