import urllib.request
urls = [
    "https://thabs1234.github.io/sitecraft-sa/samples/durban/chicken-tikka-palace.html",
    "https://thabs1234.github.io/sitecraft-sa/samples/durban/stoker-s-arms.html",
    "https://thabs1234.github.io/sitecraft-sa/samples/pmb/the-break-room.html",
    "https://thabs1234.github.io/sitecraft-sa/samples/durban/myeza-traditional-chemist.html",
]
for u in urls:
    try:
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            print(r.status, len(r.read()), u.split("/")[-1])
    except Exception as e:
        print("ERR", e, u.split("/")[-1])
