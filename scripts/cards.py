#!/usr/bin/env python3
"""Render the profile stats cards as SVG from the GitHub API.

Three cards, each in a dark and a light variant:
  activity  - contributions over the last year, gradient area chart
  totals    - the headline numbers with a weekly sparkline
  hours     - commits by local hour of day, gradient bars

Usage: GH_TOKEN=... cards.py <user> <out_dir>
"""

import datetime as dt
import json
import math
import os
import sys
import urllib.request

API = "https://api.github.com"

# one palette per theme; the accent gradients are shared so the cards read as a set
THEMES = {
	"dark": {
		"bg": "#0b0d11", "bg2": "#0e1117", "border": "rgba(255,255,255,.09)",
		"text": "#f2f4f7", "muted": "#8b93a1", "faint": "#4a5160",
		"dot": "#ffffff", "dot_op": ".10", "grid": "rgba(255,255,255,.07)",
		"glow": "#6d4cff", "glow_op": ".22", "bar_dim": "#1f3d2a", "track": "rgba(255,255,255,.05)",
	},
	"light": {
		"bg": "#ffffff", "bg2": "#fbfcfd", "border": "#d0d7de",
		"text": "#1f2328", "muted": "#59636e", "faint": "#a8b0ba",
		"dot": "#1f2328", "dot_op": ".08", "grid": "rgba(31,35,40,.08)",
		"glow": "#6d4cff", "glow_op": ".10", "bar_dim": "#cfe9d8", "track": "rgba(31,35,40,.05)",
	},
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', Menlo, Consolas, monospace"


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
    createdAt
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
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
		"years": (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))).days // 365,
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


def shell(t, w, h, key):
	"""Card background: rounded plate, halftone dots that fade in toward the bottom, a dim glow."""
	return """<defs>
	<clipPath id="clip-%(k)s"><rect width="%(w)d" height="%(h)d" rx="18"/></clipPath>
	<pattern id="dots-%(k)s" width="9" height="9" patternUnits="userSpaceOnUse"><circle cx="4.5" cy="4.5" r="1" fill="%(dot)s"/></pattern>
	<linearGradient id="fade-%(k)s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="1"/></linearGradient>
	<mask id="mask-%(k)s"><rect width="%(w)d" height="%(h)d" fill="url(#fade-%(k)s)"/></mask>
	<radialGradient id="glow-%(k)s" cx=".5" cy="1.15" r=".75"><stop offset="0" stop-color="%(glow)s" stop-opacity="%(glow_op)s"/><stop offset="1" stop-color="%(glow)s" stop-opacity="0"/></radialGradient>
	<linearGradient id="line-%(k)s" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#3b82f6"/><stop offset=".55" stop-color="#22c55e"/><stop offset="1" stop-color="#a3e635"/></linearGradient>
	<linearGradient id="area-%(k)s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4ade80" stop-opacity=".45"/><stop offset="1" stop-color="#4ade80" stop-opacity="0"/></linearGradient>
	<linearGradient id="bar-%(k)s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#86efac"/><stop offset=".45" stop-color="#22c55e"/><stop offset="1" stop-color="#15803d" stop-opacity=".55"/></linearGradient>
	<filter id="soft-%(k)s" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<g clip-path="url(#clip-%(k)s)">
	<rect width="%(w)d" height="%(h)d" fill="%(bg)s"/>
	<rect width="%(w)d" height="%(h)d" fill="url(#dots-%(k)s)" opacity="%(dot_op)s" mask="url(#mask-%(k)s)"/>
	<rect width="%(w)d" height="%(h)d" fill="url(#glow-%(k)s)"/>
</g>
<rect x=".5" y=".5" width="%(w)d" height="%(h)d" rx="18" fill="none" stroke="%(border)s"/>
""" % dict(t, k=key, w=w - 1, h=h - 1)


def title(t, x, y, text, sub=None):
	out = '<text x="%d" y="%d" font-family="%s" font-size="19" font-weight="700" fill="%s">%s</text>' % (x, y, SANS, t["text"], text)
	if sub:
		out += '<text x="%d" y="%d" font-family="%s" font-size="12" fill="%s">%s</text>' % (x, y + 20, SANS, t["muted"], sub)
	return out


def card_activity(t, key, d):
	w, h = 880, 260
	days = d["days"]
	counts = [x["contributionCount"] for x in days]
	# a three week mean, sampled every few days, turns the spiky daily series into the shape of the year
	series = smooth(counts, 21)[::4]
	left, right, top, bottom = 40, 40, 78, 214
	peak = max(series) or 1
	n = len(series)
	pts = [(left + i * (w - left - right) / (n - 1), bottom - v / peak * (bottom - top)) for i, v in enumerate(series)]

	s = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="Contributions in the last year">' % (w, h, w, h)
	s += shell(t, w, h, key)
	s += title(t, left, 40, "Activity", "contributions in the last year, all repositories")

	# headline number, monospace like a readout
	s += '<text x="%d" y="46" text-anchor="end" font-family="%s" font-size="30" font-weight="700" fill="%s">%s</text>' % (w - right, MONO, t["text"], fmt(d["total"]))

	# dotted grid, one line per quarter of the peak
	for i in range(1, 4):
		y = bottom - i * (bottom - top) / 4
		s += '<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-dasharray="2 4"/>' % (left, y, w - right, y, t["grid"])

	path = curve(pts)
	s += '<path d="%s L%.1f,%d L%d,%d Z" fill="url(#area-%s)"/>' % (path, pts[-1][0], bottom, left, bottom, key)
	s += '<path d="%s" fill="none" stroke="url(#line-%s)" stroke-width="2.5" stroke-linejoin="round" opacity=".35" filter="url(#soft-%s)"/>' % (path, key, key)
	s += '<path d="%s" fill="none" stroke="url(#line-%s)" stroke-width="2.5" stroke-linejoin="round"/>' % (path, key)

	# the peak day, called out
	pi = max(range(n), key=lambda i: series[i])
	px, py = pts[pi]
	peak_day = max(days, key=lambda x: x["contributionCount"])
	py -= 2
	s += '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%d" stroke="%s" stroke-dasharray="2 3"/>' % (px, py, px, bottom, t["faint"])
	s += '<circle cx="%.1f" cy="%.1f" r="4" fill="%s" stroke="#a3e635" stroke-width="2"/>' % (px, py, t["bg"])
	label = "%d on %s" % (peak_day["contributionCount"], dt.date.fromisoformat(peak_day["date"]).strftime("%-d %b"))
	anchor = "end" if px > w / 2 else "start"
	lx = px - 10 if anchor == "end" else px + 10
	s += '<text x="%.1f" y="%.1f" text-anchor="%s" font-family="%s" font-size="12" fill="%s">%s</text>' % (lx, py - 8, anchor, MONO, t["muted"], label)

	# month ticks along the bottom
	last = ""
	for i, x in enumerate(days):
		m = dt.date.fromisoformat(x["date"]).strftime("%b")
		if m != last and i > 6:
			tx = left + i * (w - left - right) / (len(days) - 1)
			s += '<text x="%.1f" y="%d" font-family="%s" font-size="11" fill="%s">%s</text>' % (tx, bottom + 22, MONO, t["faint"], m)
		last = m
	s += "</svg>"
	return s


def card_totals(t, key, d):
	w, h = 432, 250
	s = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="Totals">' % (w, h, w, h)
	s += shell(t, w, h, key)
	s += title(t, 32, 40, "Totals", "last year, public and private")

	cells = [
		("Commits", d["commits"]), ("Pull requests", d["prs"]), ("Issues", d["issues"]),
		("Repos touched", d["repos_contrib"]), ("Stars", d["stars"]), ("Followers", d["followers"]),
	]
	for i, (name, val) in enumerate(cells):
		x = 32 + (i % 3) * 128
		y = 112 + (i // 3) * 66
		s += '<text x="%d" y="%d" font-family="%s" font-size="24" font-weight="700" fill="%s">%s</text>' % (x, y, MONO, t["text"], fmt(val))
		s += '<text x="%d" y="%d" font-family="%s" font-size="11" fill="%s">%s</text>' % (x, y + 18, SANS, t["muted"], name)

	# weekly sparkline along the foot of the card
	weeks = [sum(x["contributionCount"] for x in d["days"][i:i + 7]) for i in range(0, len(d["days"]), 7)]
	peak = max(weeks) or 1
	left, right, top, bottom = 32, 32, 208, 232
	n = len(weeks)
	pts = [(left + i * (w - left - right) / (n - 1), bottom - v / peak * (bottom - top)) for i, v in enumerate(weeks)]
	path = curve(pts)
	s += '<path d="%s L%.1f,%d L%d,%d Z" fill="url(#area-%s)"/>' % (path, pts[-1][0], bottom, left, bottom, key)
	s += '<path d="%s" fill="none" stroke="url(#line-%s)" stroke-width="2" stroke-linejoin="round"/>' % (path, key)
	s += "</svg>"
	return s


def card_hours(t, key, d):
	w, h = 432, 250
	s = '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" role="img" aria-label="Commits by hour">' % (w, h, w, h)
	s += shell(t, w, h, key)
	s += title(t, 32, 40, "Commits by hour", "local time of the last %s commits" % fmt(d["hours_n"]))

	hours = d["hours"]
	peak = max(hours) or 1
	left, right, top, bottom = 32, 32, 88, 200
	slot = (w - left - right) / 24
	bw = slot - 5
	best = hours.index(peak)
	for i, v in enumerate(hours):
		x = left + i * slot + 2.5
		bh = max(3, v / peak * (bottom - top))
		y = bottom - bh
		s += '<rect x="%.1f" y="%d" width="%.1f" height="%d" rx="3" fill="%s"/>' % (x, top, bw, bottom - top, t["track"])
		if i == best:
			s += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="#4ade80" opacity=".6" filter="url(#soft-%s)"/>' % (x, y, bw, bh, key)
		s += '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="url(#bar-%s)"/>' % (x, y, bw, bh, key)

	# the busiest hour, called out above its bar
	bx = left + best * slot + slot / 2
	by = bottom - peak / peak * (bottom - top)
	s += '<text x="%.1f" y="%.1f" text-anchor="middle" font-family="%s" font-size="11" fill="%s">%02d:00</text>' % (bx, by - 8, MONO, t["muted"], best)

	for hr in (0, 6, 12, 18, 23):
		s += '<text x="%.1f" y="%d" text-anchor="middle" font-family="%s" font-size="11" fill="%s">%d</text>' % (left + hr * slot + slot / 2, bottom + 20, MONO, t["faint"], hr)
	s += "</svg>"
	return s


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
	print("cards written to", out, json.dumps({k: v for k, v in d.items() if k != "days"}))


if __name__ == "__main__":
	main()
