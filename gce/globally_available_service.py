# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import yaml

SELF_LINK = '$(ref.{}.selfLink)'
PROP = '$(ref.{}.{})'


def gen_instance_template(name, instance_template):
    return {
        'name': name + '-instance-template',
        'type': 'compute.v1.instanceTemplate',
        'properties': {'properties': instance_template}
    }


def gen_health_check(name, health_check_template, port, ssl=False):
    return {
        'name': name + '-health-check',
        'type': 'compute.v1.{}'.format(
            'httpsHealthCheck' if ssl else 'httpHealthCheck'
        ),
        'properties': dict(
            port=port,
            **health_check_template
        )
    }


def gen_target_proxy(name, url_map, cert=None):
    properties = {
        'urlMap': SELF_LINK.format(url_map['name']),
        'description': (
            'proxies from the fowarding rule'
            'to the instance group manager'
        )
    }
    if cert:
        properties['sslCertificates'] = [SELF_LINK.format(cert['name'])]
        return {
            'name': name + '-target-proxy-ssl',
            'type': 'compute.v1.targetHttpsProxy',
            'properties': properties
        }
    else:
        return {
            'name': name + '-target-proxy',
            'type': 'compute.v1.targetHttpProxy',
            'properties': properties
        }


def gen_firewall_rule(name, port):
    return {
        'name': name + '-firewall-rule',
        'type': 'compute.v1.firewall',
        'properties': {
            'allowed': [{'IPProtocol': 'tcp', 'ports': [port]}],
            'sourceRanges': '0.0.0.0/0'
        }
    }


def gen_target_pool(name, region, health_checks):
    return {
        'name': name + '-target-pool-' + region,
        'type': 'compute.v1.targetPool',
        'properties': {
            'region': region,
            'healthChecks': [
                SELF_LINK.format(health_check['name'])
                for health_check in health_checks
            ],
            'instances': [],
            'description': (
                'A target pool to provide health checks'
                'to individual instances serving APIs'
                'Does not serve any forwarding rules'
                'Instances are auto added by IGMs'
            ),
            'sessionAffinity': 'NONE'
        }
    }


def gen_global_forwarding_rule(name, target_proxy, port, ip_address=None):
    forwarding_rule = {
        'name': name + '-fowarding-rule-' + target_proxy['name'],
        'type': 'compute.v1.globalForwardingRule',
        'properties': {
            'target': SELF_LINK.format(target_proxy['name']),
            'portRange': port,
            'IPProtocol': 'TCP',
        }
    }
    if ip_address:
        forwarding_rule['properties']['IPAddress'] = ip_address
    return forwarding_rule


def gen_url_map(name, backend_service, dns_name=''):
    service_link = SELF_LINK.format(backend_service['name'])
    return {
        'name': name + '-url-map',
        'type': 'compute.v1.urlMap',
        'properties': {
            'defaultService': service_link,
            'hostRules': [{
                'description': (
                    'Route all traffic from the appropriate'
                    'DNS address to your backend'
                ),
                'hosts': ['*.' + dns_name],
                'pathMatcher': 'all'
            }],
            'pathMatchers': [{
                'description': 'all paths',
                'name': 'all',
                'defaultService': service_link,
                'pathRules': [{
                    'paths': ['/*'],
                    'service': service_link
                }]
            }]
        }
    }


def gen_backend_service(name,
                        backend_template,
                        igms,
                        health_check=None,
                        https=False):
    backends = [
        dict(
            group=PROP.format(igm['name'], 'instanceGroup'),
            **backend_template
        ) for igm in igms
    ]
    backend_service = {
        'name': name + '-backend-service',
        'type': 'compute.v1.backendService',
        'properties': {
            'backends': backends,
            'portName': 'api-port',
            'protocol': 'HTTPS' if https else 'HTTP',
        }
    }
    if health_check:
        backend_service['properties']['healthChecks'] = [
            SELF_LINK.format(health_check['name']),
        ]
    return backend_service


def gen_instance_group_manager(name,
                               zone,
                               instance_template,
                               target_pool=None):
    return {
        'name': name + '-igm-' + zone,
        'type': 'compute.v1.instanceGroupManager',
        'properties': {
            'baseInstanceName': instance_template['name'],
            'instanceTemplate': SELF_LINK.format(instance_template['name']),
            'targetSize': 1,
            'zone': zone,
            'targetPools': [
                SELF_LINK.format(target_pool['name'])
            ] if target_pool else []
        }
    }


def gen_autoscaler(name, autoscaler_template, instance_group_manager):
    return {
        'name': name + instance_group_manager['name'] + '-autoscaler',
        'type': 'compute.v1.autoscaler',
        'properties': dict(
            zone=instance_group_manager['properties']['zone'],
            target=SELF_LINK.format(instance_group_manager['name']),
            **autoscaler_template
        )
    }


def GenerateConfig(context):
    name = context.env['deployment']
    resources = []

    instance_template = gen_instance_template(
        name,
        context.properties['instance_template']
    )
    resources.append(instance_template)

    cert = context.properties.get('ssl_certificate')
    port = context.properties.get('port', 443 if cert else 8080)

    health_check_template = context.properties.get('health_check')

    # Only need target pools if the user wants a health check

    health_check = None
    target_pool = None
    if health_check_template:
        health_check = gen_health_check(
            name, health_check_template, port, ssl=cert)
        resources.append(health_check)

        regions = {
            zone: zone.rsplit('-', 1)[0]
            for zone in context.properties['zones']
        }
        target_pools = dict()
        for region in set(regions.values()):
            target_pool = gen_target_pool(name, region, [health_check])
            target_pools[region] = target_pool
            resources.append(target_pool)

    # Create a managed instance group in each zone
    igms = []
    for zone in context.properties['zones']:
        igm = gen_instance_group_manager(
            name,
            zone,
            instance_template,
            target_pool=target_pools[regions[zone]]
        )
        igms.append(igm)
        resources.append(igm)

    # Optionally autoscale those managed instance groups
    autoscaler_template = context.properties.get('autoscaler')
    if autoscaler_template:
        for igm in igms:
            autoscaler = gen_autoscaler(name, autoscaler_template, igm)
            resources.append(autoscaler)

    # A backend service that load balances across all the IGMs
    backend_service = gen_backend_service(
        name,
        context.properties['backend_service_template'],
        igms,
        health_check=health_check,
        https=cert
    )
    resources.append(backend_service)

    # A trivial URL Map that only maps to the single backend service
    url_map = gen_url_map(
        name, backend_service, dns_name=context.properties.get('dns_name', ''))
    resources.append(url_map)

    # A target proxy that connects the fowarding rule and the urlmap
    target_proxy = gen_target_proxy(name, url_map, cert=cert)
    resources.append(target_proxy)

    # A forwarding rule that uses the provided static IP
    forwarding_rule = gen_global_forwarding_rule(
        name,
        target_proxy,
        port,
        ip_address=context.properties.get('ip_address')
    )
    resources.append(forwarding_rule)

    return yaml.dump({'resources': resources})
