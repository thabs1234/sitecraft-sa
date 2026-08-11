# CAM Clone — API recipes (copy-paste)

All recipes are bash (git-bash on Windows) with curl. Keys go in env vars —
never in files you commit.

## 0. Postiz reachability probe (run before anything)

```bash
curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: bad-key" \
  https://api.postiz.com/public/v1/integrations
# expect 401 = route + auth shape real. 000 = network problem, not auth.
```

## 1. Postiz — list connected accounts

```bash
BASE=https://api.postiz.com/public/v1
curl -s -H "Authorization: $POSTIZ_KEY" "$BASE/integrations" \
  | python -c "import json,sys; [print(i['id'], i['provider'], i['identifier']) for i in json.load(sys.stdin)]"
```

## 2. Postiz — upload media first (never inline base64)

```bash
curl -s -X POST "$BASE/upload" -H "Authorization: $POSTIZ_KEY" \
  -F "file=@video.mp4"   # -> {"id":"...","path":"https://..."}
```

## 3. Postiz — batch-post one video to 5 platforms (TikTok as DRAFT)

```bash
curl -s -X POST "$BASE/posts" -H "Authorization: $POSTIZ_KEY" \
  -H "Content-Type: application/json" -d '{
    "type": "schedule",
    "date": "2026-08-12T06:00:00.000Z",
    "posts": [
      {"integration": {"id": "TIKTOK_ID"},
       "value": [{"content": "Your competitor is on Google. Are you? Comment SITE 👇 #sitecraftsa",
                  "image": [{"id":"VID_1","path":"https://uploads.postiz.com/..."}]}],
       "settings": {"__type": "tiktok", "content_posting_method": "UPLOAD"}},
      {"integration": {"id": "IG_ID"},
       "value": [{"content": "Same caption #reels #smallbusinesssa"}],
       "settings": {"__type": "instagram"}},
      {"integration": {"id": "YT_ID"},
       "value": [{"content": "#shorts #aiwebsites"}],
       "settings": {"__type": "youtube"}}
    ]}'
# -> [{"postId":"...","integration":"..."}]  — 1 request, 3 platforms
```

## 4. HeyGen — avatar video from text (v2 API)

```bash
curl -s -X POST "https://api.heygen.com/v2/video/generate" \
  -H "X-Api-Key: $HEYGEN_KEY" -H "Content-Type: application/json" -d '{
    "video_inputs": [{
      "character": {"type": "avatar", "avatar_id": "YOUR_AVATAR_ID", "avatar_style": "normal"},
      "voice": {"type": "text", "input_text": "Your 30 second script here.", "voice_id": "YOUR_VOICE_ID"}
    }],
    "dimension": {"width": 1080, "height": 1920}
  }'
# -> {"data":{"video_id":"..."}}  — poll:
curl -s "https://api.heygen.com/v2/video_status?video_id=VIDEO_ID" \
  -H "X-Api-Key: $HEYGEN_KEY"
# poll until "status":"completed" -> data.video_url (mp4). Download it, upload to Postiz.
```

IDs: `GET https://api.heygen.com/v2/avatars` → avatar_id;
`GET https://api.heygen.com/v2/voices` → voice_id.
⚠️ Verify these shapes against the current HeyGen docs before your first paid
run — v2 endpoints evolve; the flow (generate → poll → download) is stable.

## 5. n8n flow (when you bring n8n up — it's currently not running)

Nodes, in order: `Manual Trigger (idea text)` → `HTTP Request (Claude API —
write 10 script variants)` → `Split In Batches` → `HTTP Request (HeyGen
generate)` → `Wait` (3 min) → `HTTP Request (HeyGen status poll, loop until
completed)` → `HTTP Request (download mp4)` → `Postiz /upload` → `Postiz
/posts (batch platforms, TikTok UPLOAD)` → `No-op (log scheduled posts)`.

Each node is a thin wrapper over recipes 3-4 above. Keep the whole flow in
`manual/schedule` mode until you've shipped 20 videos by hand — automation
only amplifies a process that already works.

## 6. Free tier check before spending anything

1. HeyGen free tier: 3 videos — proves the avatar works for your niche.
2. Postiz cloud free plan: enough to connect 2 platforms and test UPLOAD.
3. TTS fallback (R0): Hermes `text_to_speech` + stills + ffmpeg — your
   `free-ai-video` skill already does frames → MP4; add the voiceover and
   you have a "0 filming" video without paying anyone.
