# -*- coding: utf-8 -*-
import yaml
import json
import requests
import dateutil.parser
import dateutil.tz
import argparse
import os.path
from datetime import datetime

EPOCH = datetime(1970, 1, 1)


def print_list(list_):
    for item in list_:
        string = u'%d %s' % (item['id'], item['name'])
        if item.get('values'):
            value = item['values'][-1]['value']
            string += '\t%s' % value
        print string


def epoch_seconds(t):
    return (t - EPOCH).total_seconds()


def load_config():
    with open(os.path.expanduser('~/.redwood.yaml')) as f:
        config = yaml.load(f)
    if 'base_url' not in config:
        config['base_url'] = 'http://api.redwoodtracker.com/'
    return config


def make_auth(config):
    if 'token' in config:
        return config['token'], ''
    return config['username'], config['password']


def get_lists(args, config):
    res = requests.get(config['base_url'] + '/api/list', auth=make_auth(config))
    print_list(res.json()['data'])


def post_list(args, config):
    data = dict(name=args.name)
    body = json.dumps(data)
    url = config['base_url'] + '/api/list'
    res = requests.post(url, auth=make_auth(config), data=body, headers={'content-type': 'application/json'})
    if 200 <= res.status_code < 300:
        print_list([res.json()])
    else:
        print res


def get_list_data(args, config):
    res = requests.get(config['base_url'] + '/api/list/%s/data' % (args.list_id, ), 
        auth=make_auth(config),
    )
    data = res.json()
    print data['name']
    print_list(data['metrics'])


def post_metric_id_data(args, config):
    pairs = [(int(metric), float(value)) 
             for metric, value in zip(args.args[::2], args.args[1::2])]
    if args.datetime is not None:
        dt = dateutil.parser.parse(args.datetime)
        if dt.tzinfo is None:
            dt = dt.replace(
                tzinfo=dateutil.tz.tzlocal()).astimezone(
                dateutil.tz.tzutc()).replace(
                tzinfo=None
            )
    else:
        dt = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = epoch_seconds(dt)
    for metric, value in pairs:
        body = json.dumps(dict(
            value=value,
            timestamp=timestamp))
        url = config['base_url'] + '/api/metric/%s/data' % (metric, )
        res = requests.post(url, auth=make_auth(config), data=body, headers={'content-type': 'application/json'})
        if res.status_code != 200:
            import ipdb;ipdb.set_trace()
            print res


def post_metric(args, config):
    data = dict(name=args.name, list_id=args.list_id, type=3)
    body = json.dumps(data)
    url = config['base_url'] + '/api/metric'
    res = requests.post(url, auth=make_auth(config), data=body, headers={'content-type': 'application/json'})
    if 200 <= res.status_code < 300:
        print_list([res.json()])
    else:
        print res


def main():
    config = load_config()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    lists_parser = subparsers.add_parser('lists')
    lists_parser.set_defaults(func=get_lists)

    list_parser = subparsers.add_parser('list')
    list_parser.add_argument('list_id')
    list_parser.set_defaults(func=get_list_data)

    list_parser = subparsers.add_parser('record')
    list_parser.add_argument('-d', '--datetime', default=None, nargs='?')
    list_parser.add_argument('args', nargs='+', help='Args should be alternating '
        'pairs of metric_id value. e.g. record 4 150 5 1 6 0 '
        'to record 150 for metric 4, 1 for 5, and 0 for 6')
    list_parser.set_defaults(func=post_metric_id_data)

    list_parser = subparsers.add_parser('new_metric')
    list_parser.add_argument('list_id')
    list_parser.add_argument('name')
    list_parser.set_defaults(func=post_metric)

    list_parser = subparsers.add_parser('new_list')
    list_parser.add_argument('name')
    list_parser.set_defaults(func=post_list)

    args = parser.parse_args()
    args.func(args, config)
