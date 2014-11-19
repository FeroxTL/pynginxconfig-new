#coding: utf8
import copy
import re

from blocks import Block, EmptyBlock, KeyValueOption, Comment


def parse(s, parent_block):
    config = copy.copy(s)
    pos, brackets_level, param_start = 0, 0, 0

    while pos < len(config):
        if config[pos] == '#' and brackets_level == 0:
            re_sharp_comment = re.search('(?P<offset>[\s\n]*)#(?P<comment>.*)$', config, re.M)
            sharp_comment = re_sharp_comment.groupdict()
            parent_block.add_comment(Comment(sharp_comment['offset'], sharp_comment['comment']))
            config = config[re_sharp_comment.end():]
            pos, param_start = 0, 0
            continue

        if config[pos] == ';' and brackets_level == 0:
            re_option = re.search('\s*(?P<param_name>\w+)\s*(?P<param_options>.*?);', config[param_start:], re.S)
            if not re_option:
                raise Exception('Wrong option')

            option = re_option.groupdict()
            parent_block[option['param_name']] = KeyValueOption(re.sub('[ \n]+', ' ', option['param_options']))

            config = config[re_option.end():]
            pos, param_start = 0, 0
            continue

        if config[pos] == '{':
            brackets_level += 1
        elif config[pos] == '}':
            brackets_level -= 1

            if brackets_level == 0 and param_start is not None:
                re_block = re.search(
                    '(?P<param_name>\w+)\s*(?P<param_options>.*)\s*{(\n){0,1}(?P<block>(.|\n)*)}',
                    config[param_start:pos + 1],
                )
                block = re_block.groupdict()

                parent_block[block['param_name']] = Block()
                if block['block']:
                    parse(block['block'], parent_block[block['param_name']])

                config = config[re_block.end():]
                pos, param_start = 0, 0
                continue

        pos += 1

    if brackets_level != 0:
        raise Exception('Not closed bracket')



qwe = EmptyBlock()

parse("""#{ asd #qweqeqwe{}
servername qweqweqweqweqwe;    # comment {lalalal} #1

server {
    listen 
    8080
    tls;
    root /data/up1;

    location / {
        l200;
    }

    #location /qwe{
    #}#123
}#qweqwe""", qwe)

print(qwe.render())


qwe = EmptyBlock()
parse(""" servername wqeqweqwe;
http {
    ##
    # Basic Settings
    ##

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    # server_tokens off;

    # server_names_hash_bucket_size 64;
    # server_name_in_redirect off;

    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    ##
    # Logging Settings
    ##

    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    ##
    # Gzip Settings
    ##

    gzip on;
    gzip_disable "msie6";
}#123123
""", qwe)

print(qwe.render())
