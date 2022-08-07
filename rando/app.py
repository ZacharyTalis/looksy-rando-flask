#!/usr/bin/env python3

from flask import Flask, request, send_file, serve

import utils.fg
import utils.rando

app = Flask(__name__)

@app.route("/")
def main():

    # Get URL args
    dimensions = request.args.get("dimensions", "")
    colors = request.args.get("colors", "")
    min = request.args.get("min", type=int)
    max = request.args.get("max", type=int)

    # Tidy up dimensions and colors args
    if (dimensions != ""):
        dimensions = tuple([int(i) for i in request.args.get("dimensions", "").split(",")])
    if (colors != ""):
        colors = request.args.get("colors", "").split(",")
        colors = [color.replace(" ", "+") for color in colors]
    
    # Replace any missing args with default values
    DEFAULT_ARGS = [(4,4), ["white", "black"], 0, -1]
    fgArgs = [dimensions, colors, min, max]
    fgArgs = [(x if x not in ["", None] else DEFAULT_ARGS[i]) for i, x in enumerate([dimensions, colors, min, max])]

    # Generate panel placements, then generate foreground image
    args = utils.rando.genForegroundArgs(*fgArgs).split(" ")
    utils.fg.generateForeground(args)

    return send_file("static/foreground.png", mimetype="image/png")

@app.route("/.well-known/gpc.json")
def wellKnown():
    return send_file("static/gpc.json", mimetype="application/json")

if __name__ == "__main__":
    serve(app)
