# -*- coding: utf-8 -*-

import re
from xml.sax.saxutils import escape, unescape

from ...utils.usercolor import UserColor
from ...utils.timeformat import TimeFormat
from ...utils.truncatehtml import truncate_html
from ...theme import Theme
from ..base.entry import AddedHtmlMarkup

user_color = UserColor()


class TumblrEntry(object):

    def __init__(self, entry):
        self.entry = entry
        self.theme = Theme()

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        return self._get_entry_dict(entry, body)

    def _get_body(self, entry):
        link = "<a href='%s' title='%s'>......</a>" % (
            entry['post_url'], _('Read more'))
        body = entry.get('text') or entry.get('body') or entry.get('caption') or ''
        body = truncate_html(body, 140, link)

        if entry.get('type') == 'quote':
            body = u'“%s”' % body

        if entry.get('source'):
            source = truncate_html(entry.get('source'), 80)
            body +=  "<div class='source'>%s</div>" % source

        return body

    def _get_entry_dict(self, entry, body):
        image_uri = 'http://api.tumblr.com/v2/blog/%s.tumblr.com/avatar/40' \
            % entry.get('blog_name')

        # command

        rebloglink = 'http://www.tumblr.com/reblog/%s/%s' % (
            entry['id'], entry['reblog_key'])

        path = '//%s/%s' % (entry['id'], entry['reblog_key'])
        likelink = 'gfeedlinefblike:%s' % path
        unlikelink = 'gfeedlinefbunlike:%s' % path
        is_liked = entry.get('liked') # FIXME

        reblog_icon = "<i class='icon-retweet'></i>"
        like_icon = "<i class='icon-heart'></i>"

        command = (
            u"<span class='commands'>"
            "<a title='%s' href='%s' >%s</a> &nbsp;"
            "<a title='%s' class='like-first %s'  href='%s' onclick='like(this);'>%s</a>"
            "<a title='%s' class='like-second %s' href='%s' onclick='like(this);'>%s</a>"
            "</span>"
            ) % (
            _('Reblog'), rebloglink, reblog_icon,
            _('Like'), 'hidden' if is_liked else '', likelink,   like_icon,
            _('Like'), '' if is_liked else 'hidden', unlikelink, like_icon, 
            )

        # popup

        for key in ['text', 'body', 'question', 'url', 'caption']:
            popup_body = entry.get(key)
            if popup_body:
                popup_body = re.sub(r'<[^>]*?>', '', popup_body).rstrip()
                break
        else:
            post_type = {'photo': _('a photo'), 'video': _('a video'), 
                         'audio': _('an audio')}
            popup_body = _('{0} posts {1} entry.').format(
                entry['blog_name'], _(post_type.get(entry['type'])))

        # print entry['type'], popup_body
        url = entry['post_url'].split('/')

        entry_dict = dict(
            date_time=TimeFormat(entry['date']).get_local_time(),
            id=entry['id'],
            styles='tumblr',
            image_uri=image_uri,
            permalink=entry['post_url'],
            userlink="%s://%s" % (url[0], url[2]),

            command='',
            onmouseover='',

            retweet='',
            retweet_by_screen_name='',
            retweet_by_name='',

            pre_username='',
            post_username='',
            event='',

            in_reply_to='',

            user_name=entry['blog_name'],
            user_name2='',
            full_name=entry['blog_name'],
            user_color=user_color.get(entry['blog_name']),
            user_description='',
            protected="<div class='tumblrbuttons'>%s</div>" % command,
            source='',

            status_body=add_markup.convert(body),
            popup_body=popup_body,
            target='',
            child=''
            )

        return entry_dict

class TumblrTextEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        title = entry.get('title')
        if title:
            body = '<p><b>%s</b></p>%s' % (title, body)

        return self._get_entry_dict(entry, body)

class TumblrPhotosEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        new_body = "<div class='image'>"
        # template = self.theme.template['image']

        for photo in entry['photos']:
            small =  photo['alt_sizes'][2]['url']
            link =  photo['alt_sizes'][0]['url'].replace('http', 'gfeedlineimg', 1)

            # key_dict = {'url': url}
            # new_body += template.substitute(key_dict)
            new_body += "<a href='%s'><img height='90' src='%s'></a>" % (
                link, small)

        new_body += "</div>" + body

        return self._get_entry_dict(entry, new_body)

class TumblrLinkEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        url = entry.get('url')
        title = entry.get('title') or url
        link = "<p><a href='%s'>%s</a><p>" % (url, title)
        body = link + body

        return self._get_entry_dict(entry, body)

class TumblrChatEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        entry['body'] = entry['body'].replace('\r', '').replace('\n', '<br>')
        body = self._get_body(self.entry)

        title = self.entry.get('title')
        if title:
            body = '<p><b>%s</b></p>%s' % (title, body)

        return self._get_entry_dict(self.entry, body)

class TumblrAudioEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = ""

        artist = entry.get('artist')
        track_name = entry.get('track_name')
        album = entry.get('album')
        image = entry.get('album_art')

        if artist:
            body = ("<p>%s</p>" % artist) + body
        if track_name:
            body = ("<p>%s</p>" % track_name) + body
        if album:
            body = ("<p>%s</p>" % album) + body

        if image:
            template = self.theme.template['image']
            key_dict = {'url': image, 'link': entry.get('post_url')}

            body += template.substitute(key_dict)

        body += self._get_body(entry)
        return self._get_entry_dict(entry, body)

class TumblrVideoEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        body = self._get_body(entry)

        template = self.theme.template['image']
        key_dict = {'url': entry.get('thumbnail_url'), 
                    'link': entry.get('post_url')}
        body = template.substitute(key_dict) + body
        return self._get_entry_dict(entry, body)

class TumblrAnswerEntry(TumblrEntry):

    def get_dict(self, api):
        entry = self.entry
        name = entry.get('asking_name')
        url = entry.get('asking_url')

        image = 'http://api.tumblr.com/v2/blog/%savatar/40' % \
            url.replace('http://', '') if url else \
            'http://www.tumblr.com/images/anonymous_avatar_40.gif'

        template = self.theme.template['bubble']
        key_dict = {'image_uri': image,
                    'permalink': url,
                    'text': entry.get('question'),
                    }
        body = template.substitute(key_dict)
        body += entry.get('answer')

        return self._get_entry_dict(entry, body)

class AddedTumblrHtmlMarkup(AddedHtmlMarkup):

    def __init__(self):
        super(AddedTumblrHtmlMarkup, self).__init__()

        num = 5
        self.new_lines = re.compile('^(([^\n]*\n){%d})(.*)' % num, re.DOTALL)
        self.remove_continuous_tags = re.compile(r'(<.*?>)\1+')

    def convert(self, text):
        text = text.replace('target="_blank"', "")
        # text = super(AddedTumblrHtmlMarkup, self).convert(text)
        # text = text.replace('"', '&quot;')
        text = text.replace('"', "'")
        text = text.replace('\r', '')
        text = text.replace('\n', '')
        text = self.remove_continuous_tags.sub('\\1\\1', text)

        return text

add_markup = AddedTumblrHtmlMarkup()
