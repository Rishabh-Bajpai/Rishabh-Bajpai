import sys

path = sys.argv[1] if len(sys.argv) > 1 else "profile-3d-contrib/profile-night-rainbow.svg"
with open(path) as f:
    svg = f.read()

svg = svg.replace('x="650" y="830" text-anchor="start" class="fill-fg">5<title>5</title>',
                   'x="650" y="830" text-anchor="start" class="fill-fg">272<title>272</title>')
svg = svg.replace('x="772" y="830" text-anchor="start" class="fill-fg">4<title>4</title>',
                   'x="772" y="830" text-anchor="start" class="fill-fg">31<title>31</title>')

with open(path, "w") as f:
    f.write(svg)
