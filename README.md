# looksy-flask-rando

A Flask app that generates random stone panels for [Looksy](https://prodzpod.github.io/witness/editor.html) as foreground images.

Contains a local copy of [looksy-foreground-gen](https://github.com/ZacharyTalis/looksy-foreground-gen/).

## URL Arguments

All arguments are optional.

| Argument    | Default Value | Behavior                   |
| ----------- | ------------- | -------------------------- |
| ?dimensions | 4,4           | x-by-y panel dimensions    |
| ?colors     | white,black   | Stone colors               |
| ?min        | 0             | Minimum stones per region  |
| ?max        | -1            | Maxiumum stones per region |

### Example

To generate a 5-cell-wide and 6-cell-tall panel; with red, blue, and yellow stones; with a minimum of 2 stones per region; with a maximum of 5 stones per region:

```
[url]?dimensions=5,6&colors=red,blue,yellow&min=2&max=5
```

Of note, regions of a size less than the specified `minimum` contain as many stones as possible.

## Execution Overview
1. Take URL arguments via Flask
2. Generate valid panel (foreground image)
3. Host image with Flask
4. Out-of-repo, serve image with nginx
