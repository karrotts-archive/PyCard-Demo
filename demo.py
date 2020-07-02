'''
TODO List
    * Scale down numbers to support numbers greater than 100 for stats
    * Set limit on description text and create auto wrapper for description
    * Unit test everything

    * (Optional) change scale to allow for longer card descriptions
    * (Optional) add more image processing options to card
'''

import json
from PIL import Image, ImageFont, ImageDraw

def crop_card(card_image, ratio_width, ratio_height, alignment=None):
    #inputted images need to be formatted to the correct aspect ratio for the image on the card
    #card images must be in 74:75 aspect ratio

    #calculate the amount of crop is needed on the sides to maintain a 74:75 aspect ratio
    max_height, max_width = 0,0
    if card_image.width > card_image.height or card_image.height == card_image.width:
        max_height = (int(card_image.height/ratio_height)*ratio_height)
        max_width = max_height / (ratio_height/ratio_width)
    elif card_image.width < card_image.height:
        max_width = (int(card_image.width/ratio_width)*ratio_width)
        max_height = (ratio_height/ratio_width) * max_width

    crop_sides = (card_image.width - max_width)/2
    crop_top = (card_image.height - max_height)/2
    
    #crop the card to the given option
    if alignment == 'top':
        card_image = card_image.crop((crop_sides, 0, card_image.width-crop_sides, card_image.height-(crop_top*2)))
    elif alignment == 'bottom':
        card_image = card_image.crop((crop_sides, (crop_top*2), card_image.width-crop_sides, card_image.height))
    elif alignment == 'left':
        card_image = card_image.crop((0, crop_top, card_image.width-(crop_sides*2), card_image.height))
    elif alignment == 'right':
        card_image = card_image.crop(((crop_sides*2), crop_top, card_image.width, card_image.height))
    elif alignment == 'top-left':
        card_image = card_image.crop((0, 0, card_image.width-(crop_sides*2), card_image.height-(crop_top*2)))
    elif alignment == 'top-right':
        card_image = card_image.crop(((crop_sides*2), 0, card_image.width, card_image.height-(crop_top*2)))
    elif alignment == 'bottom-left':
        card_image = card_image.crop((0, (crop_top*2), card_image.width-(crop_sides*2), card_image.height))
    elif alignment == 'bottom-right':
        card_image = card_image.crop(((crop_sides*2), (crop_top*2), card_image.width, card_image.height))
    elif alignment == 'center':
        card_image = card_image.crop((crop_sides, crop_top, card_image.width-crop_sides, card_image.height-crop_top))
    else:
        card_image = card_image.crop((crop_sides, crop_top, card_image.width-crop_sides, card_image.height-crop_top))
    
    card_image = card_image.resize((330, 315), Image.ANTIALIAS)
    return card_image

def make_card(card_info):
    #load in the images
    background = Image.open('mt_images/template/background.png')
    card_image = Image.open(card_info["image"]["path"])
    mana_icon = Image.open('mt_images/template/mana.png')
    attack_icon = Image.open('mt_images/template/attack.png')
    health_icon = Image.open('mt_images/template/health.png')

    #set the card cover
    card_cover = Image.open('mt_images/template/white.png')
    if card_info["color"] == "red":
        card_cover = Image.open('mt_images/template/red.png')
    elif card_info["color"] == "blue":
        card_cover = Image.open('mt_images/template/blue.png')
    elif card_info["color"] == "green":
        card_cover = Image.open('mt_images/template/green.png')

    #create a new image with alpha layers
    card = Image.new('RGBA', (background.width, background.height))

    #paste the background layer
    card.paste(background, (0,0))

    #crop the card and paste it to the new image
    card_image = crop_card(card_image, 74, 75, card_info["image"]["alignment"]).convert("RGBA")
    card.paste(card_image, (29+card_info["image"]["x-offset"], 30+card_info["image"]["y-offset"]), card_image)

    #paste the overlay for the card
    card.paste(card_cover, (0,0), card_cover)

    #set fonts
    stat_font = ImageFont.truetype('./fonts/Roboto-Regular.ttf', 60)
    text_font = ImageFont.truetype('./fonts/Roboto-Regular.ttf', 30)
    text_font_bold = ImageFont.truetype('./fonts/Roboto-Bold.ttf', 30)

    # get a drawing context
    draw = ImageDraw.Draw(card)

    # draw stats
    if card_info["mana"]["visible"]:
        card.paste(mana_icon, (0,0), mana_icon)
        w, h = draw.textsize(str(card_info["mana"]["value"]), font=stat_font)
        draw.text(((82-w)/2,(81-h)/4), str(card_info["mana"]["value"]), font=stat_font, fill=(255,255,255,255))
    if card_info["health"]["visible"]:
        card.paste(health_icon, (0,0), health_icon)
        w, h = draw.textsize(str(card_info["health"]["value"]), font=stat_font)
        draw.text((((82-w)/2)+304,((81-h)/4)+583), str(card_info["health"]["value"]), font=stat_font, fill=(255,255,255,255))
    if card_info["attack"]["visible"]:
        card.paste(attack_icon, (0,0), attack_icon)
        w, h = draw.textsize(str(card_info["attack"]["value"]), font=stat_font)
        draw.text(((82-w)/2,((81-h)/4)+583), str(card_info["attack"]["value"]), font=stat_font, fill=(255,255,255,255))

    # center and draw name
    w, h = draw.textsize(str(card_info["name"]), font=text_font_bold)
    center = (card.width-w)/2
    draw.text((center,350), str(card_info["name"]), font=text_font_bold, fill=(255,255,255,255))


    # create a list of all the description options
    description_items = []
    for i in range(len(card_info["effects"])):
        description_items.append([card_info["effects"][i]["name"]+ ': ', card_info["effects"][i]["description"].replace('[X]', str(card_info["effects"][i]["modifier"]), 2)])

    # draw each card effect
    # steps:
    # 1 add up the widths of name and description
    for i in range(len(description_items)):
        name_width, name_height = draw.textsize(description_items[0][0], font=text_font_bold)
        description_width, description_height = draw.textsize(description_items[0][1], font=text_font)
        while():
            total_width = name_width + description_width
            # 2 check if width exceeds a certain threshold
            if total_width > 330:
            # 3 break off the last word and move it to a new line
                words = description_items[0][1].split()
                description_items[0][]
                description_items.insert(1, words[len(words)-1])
            else:
                break

    # 4 repeat until the description fits on one line or no more words available.
    # 5 draw text on card

    '''
    effect_list = card_info["effects"]
    for i in range(len(effect_list)):
        effect_name = effect_list[i]["name"] + ': '
        effect_description = effect_list[i]["description"].replace('[X]', str(effect_list[i]["modifier"]), 2)
        name_width, name_height = draw.textsize(effect_name, font=text_font_bold)
        description_width, description_height = draw.textsize(effect_description, font=text_font)
        
        center = (card.width-(name_width+description_width))/2
        draw.text((center,419+(i*35)), effect_name, font=text_font_bold, fill=(0,0,0,255))
        draw.text((center+name_width,419+(i*35)), effect_description, font=text_font, fill=(0,0,0,255))
    '''

    card.save('mt_images/cards/test.png')

card = {
            "color":"blue",
            "name":"Dragon McDragonface",
            "type": "spell",
            "mana": {
                "visible": True,
                "value": 5
            },
            "health": {
                "visible": True,
                "value": 10
            },
            "attack": {
                "visible": True,
                "value": 5
            },
            "image": {
                "path": "mt_images/template/beast.jpg",
                "alignment":"top-left",
                "x-offset": 0,
                "y-offset": 0
            },
            "effects": [
                {
                    "name": "Explode",
                    "description": "Deal [X] damage.",
                    "modifier": 1
                }
            ]
        }

make_card(card)