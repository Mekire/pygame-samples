import pygame as pg


def cursor_from_image(image,size,hotspot,location=(0,0)):
    """This functions return value is of the form accepted by
    pg.mouse.set_cursor() (passed using the *args syntax). The argument image
    is an already loaded image surface containing your desired cursor; size is
    a single integer corresponding to the width of the cursor (must be a
    multiple of 8); hotspot is a 2-tuple representing the exact point in your
    cursor that will represent the mouse pointer position; location is the
    where your cursor is located on the passed in image."""
    if size%8:
        raise ValueError("Size must be a multiple of 8.")
    colors = {(0,0,0,255):".", (255,255,255,255):"X"}
    cursor_string = []
    for j in range(size):
        this_row = []
        for i in range(size):
            where = (i+location[0],j+location[1])
            pixel = tuple(image.get_at(where))
            this_row.append(colors.get(pixel," "))
        cursor_string.append("".join(this_row))
    xors,ands = pg.cursors.compile(cursor_string)
    size = size,size
    return size,hotspot,xors,ands
