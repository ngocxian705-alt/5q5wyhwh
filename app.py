from flask import Flask, request, jsonify
import asyncio
import threading
import os
import time
import main

app = Flask(__name__)

bot_loop = None
loop_thread = None

def start_bot_loop():
    global bot_loop
    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    try:
        bot_loop.run_until_complete(main.StarTinG())
    except Exception as e:
        print(f"Bot loop crashed: {e}")
    finally:
        main.bot_connected = False
        bot_loop.close()

def schedule_coro(coro):
    if not bot_loop or not main.bot_connected:
        raise RuntimeError("Bot is not connected")
    return asyncio.run_coroutine_threadsafe(coro, bot_loop)

def bot_status_check():
    if not main.bot_connected or not main.online_writer or not main.whisper_writer:
        return jsonify({'error': 'Bot not ready'}), 503
    return None

def parse_uids(uids_str):
    if not uids_str:
        return []
    return [int(uid.strip()) for uid in uids_str.split(',') if uid.strip().isdigit()]

@app.route('/status', methods=['GET'])
def status():
    if main.bot_connected and main.online_writer and main.whisper_writer:
        return jsonify({
            'status': 'online',
            'uptime': time.time() - main.bot_start_time,
            'connected': True
        })
    else:
        return jsonify({'status': 'offline', 'connected': False}), 503

@app.route('/squad/create', methods=['GET'])
def create_squad():
    check = bot_status_check()
    if check:
        return check

    size = request.args.get('size', default=5, type=int)
    uids_str = request.args.get('uids', default='')
    uids = parse_uids(uids_str)

    if size not in [3, 5, 6]:
        return jsonify({'error': 'Size must be 3, 5, or 6'}), 400
    if not uids:
        return jsonify({'error': 'uids must be a comma-separated list of integers'}), 400

    async def _action():
        try:
            PAc = await main.OpEnSq(main.key, main.iv, main.region)
            await main.SEndPacKeT(main.whisper_writer, main.online_writer, 'OnLine', PAc)
            await asyncio.sleep(0.3)

            for target_uid in uids:
                C = await main.cHSq(size, target_uid, main.key, main.iv, main.region)
                await main.SEndPacKeT(main.whisper_writer, main.online_writer, 'OnLine', C)
                await asyncio.sleep(0.3)
                V = await main.SEnd_InV(size, target_uid, main.key, main.iv, main.region)
                await main.SEndPacKeT(main.whisper_writer, main.online_writer, 'OnLine', V)
                await asyncio.sleep(0.3)

            E = await main.ExiT(None, main.key, main.iv)
            await asyncio.sleep(7)
            await main.SEndPacKeT(main.whisper_writer, main.online_writer, 'OnLine', E)

            return {'success': True, 'message': f'Squad {size} created and invites sent'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    future = schedule_coro(_action())
    result = future.result(timeout=10)
    return jsonify(result)


@app.route('/stop', methods=['GET'])
def stop_bot():
    check = bot_status_check()
    if check:
        return check

    async def _shutdown():
        await main.connection_pool.close()
        os._exit(0)

    schedule_coro(_shutdown())
    return jsonify({'success': True, 'message': 'Bot is shutting down'})

def start_background_loop():
    global loop_thread
    if loop_thread is None:
        loop_thread = threading.Thread(target=start_bot_loop, daemon=True)
        loop_thread.start()
        time.sleep(5)

if __name__ == '__main__':
    start_background_loop()
    app.run(host='0.0.0.0', port=5000, debug=False)