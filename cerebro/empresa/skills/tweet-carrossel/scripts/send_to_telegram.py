#!/usr/bin/env python3
"""
send_to_telegram.py — Envia imagens do carrossel para o Telegram do usuário.

Uso:
    python3 send_to_telegram.py \
        --chat-id -1003803476669 \
        --thread-id 4 \
        --dir /root/cerebro-vital-slim/deliverables/creatina-cerebro-jpeg-2026-04-14 \
        --caption "Carrossel Creatina"

Env: TELEGRAM_BOT_TOKEN
"""
import argparse, os, json, sys, glob, requests

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chat-id", type=int, required=True)
    ap.add_argument("--thread-id", type=int, default=None, help="ID do tópico (forum)")
    ap.add_argument("--dir", required=True, help="Diretório com slide_*.jpg")
    ap.add_argument("--caption", default="")
    ap.add_argument("--token", default=os.environ.get("TELEGRAM_BOT_TOKEN"))
    args = ap.parse_args()

    if not args.token:
        print("ERRO: TELEGRAM_BOT_TOKEN não definido", file=sys.stderr)
        sys.exit(1)

    slides = sorted(glob.glob(f"{args.dir}/slide_*.jpg"))
    if not slides:
        print(f"ERRO: sem slides em {args.dir}", file=sys.stderr)
        sys.exit(1)

    # Telegram aceita até 10 imagens por mediaGroup
    for chunk_start in range(0, len(slides), 10):
        chunk = slides[chunk_start:chunk_start+10]
        files = {}
        media = []
        for i, path in enumerate(chunk):
            key = f"photo{i}"
            files[key] = open(path, "rb")
            item = {"type": "photo", "media": f"attach://{key}"}
            if chunk_start == 0 and i == 0 and args.caption:
                item["caption"] = args.caption
            media.append(item)

        data = {"chat_id": args.chat_id, "media": json.dumps(media)}
        if args.thread_id is not None:
            data["message_thread_id"] = args.thread_id

        url = f"https://api.telegram.org/bot{args.token}/sendMediaGroup"
        resp = requests.post(url, data=data, files=files, timeout=120)
        for f in files.values():
            f.close()

        if resp.status_code != 200:
            print(f"ERRO {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
            sys.exit(1)

    print(f"OK: {len(slides)} slides enviados ao chat {args.chat_id} (thread {args.thread_id})")

if __name__ == "__main__":
    main()
