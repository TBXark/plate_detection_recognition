import config
import re


def render_caption(plates, opt: config.AlertOpt):
    caption = ''
    disable_notification = True
    for p in plates:
        if caption != '':
            caption += '\n'
        caption += '车牌号: ' + p['no'] + ' | ' + '车牌颜色: ' + p['color']
        if not disable_notification:
            if opt.color_re is not None:
                if re.match(opt.color_re, p['color']) is not None:
                    disable_notification = False
            if opt.number_re is not None:
                if re.match(opt.number_re, p['no']) is not None:
                    disable_notification = False
    return caption, disable_notification
