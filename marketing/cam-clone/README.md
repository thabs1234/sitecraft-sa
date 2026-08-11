# CAM Clone — the Doctor AI content machine, built from your stack

CAM = Content Automation App (Jonathan Acuña's system): paste an idea → AI
avatar video in ~10 min for under $3 → auto-posted to 5 platforms → comment
keyword funnels DMs. He claims 7-14M views/month and 700+ leads/day on it.

This doc maps that machine 1:1 onto tools you already run or have skills for.
Total running cost: ~R800/month (~$40) for everything, or ~R0 with free tiers.

```
IDEA ─► SCRIPT (Claude) ─► AVATAR VIDEO (HeyGen) ─► CAPTIONS (Claude)
      ─► POST (Postiz) ─► COMMENT FUNNEL (ManyChat/manual) ─► LEADS
                       └────────── FEEDBACK LOOP (weekly cron) ──────────┘
```

## The stack

| Stage | Tool | Role | Cost |
|---|---|---|---|
| Idea bank | `content-pillars.md` + cron rotation | 5 pillars, never stare at blank page | R0 |
| Script | Claude (API or Claude Code) | 30-45s hook-first scripts, per platform | pennies |
| Avatar video | **HeyGen API** (v2) | text → avatar presenter video | ~$29/mo ≈ 100 min → ~R5/video |
| Cover art | Nano Banana Pro / Midjourney / free fallback | thumbnails, slideshow stills | $0-10/mo |
| Captions+tags | Claude | per-platform captions + "SITE" CTA | pennies |
| Poster | **Postiz** (cloud or self-host) | batch TikTok+IG+YT+LinkedIn in 1 call | free tier / ~$5 hosting |
| Funnel | ManyChat (IG) + manual (TikTok) | keyword comment → auto-DM | $0-15/mo |
| Orchestrator | n8n (or Hermes cron) | idea → script → video → post, hands-free | R0 (self-host) |
| Feedback | weekly cron reading Postiz analytics | rank hooks, feed winners to idea bank | R0 |

**Avatar alternatives (cheaper entry):** HeyGen free tier (test 3 videos);
D-ID (~$6/mo); Synthesia (~$29/mo); FREE: stills + TTS (your existing
`free-ai-video` / Hermes text_to_speech pipeline) — Doctor AI's own tutorials
also mix HeyGen + Nano Banana + Sora 2; slideshow style (6-slide Larry formula
from `viral-slideshow-engine`) is proven and free.

## The batch math (how "10 posts/day" actually works)

1. **One sitting, 10 videos.** Pick 1 idea → Claude writes 10 script variants
   (different hooks, same core). Paste into HeyGen via API → 10 avatar videos.
   ~1 hour total, ~R50 in credits.
2. **One Postiz call posts a week.** `/posts` accepts an array — batch all
   platforms (TikTok + IG + YT Shorts + LinkedIn + FB) per video, schedule the
   whole week in ONE request per video (100 req/hr limit is plenty).
3. **TikTok = draft, always.** `content_posting_method: "UPLOAD"` → video lands
   in the TikTok app inbox; you add a trending sound (~10s) and publish. This
   dodges TikTok's shadowban on API auto-posts and is the single biggest
   view-multiplier in the system. Never DIRECT_POST to TikTok.
4. **Daily 5-minute routine**: open TikTok → publish drafts → reply to "SITE"
   comments → done. (Same tap as the comment funnel in `../comment-funnel/`.)

Daily output: 2 TikTok, 2 IG Reels, 2 YT Shorts, 2 LinkedIn, 2 Facebook =
10 posts across 5 platforms. Scale down to 1+1+1 to start.

## Feedback loop (the part everyone skips)

Weekly cron (reuse `viral-slideshow-engine`'s `analytics_cron.py` shape):
1. Pull per-video views/comments/likes (Postiz analytics endpoint).
2. Tag each video with its pillar + hook type.
3. Rank pillars by comment rate (comments are the money metric here, not
   views — comments = funnel entries).
4. Append winners to the idea bank, drop the duds.

## Pitfalls (from the Postiz skill + Doctor AI's own playbook)

- **Never auto-DIRECT_POST TikTok** — shadowban. UPLOAD draft + trending sound.
- **9:16 or nothing** — landscape kills reach on every platform here.
- **New accounts: warm up 7-14 days** (scroll/like/follow in-niche) before
  posting or reach is throttled from day one.
- **Pre-upload media to Postiz** — `/posts` body cap is 50 MB; base64 inline =
  413.
- **Views ≠ revenue.** Track comment-keyword count and DMs — that's the funnel
  entry rate. Optimize for comments, not plays.
- **Voice/avatar consistency**: lock 1 avatar + 1 voice for 90 days. The
  audience follows a face, even an AI one.

## First week checklist

- [ ] Get HeyGen API key, pick avatar + voice (SA-friendly English)
- [ ] Postiz cloud signup → Settings → Developers → API key → 401-probe it
- [ ] Connect TikTok + IG + YT + LinkedIn accounts (integrations)
- [ ] Run the API recipes in `api-recipes.md` end-to-end with 1 test video
- [ ] Publish 1 video/day for 7 days (drafts on TikTok)
- [ ] Wire ManyChat keyword "site" → DM 1 (see `../comment-funnel/dms.md`)
