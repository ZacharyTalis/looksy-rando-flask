#!/usr/bin/env python3

import sys
from PIL import Image

def generateForeground(args):
    # If help requested, print help message
    if ((len(args) == 1) or ("help" in args[1])):
        helpMessage = \
    """Format: python3 main.py <icons> [colors] <x,y> <placements>

    Examples:

    Generate a 2x4 foreground image with row order \"blanks -> stars -> hearts -> blanks\".
    python3 main.py star,heart 2,4 0,0-1,1-2,2

    Generate a 3x3 foreground image with hearts placed diagonally. Each row is colored in red, then green, then blue.
    python3 main.py heart looksy-red,looksy-green,looksy-blue 3,3 0,0,1c1-0,1c2,0-1c3

    Paths: All icons should be PNGs and reside within the \"icons\" folder. Each output is saved to the \"output\" folder as \"foreground.png\"."""
        print(helpMessage)
        sys.exit(0)

    # Calculate image size (height or width) based on panel dimension
    def calcImageSize(dimension):
        return (82 * dimension + 104)

    # Constants (same every time)
    iconDir = "icons/"
    outputDir = "static/"
    cellSizePx = 58 # height and width of a cell
    edgeSizePx = 64 # offset from edge of image to first row/column
    gapSizePx  = 82 # cellSizePx + 24px between cells

    # Input values (based on arguments)
    try:
        iconNames = args[0].split(",")
        # Handle optional color argument
        i = 1
        colorNames = []
        if ((not args[i][0].isdigit()) or (args[i][0] == "+") or (len(args[i].split(",")[0].split("-")) == 3)):
            colorNames = args[i].split(",")
            i += 1
        rawDimensions = [int(x) for x in args[i].split(",")]
        dimensions = [calcImageSize(x) for x in rawDimensions]
        placements = [[c.split('c') for c in x.split(",")] for x in args[i+1].split("-")]
    except:
        sys.exit("Arguments missing or not recognized! Refer to \"main.py --help\" for argument format.")
    if (not len(rawDimensions) == 2):
        sys.exit(f"Panel size argument \"{args[i]}\" must contain exactly two values \"x,y\"!")

    # Check if dimensions are valid, else return error
    if (rawDimensions[0] <= 0):
        sys.exit(f"x dimension ({rawDimensions[0]}) must be 1 or greater!")
    if (rawDimensions[1] <= 0):
        sys.exit(f"y dimension ({rawDimensions[1]}) must be 1 or greater!")

    # Check if placements if valid, else return error
    if (len(placements) > rawDimensions[1]):
        sys.exit("Too many rows specified!")
    i = 1
    failedRows = []
    for row in placements:
        if (len(row) > rawDimensions[0]):
            failedRows.append(i)
        i += 1
    if (len(failedRows) > 0):
        if (len(failedRows) == 1):
            sys.exit(f"Row {failedRows[0]} is longer than x dimension specified ({rawDimensions[0]})!")
        else:
            sys.exit(f"Rows {failedRows} are longer than x dimension specified ({rawDimensions[0]})!")

    # Generate icon dictionary
    icons = {}
    for iconName in iconNames:
        try:
            icons[iconName] = Image.open(f"{iconDir}{iconName}.png").convert("RGBA")
        except:
            sys.exit(f"{iconName}.png not found in icons folder!")
        try:
            icons[iconName] = icons[iconName].resize((cellSizePx, cellSizePx))
        except:
            sys.exit("Image resize failed!")

    # Generate color dictionary
    colors = \
        {
        # Colors from Looksy
        "looksy-black": (0, 0, 0),
        "looksy-white": (255, 255, 255), 
        "looksy-lightgray": (204, 204, 204), 

        "looksy-red": (255, 0, 0),
        "looksy-pink": (255, 102, 179),
        "looksy-darkred": (128, 0, 0),

        "looksy-orange": (255, 165, 0),
        "looksy-lightred": (255, 102, 102),
        "looksy-orangered": (255, 64, 0),

        "looksy-yellow": (255, 255, 0),
        "looksy-lightyellow": (255, 255, 128),
        "looksy-gold": (255, 201, 0),

        "looksy-darkgreen": (0, 128, 0),
        "looksy-green": (0, 255, 0),
        "looksy-lightgreen": (176, 255, 176),

        "looksy-blue": (0, 0, 255),
        "looksy-blueviolet": (104, 103, 253),
        "looksy-lightcyan": (128, 255, 255),

        "looksy-purple": (128, 0, 128),
        "looksy-violet": (129, 1, 255),
        "looksy-magenta": (255, 7, 255),
        
        # Others
        "black": (0, 0, 0),
        "grey": (128, 128, 128),
        "white": (255, 255, 255),
        "darkred": (128, 0, 0),
        "red": (255, 0, 0),
        "orange": (255, 165, 0),
        "olive": (128, 128, 0),
        "yellow": (255, 255, 0),
        "darkgreen": (0, 128, 0),
        "green": (0, 255, 0),
        "teal": (0, 128, 128),
        "cyan": (0, 255, 255),
        "darkblue": (0, 0, 128),
        "blue": (0, 0, 255),
        "purple": (128, 0, 128),
        "magenta": (255, 0, 255)
        }

    # Replace 3-digit hexcodes with 6-digit equivalents
    # (we want to keep stored colorNames "canonical")
    tempColorNames = []
    for colorName in colorNames:
        if (len(colorName) == 4 and colorName[0] == '+' and all(x in "0123456789ABCDEFabcdef" for x in colorName[1:])):
            tempColorNames.append(f"+{colorName[1]}{colorName[1]}{colorName[2]}{colorName[2]}{colorName[3]}{colorName[3]}")
        else:
            tempColorNames.append(colorName)
    colorNames = tempColorNames

    # Handle various types of colorNames
    for colorName in colorNames:
        # Using predefined table
        if colorName in colors:
            pass
        # Hexcode
        elif (len(colorName) == 7 and colorName[0] == '+' and all(x in "0123456789ABCDEFabcdef" for x in colorName[1:])):
            colors[colorName] = tuple(int(colorName[r:r+2], 16) for r in range(1, 7, 2))
        # RGB 
        elif (len(colorName.split('-')) == 3):
            try:
                colors[colorName] = list(int(x) for x in colorName.split('-'))
            except:
                sys.exit(f"Syntax error for RGB color with name \"{colorName}\"!")
        # colorName format not recognized
        else:
            sys.exit(f"Syntax error for color with name \"{colorName}\"!")

    # Generate image
    baseImage = Image.new("RGBA", dimensions)
    currentY = edgeSizePx
    for row in placements:
        currentX = edgeSizePx
        for cell in row:
            iconValue = cell[0]
            if (iconValue.isdigit()):
                iconValue = int(iconValue)
                if (iconValue > len(iconNames)):
                    sys.exit(f"Specified icon index \"{iconValue}\" doesn't correspond to any specified icon!")
                # Time to generate and place an icon
                if (iconValue > 0):
                    colorValue = cell[1] if len(cell) > 1 and cell[1] else '0'
                    if(colorValue.isdigit()):
                        colorValue = int(colorValue)
                        if (colorValue > len(colorNames)):
                            sys.exit(f"Specified color index \"{colorValue}\" doesn't correspond to any specified color!")
                        currentIcon = icons[iconNames[iconValue - 1]]
                        # If color tint requested, paste icon with appropriate tint
                        if (colorValue != 0):
                            rgb = (cIcon.point(lambda x: x * cColor // 255) for cIcon, cColor in zip(currentIcon.split(), colors[colorNames[colorValue-1]]))
                            a = currentIcon.split()[-1]
                            baseImage.paste(Image.merge("RGBA", [*rgb, a]), (currentX, currentY))
                        # Otherwise, paste icon normally
                        else:
                            baseImage.paste(currentIcon, (currentX, currentY))
                    else:
                        sys.exit(f"Color index {colorValue} isn't a digit!")
            elif (not len(iconValue) == 0):
                sys.exit(f"Icon index {iconValue} isn't a digit!")
            currentX += gapSizePx
        currentY += gapSizePx
    baseImage.save(f"{outputDir}foreground.png", "PNG")
