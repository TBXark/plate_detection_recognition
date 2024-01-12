import config
import re


def render_caption(plates, opt: config.AlertOpt):
    caption = ''
    disable_notification = True
    for p in plates:
        if caption != '':
            caption += '\n'
        caption += 'No: ' + p['no'] + ' | ' + 'Color: ' + p['color']
    if opt.caption_re is not None:
        if re.match(opt.caption_re, caption) is not None:
            disable_notification = False
    if not disable_notification:
        caption = '⚠️⚠️⚠️ WARNING ⚠️⚠️⚠️\n' + caption
    return caption, disable_notification
