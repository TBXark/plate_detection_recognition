import config
import re


def render_caption(plates, opt: config.AlertOpt):
    caption = ''
    disable_notification = True
    for p in plates:
        if caption != '':
            caption += '\n'
        caption += '车牌号: ' + p['no'] + ' | ' + '车牌颜色: ' + p['color']
    if opt.caption_re is not None:
        if re.match(opt.caption_re, caption) is not None:
            disable_notification = False
    return caption, disable_notification
