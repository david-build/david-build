#!/usr/bin/env python3
"""Render the profile stats cards as SVG from the GitHub API.

Three cards, each in a dark and a light variant:
  activity  - contributions over the last year, gradient area chart
  totals    - the headline numbers with a weekly sparkline
  hours     - commits by local hour of day, gradient bars

The snake SVGs already in the output folder get their progress bar rounded.

Usage: GH_TOKEN=... cards.py <user> <out_dir>
"""

import base64
import datetime as dt
import json
import os
import random
import re
import sys
import urllib.request

API = "https://api.github.com"
HERE = os.path.dirname(os.path.abspath(__file__))
PAD = 27

# what surfaces between the dots, now and then: small artefacts of a developer's day
EGGS = ["</>", "{ }", ";", "=>", "#!", "λ", "0x9B", ":wq", "git push", "404", "sudo", "null", "&&", "//", "~/", "TODO", "42", "rm -rf", "⌘", "λx.x", "0b1010", "npm i", "SELECT *", "<?php", "swift build"]

# brand palette: Dark Void, Neon Purple, Links, Tealish Green, Liquid Lava, the greys and Snow
BRAND = {
	"void": "#151419", "purple": "#9b30ff", "links": "#8c78f2", "green": "#5afa77", "lava": "#f56f10",
	"glucon": "#26242b", "anchor": "#2f2e36", "cute": "#61606d", "dusty": "#878787", "snow": "#fbfbfb",
}

THEMES = {
	"dark": {
		"bg": BRAND["void"],
		"text": BRAND["snow"], "muted": BRAND["dusty"], "faint": BRAND["cute"],
		"dot": "#ffffff", "dot_op": ".045", "egg_op": ".13", "grid": "rgba(255,255,255,.06)", "glow_op": ".24",
		"edge": "#ffffff", "edge_op": ".16",
	},
	"light": {
		"bg": BRAND["snow"],
		"text": BRAND["void"], "muted": BRAND["cute"], "faint": BRAND["dusty"],
		"dot": BRAND["void"], "dot_op": ".05", "egg_op": ".14", "grid": "rgba(21,20,25,.07)", "glow_op": ".11",
		"edge": BRAND["void"], "edge_op": ".14",
	},
}

FONT = "Onest, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def font_face():
	"""The brand face travels inside the SVG: an image on GitHub can load no external font."""
	with open(os.path.join(HERE, "..", "assets", "fonts", "onest.woff2"), "rb") as f:
		data = base64.b64encode(f.read()).decode()
	return "<style>@font-face{font-family:Onest;font-weight:100 900;src:url(data:font/woff2;base64,%s) format('woff2')}</style>" % data


def fetch(url, token, data=None):
	req = urllib.request.Request(url, data=data, headers={
		"Authorization": "Bearer " + token,
		"Accept": "application/vnd.github+json",
		"User-Agent": "profile-cards",
		"Content-Type": "application/json",
	})
	with urllib.request.urlopen(req, timeout=60) as r:
		return json.load(r)


def graphql(token, query, variables):
	body = json.dumps({"query": query, "variables": variables}).encode()
	out = fetch(API + "/graphql", token, body)
	if "errors" in out:
		raise SystemExit(out["errors"])
	return out["data"]


QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      nodes { stargazerCount }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def load(user, token):
	u = graphql(token, QUERY, {"login": user})["user"]
	cc = u["contributionsCollection"]
	days = [d for w in cc["contributionCalendar"]["weeks"] for d in w["contributionDays"]]

	# the search index caps at 1000 results; the newest commits are what a
	# "when do you work" chart is about anyway
	hours = [0] * 24
	seen = 0
	for page in range(1, 11):
		try:
			res = fetch(API + "/search/commits?q=author:%s&sort=author-date&order=desc&per_page=100&page=%d" % (user, page), token)
		except Exception:
			break
		items = res.get("items", [])
		for it in items:
			stamp = it["commit"]["author"]["date"]
			# the author date carries the committer's own offset, so the hour is already local
			try:
				hours[dt.datetime.fromisoformat(stamp.replace("Z", "+00:00")).hour] += 1
				seen += 1
			except ValueError:
				pass
		if len(items) < 100:
			break

	return {
		"days": days,
		"total": cc["contributionCalendar"]["totalContributions"],
		"commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
		"prs": cc["totalPullRequestContributions"],
		"issues": cc["totalIssueContributions"],
		"repos_contrib": cc["totalRepositoriesWithContributedCommits"],
		"stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
		"followers": u["followers"]["totalCount"],
		"hours": hours,
		"hours_n": seen,
	}


def fmt(n):
	if n >= 10000:
		return "%.1fk" % (n / 1000)
	return "{:,}".format(n)


def smooth(values, window):
	out = []
	half = window // 2
	for i in range(len(values)):
		lo, hi = max(0, i - half), min(len(values), i + half + 1)
		out.append(sum(values[lo:hi]) / (hi - lo))
	return out


def curve(points):
	"""Catmull-Rom through the points as cubic beziers, so the line stays on the data."""
	if len(points) < 2:
		return ""
	d = "M%.1f,%.1f" % points[0]
	for i in range(len(points) - 1):
		p0 = points[i - 1] if i > 0 else points[i]
		p1, p2 = points[i], points[i + 1]
		p3 = points[i + 2] if i + 2 < len(points) else p2
		c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
		c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
		d += " C%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (c1 + c2 + p2)
	return d


def open_svg(w, h, label):
	return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="%s">%s' % (w, h, w, h, label, font_face())


def eggs(t, w, h, key):
	"""A few developer artefacts sit on the dot grid instead of dots; the seed keeps them still between daily renders."""
	rng = random.Random(key)
	out = ""
	for _ in range(max(4, (w * h) // 26000)):
		x = rng.randrange(2, w // 10 - 2) * 10 + 5
		y = rng.randrange(2, h // 10 - 2) * 10 + 5
		out += '<text x="%d" y="%d" text-anchor="middle" dominant-baseline="middle" font-family="%s" font-size="10" fill="%s" opacity="%s">%s</text>' % (x, y, FONT, t["dot"], t["egg_op"], rng.choice(EGGS).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
	return out


def shell(t, w, h, key, glow):
	"""Card plate: rounded, an even halftone of faint dots with a few easter eggs, a glow of the card's own colour rising from the foot, a gradient edge."""
	return """<defs>
	<clipPath id="clip-%(k)s"><rect width="%(w)d" height="%(h)d" rx="18"/></clipPath>
	<pattern id="dots-%(k)s" width="10" height="10" patternUnits="userSpaceOnUse"><circle cx="5" cy="5" r="1" fill="%(dot)s"/></pattern>
	<radialGradient id="glow-%(k)s" cx=".5" cy="1.2" r=".8"><stop offset="0" stop-color="%(glow)s" stop-opacity="%(glow_op)s"/><stop offset="1" stop-color="%(glow)s" stop-opacity="0"/></radialGradient>
	<linearGradient id="edge-%(k)s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%(edge)s" stop-opacity="%(edge_op)s"/><stop offset="1" stop-color="%(glow)s" stop-opacity=".25"/></linearGradient>
	<linearGradient id="line-%(k)s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="%(links)s"/><stop offset="1" stop-color="%(purple)s"/></linearGradient>
	<linearGradient id="area-%(k)s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%(purple)s" stop-opacity=".4"/><stop offset="1" stop-color="%(purple)s" stop-opacity="0"/></linearGradient>
	<linearGradient id="spark-%(k)s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3b82f6"/><stop offset=".55" stop-color="#22c55e"/><stop offset="1" stop-color="#a3e635"/></linearGradient>
	<linearGradient id="sparkarea-%(k)s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4ade80" stop-opacity=".4"/><stop offset="1" stop-color="#4ade80" stop-opacity="0"/></linearGradient>
	<linearGradient id="bar-%(k)s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%(green)s"/><stop offset=".5" stop-color="%(green)s" stop-opacity=".55"/><stop offset="1" stop-color="%(green)s" stop-opacity=".06"/></linearGradient>
	<filter id="soft-%(k)s" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<g clip-path="url(#clip-%(k)s)">
	<rect width="%(w)d" height="%(h)d" fill="%(bg)s"/>
	<rect width="%(w)d" height="%(h)d" fill="url(#dots-%(k)s)" opacity="%(dot_op)s"/>
	%(eggs)s
	<rect width="%(w)d" height="%(h)d" fill="url(#glow-%(k)s)"/>
</g>
<rect x=".5" y=".5" width="%(w)d" height="%(h)d" rx="18" fill="none" stroke="url(#edge-%(k)s)"/>
""" % dict(t, **BRAND, k=key, w=w - 1, h=h - 1, glow=glow, eggs=eggs(t, w, h, key))


def text(x, y, s, size, color, weight=400, anchor="start"):
	return '<text x="%.1f" y="%.1f" text-anchor="%s" font-family="%s" font-size="%d" font-weight="%d" fill="%s">%s</text>' % (x, y, anchor, FONT, size, weight, color, s)


def title(t, x, y, head, sub):
	# y is the top of the text block: a 19px title cap sits 15px below it, the subtitle 22px under that
	return text(x, y + 15, head, 19, t["text"], 700) + text(x, y + 37, sub, 12, t["muted"])


def card_activity(t, key, d):
	w, h = 880, 260
	days = d["days"]
	counts = [x["contributionCount"] for x in days]
	# a three week mean, sampled every few days, turns the spiky daily series into the shape of the year
	series = smooth(counts, 21)[::4]
	left, right = PAD, w - PAD
	top, bottom = PAD + 56, h - PAD - 22
	peak = max(series) or 1
	n = len(series)
	pts = [(left + i * (right - left) / (n - 1), bottom - v / peak * (bottom - top)) for i, v in enumerate(series)]

	s = open_svg(w, h, "Contributions in the last year")
	s += shell(t, w, h, key, BRAND["purple"])
	s += title(t, PAD, PAD, "Activity", "contributions in the last year, all repositories")
	s += text(right, PAD + 24, fmt(d["total"]), 30, t["text"], 700, "end")

	# dotted grid, one line per quarter of the peak
	for i in range(1, 4):
		y = bottom - i * (bottom - top) / 4
		s += '<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-dasharray="2 4"/>' % (left, y, right, y, t["grid"])

	path = curve(pts)
	s += '<path d="%s L%.1f,%d L%d,%d Z" fill="url(#area-%s)"/>' % (path, pts[-1][0], bottom, left, bottom, key)
	s += '<path d="%s" fill="none" stroke="url(#line-%s)" stroke-width="2.5" stroke-linejoin="round" opacity=".4" filter="url(#soft-%s)"/>' % (path, key, key)
	s += '<path d="%s" fill="none" stroke="url(#line-%s)" stroke-width="2.5" stroke-linejoin="round"/>' % (path, key)

	# the peak day, called out
	pi = max(range(n), key=lambda i: series[i])
	px, py = pts[pi]
	peak_day = max(days, key=lambda x: x["contributionCount"])
	s += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%d" stroke="%s" stroke-dasharray="2 3"/>' % (px, py, px, bottom, t["faint"])
	s += '<circle cx="%.1f" cy="%.1f" r="4" fill="%s" stroke="%s" stroke-width="2"/>' % (px, py, t["bg"], BRAND["green"])
	label = "%d on %s" % (peak_day["contributionCount"], dt.date.fromisoformat(peak_day["date"]).strftime("%-d %b"))
	anchor = "end" if px > w / 2 else "start"
	s += text(px - 10 if anchor == "end" else px + 10, py - 8, label, 12, t["muted"], 500, anchor)

	# month ticks along the foot
	last = ""
	for i, x in enumerate(days):
		m = dt.date.fromisoformat(x["date"]).strftime("%b")
		if m != last and i > 6:
			s += text(left + i * (right - left) / (len(days) - 1), h - PAD, m, 11, t["faint"], 500, "middle")
		last = m
	s += "</svg>"
	return s


def card_totals(t, key, d):
	w, h = 432, 250
	s = open_svg(w, h, "Totals")
	s += shell(t, w, h, key, BRAND["lava"])
	s += title(t, PAD, PAD, "Totals", "last year, public and private")

	cells = [
		("Commits", d["commits"]), ("Pull requests", d["prs"]), ("Issues", d["issues"]),
		("Repos touched", d["repos_contrib"]), ("Stars", d["stars"]), ("Followers", d["followers"]),
	]
	col = (w - 2 * PAD) / 3
	for i, (name, val) in enumerate(cells):
		x = PAD + (i % 3) * col
		y = PAD + 76 + (i // 3) * 58
		s += text(x, y, fmt(val), 24, t["text"], 700)
		s += text(x, y + 17, name, 11, t["muted"])

	# weekly sparkline along the foot of the card
	weeks = [sum(x["contributionCount"] for x in d["days"][i:i + 7]) for i in range(0, len(d["days"]), 7)]
	peak = max(weeks) or 1
	left, right = PAD, w - PAD
	top, bottom = h - PAD - 26, h - PAD
	n = len(weeks)
	pts = [(left + i * (right - left) / (n - 1), bottom - v / peak * (bottom - top)) for i, v in enumerate(weeks)]
	path = curve(pts)
	s += '<path d="%s L%.1f,%d L%d,%d Z" fill="url(#sparkarea-%s)"/>' % (path, pts[-1][0], bottom, left, bottom, key)
	s += '<path d="%s" fill="none" stroke="url(#spark-%s)" stroke-width="2" stroke-linejoin="round"/>' % (path, key)
	s += "</svg>"
	return s


def card_hours(t, key, d):
	w, h = 432, 250
	s = open_svg(w, h, "Commits by hour")
	s += shell(t, w, h, key, BRAND["green"])
	s += title(t, PAD, PAD, "Commits by hour", "local time of the last %s commits" % fmt(d["hours_n"]))

	hours = d["hours"]
	peak = max(hours) or 1
	left, right = PAD, w - PAD
	top, bottom = PAD + 70, h - PAD - 22
	slot = (right - left) / 24
	bw = slot - 4
	best = hours.index(peak)
	for i, v in enumerate(hours):
		x = left + i * slot + 2
		bh = max(2, v / peak * (bottom - top))
		y = bottom - bh
		s += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="url(#bar-%s)"/>' % (x, y, bw, bh, key)

	# the busiest hour, called out above its bar
	s += text(left + best * slot + slot / 2, top - 8, "%02d:00" % best, 11, t["muted"], 500, "middle")
	for hr in (0, 6, 12, 18, 23):
		s += text(left + hr * slot + slot / 2, h - PAD, str(hr), 11, t["faint"], 500, "middle")
	s += "</svg>"
	return s


def round_snake(path):
	"""The snake's progress bar is a row of flat rects; clip the row to one rounded shape."""
	with open(path, encoding="utf-8") as f:
		svg = f.read()
	rects = re.findall(r'<rect class="u u\d+"[^>]*/>', svg)
	if not rects:
		return
	nums = [(float(re.search(r'x="([\d.]+)"', r).group(1)), float(re.search(r'width="([\d.]+)"', r).group(1)),
	         float(re.search(r'y="([\d.]+)"', r).group(1)), float(re.search(r'height="([\d.]+)"', r).group(1))) for r in rects]
	x0 = min(n[0] for n in nums)
	x1 = max(n[0] + n[1] for n in nums)
	y0, hh = nums[0][2], nums[0][3]
	clip = '<clipPath id="stack"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f"/></clipPath>' % (x0, y0, x1 - x0, hh, hh / 2)
	row = "".join(rects)
	svg = svg.replace(row, '<defs>%s</defs><g clip-path="url(#stack)">%s</g>' % (clip, row), 1)
	with open(path, "w", encoding="utf-8") as f:
		f.write(svg)


def main():
	user = sys.argv[1] if len(sys.argv) > 1 else "david-build"
	out = sys.argv[2] if len(sys.argv) > 2 else "dist"
	token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
	if not token:
		raise SystemExit("GH_TOKEN is required")
	os.makedirs(out, exist_ok=True)
	d = load(user, token)
	for theme, t in THEMES.items():
		suffix = "" if theme == "light" else "-" + theme
		for name, fn in (("activity", card_activity), ("totals", card_totals), ("hours", card_hours)):
			with open(os.path.join(out, "card-%s%s.svg" % (name, suffix)), "w", encoding="utf-8") as f:
				f.write(fn(t, name + theme[0], d))
	for name in os.listdir(out):
		if name.startswith("github-contribution-grid-snake") and name.endswith(".svg"):
			round_snake(os.path.join(out, name))
	print("cards written to", out, json.dumps({k: v for k, v in d.items() if k != "days"}))


if __name__ == "__main__":
	main()
