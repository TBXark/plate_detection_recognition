def render_caption(plates, alert_color):
    caption = ''
    disable_notification = True
    for p in plates:
        if caption != '':
            caption += '\n'
        caption += '车牌号: ' + p['no'] + ' | ' + '车牌颜色: ' + p['color']
        if p['color'] == alert_color:
            disable_notification = False
    return caption, disable_notification
